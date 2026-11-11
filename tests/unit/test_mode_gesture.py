import pytest

from vision_caption.core.domain.hand_pose import (
    HandLandmark,
    HandObservation,
    Handedness,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.services.pointing.mode_gesture import (
    ModeGestureDetector,
    ModeGestureSettings,
    is_two_finger_sign,
)
from vision_caption.core.services.pointing.stop_gesture import (
    StopGestureDetector,
    StopGestureSettings,
)

from tests.unit.test_stop_gesture import FINGERS, _open_palm
from tests.unit.test_pointing_gesture_recognizer import _pointing_hand


def _hand(extended: tuple[int, ...]) -> HandObservation:
    """Dita dritte quelle elencate (indice 0..3), le altre ripiegate su sé stesse."""
    world = [WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    for column, joints in enumerate(FINGERS):
        for row, joint in enumerate(joints):
            if column in extended:
                point = WorldLandmark(x=float(column), y=-float(row), z=0.0)
            else:
                # Un dito chiuso: le falangi tornano indietro e l'angolo crolla.
                offsets = ((0.0, 0.0), (0.0, -1.0), (0.4, -0.4), (0.4, 0.4))
                dx, dy = offsets[row]
                point = WorldLandmark(x=float(column) + dx, y=dy, z=0.0)
            world[joint.value] = point
    return HandObservation(
        handedness=Handedness.RIGHT,
        image_landmarks=tuple(ImageLandmark(x=0.5, y=0.5, z=0.0) for _ in range(21)),
        world_landmarks=tuple(world),
        confidence=0.99,
    )


def _victory() -> HandObservation:
    return _hand((0, 1))


def test_two_fingers_held_switch_once_until_the_hand_is_lowered() -> None:
    detector = ModeGestureDetector(
        ModeGestureSettings(hold_seconds=0.7, cooldown_seconds=0.0)
    )
    sign = (_victory(),)

    assert detector.update(sign, 0.0) is False
    assert detector.update(sign, 0.5) is False
    assert detector.update(sign, 0.8) is True
    # Tenere la mano alzata non fa rimbalzare le modalità.
    assert detector.update(sign, 1.5) is False
    detector.update((), 1.6)
    # Riarmato: va tenuta di nuovo per hold_seconds, non basta rialzarla.
    assert detector.update(sign, 2.4) is False
    assert detector.update(sign, 3.2) is True


def test_the_cooldown_keeps_the_modes_from_ping_ponging() -> None:
    detector = ModeGestureDetector(
        ModeGestureSettings(hold_seconds=0.1, cooldown_seconds=3.0)
    )
    sign = (_victory(),)

    detector.update(sign, 0.0)
    assert detector.update(sign, 0.2) is True
    detector.update((), 0.3)
    assert detector.update(sign, 0.4) is False
    assert detector.update(sign, 1.0) is False
    assert detector.update(sign, 3.5) is True


def test_the_other_two_gestures_are_not_a_mode_change() -> None:
    settings = ModeGestureSettings()
    # Lo stop: quattro dita tese.
    assert is_two_finger_sign(_open_palm(), settings) is False
    # Il puntamento: solo l'indice.
    assert is_two_finger_sign(_pointing_hand(), settings) is False
    assert is_two_finger_sign(_victory(), settings) is True


def test_the_mode_change_is_not_a_stop() -> None:
    stop = StopGestureDetector(StopGestureSettings(hold_seconds=0.1, cooldown_seconds=0.0))
    sign = (_victory(),)

    stop.update(sign, 0.0)
    assert stop.update(sign, 1.0) is False
    assert stop.palm_visible(sign) is False


def test_impossible_thresholds_are_refused() -> None:
    with pytest.raises(ValueError):
        ModeGestureSettings(min_extended_deg=100.0, max_folded_deg=120.0)
    with pytest.raises(ValueError):
        ModeGestureSettings(hold_seconds=-1.0)


# --- Il gesto dentro le pipeline ------------------------------------------

from unittest.mock import AsyncMock, Mock  # noqa: E402

from vision_caption.core.domain.frame import CaptionMode, Frame  # noqa: E402
from vision_caption.core.domain.hand_pose import HandPoseResult  # noqa: E402
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult  # noqa: E402
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort  # noqa: E402
from vision_caption.core.services.caption_pipeline import CaptionPipeline  # noqa: E402
from vision_caption.core.services.rate_limiter import RateLimiter  # noqa: E402

from tests.unit.test_stop_gesture import FakeEstimator  # noqa: E402
from tests.unit.test_caption_pipeline import (  # noqa: E402
    FakeCaptionGenerator,
    FakeSpeechSynthesizer,
)


def _auto_pipeline(hands, now, detector):
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(return_value=SceneAnalysisResult(is_change=True))
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=FakeCaptionGenerator("Una stanza."),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
        hand_pose_estimator=FakeEstimator(hands),
        mode_gesture=detector,
        clock=lambda: now[0],
    )
    return pipeline, scene_detector


@pytest.mark.asyncio
async def test_two_fingers_in_auto_ask_the_phone_for_pointing() -> None:
    now = [0.0]
    detector = ModeGestureDetector(ModeGestureSettings(hold_seconds=0.4))
    pipeline, scene_detector = _auto_pipeline((_victory(),), now, detector)
    switches: list[tuple[CaptionMode, int]] = []

    async def on_mode_switch(mode, frame_id) -> None:
        switches.append((mode, frame_id))

    frame = Frame(frame_id=1, image_bytes=b"jpeg", caption_mode=CaptionMode.AUTO)
    results = [r async for r in pipeline.process(frame, on_mode_switch=on_mode_switch)]
    assert switches == []
    # La mano davanti all'obiettivo non viene descritta mentre si tiene il gesto.
    assert results == []

    now[0] = 0.5
    frame = Frame(frame_id=2, image_bytes=b"jpeg", caption_mode=CaptionMode.AUTO)
    results = [r async for r in pipeline.process(frame, on_mode_switch=on_mode_switch)]

    assert switches == [(CaptionMode.POINTING, 2)]
    assert results == []
    # Il frame con la mano non diventa il riferimento della scena.
    scene_detector.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_without_the_gesture_auto_keeps_describing() -> None:
    now = [0.0]
    detector = ModeGestureDetector(ModeGestureSettings(hold_seconds=0.4))
    pipeline, _ = _auto_pipeline((), now, detector)
    switches: list[tuple] = []

    async def on_mode_switch(mode, frame_id) -> None:
        switches.append((mode, frame_id))

    frame = Frame(frame_id=1, image_bytes=b"jpeg", caption_mode=CaptionMode.AUTO)
    results = [r async for r in pipeline.process(frame, on_mode_switch=on_mode_switch)]

    assert switches == []
    assert [result.caption for result in results] == ["Una stanza."]
