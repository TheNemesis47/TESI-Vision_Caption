from collections.abc import AsyncIterator

import pytest

from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.domain.captionResult import CaptionResult
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.hand_pose import (
    HandPoseResult,
    Handedness,
)
from vision_caption.core.domain.pointing import (
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

    def update(self, hands, *, timestamp):
        self.calls += 1
        return PointingRecognitionResult(
            activations=self.activations if self.calls == 1 else (),
            overlays=self.overlays,
        )

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

    async def generate(self, event, images) -> PointingCaption | None:
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
async def test_overlay_is_forwarded_even_without_vlm_activation() -> None:
    pipeline, _, _, preparer, generator, speech = _pipeline(
        (),
        _caption(),
        (_overlay(),),
    )
    received: list[tuple[tuple[PointingOverlay, ...], int]] = []

    async def on_overlay(
        overlays: tuple[PointingOverlay, ...],
        frame_id: int,
    ) -> None:
        received.append((overlays, frame_id))

    results = [
        result
        async for result in pipeline.process(
            _frame(),
            on_overlay=on_overlay,
        )
    ]

    assert results == []
    assert received == [((_overlay(),), 5)]
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
async def test_invalid_vlm_result_is_never_sent_to_tts() -> None:
    pipeline, _, _, preparer, generator, speech = _pipeline(
        (_activation(),),
        None,
    )

    results = [result async for result in pipeline.process(_frame())]

    assert results == []
    assert preparer.calls == 1
    assert generator.calls == 1
    assert speech.calls == []


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
