from collections.abc import AsyncIterator
from unittest.mock import ANY, Mock

import pytest

from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.hand_pose import (
    HandObservation,
    HandPoseResult,
    Handedness,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.domain.pointing import (
    HandLandmarks,
    ImagePoint,
    NormalizedPoint,
    PointingOverlay,
    PointingOverlayState,
    PointingRay,
)
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages
from vision_caption.core.services.pointing.gesture_recognizer import (
    PointingActivation,
    PointingRecognitionResult,
)
from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)
from vision_caption.core.services.pointing.pointing_pipeline import (
    REPOINT_PROMPT,
    PointingPipeline,
    compose_accessibility_caption,
)


class FakeEstimator:
    def __init__(self) -> None:
        self.calls = 0
        self.closed = False

    async def estimate(self, frame: Frame) -> HandPoseResult:
        self.calls += 1
        return HandPoseResult(frame_id=frame.frame_id)

    async def close(self) -> None:
        self.closed = True


class StubRecognizer:
    def __init__(
        self,
        activations: tuple[PointingActivation, ...],
        overlays: tuple[PointingOverlay, ...] = (),
    ) -> None:
        self.activations = activations
        self.overlays = overlays
        self.calls = 0
        self.reset_calls = 0
        self.cancelled: list[PointingActivation] = []

    def update(self, hands, *, timestamp):
        self.calls += 1
        return PointingRecognitionResult(
            activations=self.activations if self.calls == 1 else (),
            overlays=self.overlays,
        )

    def cancel(self, activation: PointingActivation) -> None:
        self.cancelled.append(activation)

    def reset(self) -> None:
        self.reset_calls += 1


class FakePreparer:
    def __init__(self) -> None:
        self.calls = 0

    async def prepare(self, frame, event) -> PointingImages:
        self.calls += 1
        return PointingImages(b"context", b"focus", b"clean")


class FakeGenerator:
    def __init__(self, caption: PointingCaption | None) -> None:
        self.caption = caption
        self.calls = 0

    async def generate(self, event, images, context=None) -> PointingCaption | None:
        self.calls += 1
        return self.caption


class FakeSpeech:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def synthesize(self, text: str, language: str = "it") -> Audio:
        self.calls.append(text)
        return Audio(
            audio_format=AudioFormat.WAV,
            audio_bytes=b"audio",
            audio_duration=0.5,
        )


def _activation() -> PointingActivation:
    return PointingActivation(
        handedness=Handedness.RIGHT,
        ray=PointingRay(
            start=NormalizedPoint(x=0.3, y=0.5),
            end=NormalizedPoint(x=1.0, y=0.5),
        ),
    )


def _caption() -> PointingCaption:
    return PointingCaption(
        target="cartello",
        description="Un cartello rosso",
        visible_text="USCITA\nEXIT",
        text_confidence=0.9,
        text_complete=True,
        confidence=0.95,
        needs_repointing=False,
        needs_closer_view=False,
    )


def _overlay() -> PointingOverlay:
    activation = _activation()
    return PointingOverlay(
        handedness=activation.handedness,
        ray=activation.ray,
        state=PointingOverlayState.ACTIVE,
        confirmation_progress=1.0,
    )


def _frame(frame_id: int = 5) -> Frame:
    return Frame(
        frame_id=frame_id,
        image_bytes=b"jpeg",
        caption_mode=CaptionMode.POINTING,
    )


def _pipeline(
    activations: tuple[PointingActivation, ...],
    caption: PointingCaption | None,
    overlays: tuple[PointingOverlay, ...] = (),
):
    estimator = FakeEstimator()
    recognizer = StubRecognizer(activations, overlays)
    preparer = FakePreparer()
    generator = FakeGenerator(caption)
    speech = FakeSpeech()
    pipeline = PointingPipeline(
        hand_pose_estimator=estimator,
        gesture_recognizer=recognizer,
        event_gate=PointingEventGate(cooldown_seconds=0.0),
        image_preparer=preparer,
        caption_generator=generator,
        speech_synthesizer=speech,
        clock=lambda: 10.0,
    )
    return pipeline, estimator, recognizer, preparer, generator, speech


@pytest.mark.asyncio
async def test_no_activation_stops_before_images_vlm_and_tts() -> None:
    pipeline, estimator, _, preparer, generator, speech = _pipeline((), _caption())

    results = [result async for result in pipeline.process(_frame())]

    assert results == []
    assert estimator.calls == 1
    assert preparer.calls == 0
    assert generator.calls == 0
    assert speech.calls == []


@pytest.mark.asyncio
async def test_optional_diagnostics_record_a_frame_without_a_hand() -> None:
    recorder = Mock()
    pipeline = PointingPipeline(
        FakeEstimator(), StubRecognizer(()), PointingEventGate(), FakePreparer(),
        FakeGenerator(None), FakeSpeech(), clock=lambda: 10.0,
        research_recorder=recorder, diagnostics_enabled=True,
    )
    assert [r async for r in pipeline.process(_frame())] == []
    recorder.record.assert_called_once_with(
        "pointing_frame", frame_id=5, interval_ms=None, reason="no_hand", hands=[],
        recovery_used=False, pose_ms=ANY,
    )


@pytest.mark.asyncio
async def test_overlay_is_forwarded_even_without_vlm_activation() -> None:
    pipeline, _, _, preparer, generator, speech = _pipeline(
        (),
        _caption(),
        (_overlay(),),
    )
    received: list[
        tuple[tuple[PointingOverlay, ...], int, tuple[HandLandmarks, ...]]
    ] = []

    async def on_overlay(
        overlays: tuple[PointingOverlay, ...],
        frame_id: int,
        hands: tuple[HandLandmarks, ...],
    ) -> None:
        received.append((overlays, frame_id, hands))

    results = [
        result
        async for result in pipeline.process(
            _frame(),
            on_overlay=on_overlay,
        )
    ]

    assert results == []
    assert received == [((_overlay(),), 5, ())]
    assert preparer.calls == 0
    assert generator.calls == 0
    assert speech.calls == []


@pytest.mark.asyncio
async def test_activation_produces_one_complete_caption_and_one_audio() -> None:
    pipeline, _, _, preparer, generator, speech = _pipeline(
        (_activation(),),
        _caption(),
    )

    results = [result async for result in pipeline.process(_frame())]

    assert len(results) == 1
    assert results[0].frame_id == 5
    assert results[0].caption == (
        "Un cartello rosso. C'è scritto: USCITA\nEXIT"
    )
    assert preparer.calls == 1
    assert generator.calls == 1
    assert speech.calls == [results[0].caption]


@pytest.mark.asyncio
async def test_invalid_vlm_result_asks_to_point_again() -> None:
    pipeline, _, _, preparer, generator, speech = _pipeline(
        (_activation(),),
        None,
    )

    results = [result async for result in pipeline.process(_frame())]

    assert [result.caption for result in results] == [REPOINT_PROMPT]
    assert preparer.calls == 1
    assert generator.calls == 1
    assert speech.calls == [REPOINT_PROMPT]


@pytest.mark.asyncio
async def test_reset_and_close_are_forwarded_to_session_state() -> None:
    pipeline, estimator, recognizer, _, _, _ = _pipeline((), None)

    pipeline.reset()
    await pipeline.close()

    assert recognizer.reset_calls == 1
    assert estimator.closed


def test_caption_composition_falls_back_to_target() -> None:
    caption = _caption().model_copy(
        update={"description": "", "visible_text": None}
    )

    assert compose_accessibility_caption(caption) == "cartello"


def _hand_observation() -> HandObservation:
    return HandObservation(
        handedness=Handedness.RIGHT,
        image_landmarks=tuple(
            ImageLandmark(x=index / 100.0, y=0.123456, z=0.0)
            for index in range(21)
        ),
        world_landmarks=tuple(
            WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)
        ),
    )


@pytest.mark.asyncio
async def test_hand_landmarks_reach_the_client_without_any_gesture() -> None:
    pipeline, estimator, _, _, _, _ = _pipeline((), _caption(), ())
    estimator.estimate = _returning_hands()
    received: list[tuple[HandLandmarks, ...]] = []

    async def on_overlay(overlays, frame_id, hands) -> None:
        received.append(hands)

    _ = [
        result
        async for result in pipeline.process(_frame(), on_overlay=on_overlay)
    ]

    assert len(received) == 1
    hands = received[0]
    assert len(hands) == 1
    assert hands[0].handedness is Handedness.RIGHT
    assert len(hands[0].landmarks) == 21
    # Le coordinate arrivano arrotondate: il messaggio parte a ogni fotogramma.
    assert hands[0].landmarks[1] == ImagePoint(x=0.01, y=0.1235)


def _returning_hands():
    async def estimate(frame: Frame) -> HandPoseResult:
        return HandPoseResult(
            frame_id=frame.frame_id,
            hands=(_hand_observation(),),
        )

    return estimate


@pytest.mark.asyncio
async def test_activation_blocked_by_cooldown_is_returned_to_recognizer() -> None:
    recognizer = StubRecognizer((_activation(),))
    gate = PointingEventGate(cooldown_seconds=5.0)
    assert gate.allow(9.0)
    generator = FakeGenerator(_caption())
    pipeline = PointingPipeline(
        hand_pose_estimator=FakeEstimator(),
        gesture_recognizer=recognizer,
        event_gate=gate,
        image_preparer=FakePreparer(),
        caption_generator=generator,
        speech_synthesizer=FakeSpeech(),
        clock=lambda: 10.0,
    )

    results = [result async for result in pipeline.process(_frame())]

    assert results == []
    assert generator.calls == 0
    assert recognizer.cancelled == [_activation()]


def _lesson_caption(**fields) -> PointingCaption:
    return _caption().model_copy(update=fields)


def test_lesson_pointing_preserves_a_real_object_with_its_label() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    caption = _lesson_caption(
        target_kind="object", target="bottiglia", description="Una bottiglia rossa",
        visible_text="ACQUA", text_complete=True,
    )
    assert compose_lesson_caption(caption) == "Una bottiglia rossa. C'è scritto: ACQUA"


def test_lesson_pointing_uses_content_rules_for_a_slide_label() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    caption = _lesson_caption(
        target_kind="educational_content", target="Evaporazione",
        description="etichetta", visible_text="Evaporazione",
    )
    assert compose_lesson_caption(caption) == "Evaporazione"


def test_lesson_pointing_reads_a_label_once() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import (
        compose_lesson_caption,
    )

    caption = _lesson_caption(
        target="Evaporazione",
        description="Etichetta di un nodo con scritto Evaporazione",
        visible_text="Evaporazione",
    )

    assert compose_lesson_caption(caption) == (
        "Etichetta di un nodo con scritto Evaporazione"
    )
    assert compose_lesson_caption(
        _lesson_caption(target="Raccolta", description="etichetta", visible_text="Raccolta")
    ) == "Raccolta"


def test_lesson_pointing_skips_raw_chart_labels() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import (
        compose_lesson_caption,
    )

    caption = _lesson_caption(
        target="grafico",
        description="Grafico a linee della popolazione italiana dal 1950 al 2025.",
        visible_text="Popolazione italiana (milioni)\n60\n57\n47\n1950 1970 1990 2010 2025",
    )

    assert compose_lesson_caption(caption) == (
        "Grafico a linee della popolazione italiana dal 1950 al 2025."
    )


def test_lesson_pointing_reads_a_formula_only_in_words() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import (
        compose_lesson_caption,
    )

    caption = _lesson_caption(
        target="formula",
        description="a x al quadrato più b x più c uguale zero",
        visible_text="ax² + bx + c = 0",
    )

    assert compose_lesson_caption(caption) == (
        "a x al quadrato più b x più c uguale zero"
    )


@pytest.mark.asyncio
async def test_lesson_pointing_sends_the_slide_memory_to_the_model() -> None:
    from vision_caption.core.services.lesson_memory import LessonMemory

    class ContextGenerator(FakeGenerator):
        def __init__(self, caption) -> None:
            super().__init__(caption)
            self.contexts: list[str | None] = []

        async def generate(self, event, images, context=None):
            self.contexts.append(context)
            return await super().generate(event, images)

    memory = LessonMemory()
    memory.remember(2, 7, "Titolo: Equazioni di secondo grado.")
    generator = ContextGenerator(_caption())
    pipeline = PointingPipeline(
        hand_pose_estimator=FakeEstimator(),
        gesture_recognizer=StubRecognizer((_activation(),)),
        event_gate=PointingEventGate(cooldown_seconds=0.0),
        image_preparer=FakePreparer(),
        caption_generator=generator,
        speech_synthesizer=FakeSpeech(),
        clock=lambda: 10.0,
        lesson_memory=memory,
        speech_text=lambda text: text.upper(),
    )

    results = [result async for result in pipeline.process(_frame())]

    assert "Slide 2 di 7: Titolo: Equazioni" in generator.contexts[0]
    assert results[0].caption == results[0].caption.upper()


def test_lesson_pointing_reads_content_without_the_generic_slide_wrapper() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption
    caption = _lesson_caption(
        target="testo", description="Testo sulla slide proiettata",
        visible_text="Un visore pesa\n circa 500 grammi", target_kind="educational_content",
    )
    assert compose_lesson_caption(caption) == "Un visore pesa, circa 500 grammi"



def test_lesson_pointing_does_not_read_incomplete_text_from_outside_the_picture() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption
    caption = _lesson_caption(
        target="cabina arcade", description="immagine di una cabina arcade viola",
        visible_text="deogioco", text_complete=False, target_kind="educational_content",
    )
    assert compose_lesson_caption(caption) == "immagine di una cabina arcade viola"


def test_lesson_pointing_reads_a_long_text_instead_of_naming_it() -> None:
    """Sessione d0068e48c5ce: la frase a parete era trascritta ma non letta."""
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    caption = _lesson_caption(
        target_kind="educational_content", target="testo decorativo",
        description="testo decorativo a parete con una citazione sull'amore e la famiglia",
        visible_text="la più\nbella\ncosa\nche ci sia\nè una famiglia\nche si amiamo.",
        text_complete=True,
    )

    assert compose_lesson_caption(caption) == (
        "la più, bella, cosa, che ci sia, è una famiglia, che si amiamo. "
        "testo decorativo a parete con una citazione sull'amore e la famiglia"
    )


def test_lesson_pointing_reads_the_whole_label_of_a_real_object() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    caption = _lesson_caption(
        target_kind="object", target="scatola di medicinali",
        description="una scatola bianca e verde",
        visible_text="TACHIPIRINA 500 mg\ncompresse\nparacetamolo\n20 compresse",
        text_complete=True,
    )

    assert compose_lesson_caption(caption) == (
        "una scatola bianca e verde. C'è scritto: TACHIPIRINA 500 mg\n"
        "compresse\nparacetamolo\n20 compresse"
    )


def test_pointing_does_not_repeat_a_label_already_in_the_description() -> None:
    """Replay 9354113f2536/506: "con la scritta KIWI. C'è scritto: KIWI"."""
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    caption = _lesson_caption(
        target_kind="object", target="dispositivo elettronico",
        description="un dispositivo elettronico verde scuro con la scritta KIWI",
        visible_text="KIWI", text_complete=True,
    )

    assert compose_lesson_caption(caption) == (
        "un dispositivo elettronico verde scuro con la scritta KIWI"
    )


def test_lesson_pointing_reads_a_paragraph_longer_than_twenty_words() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption

    testo = (
        "La realtà virtuale permette di ricreare ambienti sicuri in cui la "
        "persona anziana può muoversi, esplorare e ritrovare ricordi senza "
        "rischi fisici."
    )
    caption = _lesson_caption(
        target_kind="educational_content", target="paragrafo",
        description="blocco di testo", visible_text=testo, text_complete=True,
    )

    assert compose_lesson_caption(caption) == testo


def test_pointed_picture_keeps_even_a_short_description_after_its_text() -> None:
    from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption
    caption = _lesson_caption(
        target_kind="educational_content", target="cabina arcade",
        description="Cabina arcade viola", visible_text="Sala prove", text_complete=True,
    )
    assert compose_lesson_caption(caption) == "Sala prove. Cabina arcade viola"


class PreflightRecognizer(StubRecognizer):
    def has_pointing_pose(self,hands):
        return bool(hands)


class PoseEstimator(FakeEstimator):
    def __init__(self,hands):
        super().__init__()
        self.hands=hands
    async def estimate(self,frame):
        self.calls+=1
        return HandPoseResult(frame_id=frame.frame_id,hands=self.hands)


@pytest.mark.asyncio
@pytest.mark.parametrize(('primary_hands','recovery_hands','expected_recovery_calls'),[
    ((),True,1), (True,True,0), ((),(),1),
])
async def test_mirror_recovery_is_only_used_when_primary_pose_is_missing(primary_hands,recovery_hands,expected_recovery_calls):
    hand=_hand_observation()
    primary=PoseEstimator((hand,) if primary_hands else ())
    recovery=PoseEstimator((hand,) if recovery_hands else ())
    recorder=Mock()
    pipeline=PointingPipeline(primary,PreflightRecognizer(()),PointingEventGate(),FakePreparer(),FakeGenerator(None),FakeSpeech(),research_recorder=recorder,recovery_pose_estimator=recovery)
    assert [r async for r in pipeline.process(_frame())]==[]
    assert recovery.calls==expected_recovery_calls
    if expected_recovery_calls:
        expected='mirror' if recovery_hands else 'primary'
        assert recorder.record.call_args.kwargs['selected']==expected
    await pipeline.close()
    assert primary.closed and recovery.closed


@pytest.mark.asyncio
@pytest.mark.parametrize('flag',['needs_repointing','needs_closer_view'])
async def test_uncertain_target_gives_actionable_feedback_instead_of_the_guess(flag):
    from vision_caption.core.services.pointing.pointing_pipeline import CLOSER_VIEW_PROMPT
    caption=_caption().model_copy(update={flag:True,'description':'Una ipotesi non affidabile'})
    pipeline,*_=_pipeline((_activation(),),caption)
    results=[r async for r in pipeline.process(_frame())]
    assert results[0].caption==(CLOSER_VIEW_PROMPT if flag=='needs_closer_view' else REPOINT_PROMPT)
    assert 'ipotesi' not in results[0].caption


@pytest.mark.asyncio
async def test_two_fingers_in_pointing_ask_the_phone_to_go_back_to_auto() -> None:
    """Il gesto di modalità vale nei due versi e non genera un puntamento."""
    from vision_caption.core.domain.hand_pose import HandPoseResult
    from vision_caption.core.services.pointing.mode_gesture import (
        ModeGestureDetector,
        ModeGestureSettings,
    )

    from tests.unit.test_mode_gesture import _victory

    class HandEstimator(FakeEstimator):
        async def estimate(self, frame):
            self.calls += 1
            return HandPoseResult(frame_id=frame.frame_id, hands=(_victory(),))

    generator = FakeGenerator(_caption())
    recognizer = StubRecognizer((_activation(),))
    now = [0.0]
    pipeline = PointingPipeline(
        hand_pose_estimator=HandEstimator(),
        gesture_recognizer=recognizer,
        event_gate=PointingEventGate(cooldown_seconds=0.0),
        image_preparer=FakePreparer(),
        caption_generator=generator,
        speech_synthesizer=FakeSpeech(),
        clock=lambda: now[0],
        mode_gesture=ModeGestureDetector(ModeGestureSettings(hold_seconds=0.4)),
    )
    switches: list[tuple] = []

    async def on_mode_switch(mode, frame_id) -> None:
        switches.append((mode.value, frame_id))

    first = [r async for r in pipeline.process(_frame(), on_mode_switch=on_mode_switch)]
    now[0] = 0.5
    second = [r async for r in pipeline.process(_frame(), on_mode_switch=on_mode_switch)]

    # Il primo frame tiene il gesto, il secondo lo conferma e cambia modalità.
    assert switches == [("AUTO", _frame().frame_id)]
    assert second == []
    assert recognizer.reset_calls >= 1
