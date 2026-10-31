from unittest.mock import AsyncMock, Mock

import pytest

from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.hand_pose import (
    HandLandmark,
    HandObservation,
    HandPoseResult,
    Handedness,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort
from vision_caption.core.services.caption_pipeline import CaptionPipeline
from vision_caption.core.services.pointing.stop_gesture import (
    StopGestureDetector,
    StopGestureSettings,
)
from vision_caption.core.services.rate_limiter import RateLimiter

from tests.unit.test_caption_pipeline import FakeCaptionGenerator, FakeSpeechSynthesizer
from tests.unit.test_pointing_gesture_recognizer import _pointing_hand


FINGERS = (
    (HandLandmark.INDEX_FINGER_MCP, HandLandmark.INDEX_FINGER_PIP, HandLandmark.INDEX_FINGER_DIP, HandLandmark.INDEX_FINGER_TIP),
    (HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.MIDDLE_FINGER_DIP, HandLandmark.MIDDLE_FINGER_TIP),
    (HandLandmark.RING_FINGER_MCP, HandLandmark.RING_FINGER_PIP, HandLandmark.RING_FINGER_DIP, HandLandmark.RING_FINGER_TIP),
    (HandLandmark.PINKY_MCP, HandLandmark.PINKY_PIP, HandLandmark.PINKY_DIP, HandLandmark.PINKY_TIP),
)


def _open_palm() -> HandObservation:
    """Quattro dita dritte e parallele, come una mano alzata per dire stop."""
    world = [WorldLandmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    for column, joints in enumerate(FINGERS):
        for row, joint in enumerate(joints):
            world[joint.value] = WorldLandmark(x=float(column), y=-float(row), z=0.0)
    return HandObservation(
        handedness=Handedness.RIGHT,
        image_landmarks=tuple(ImageLandmark(x=0.5, y=0.5, z=0.0) for _ in range(21)),
        world_landmarks=tuple(world),
        confidence=0.99,
    )


def test_open_palm_held_stops_once_until_the_hand_is_lowered() -> None:
    detector = StopGestureDetector(StopGestureSettings(hold_seconds=0.4, cooldown_seconds=0.0))
    palm = (_open_palm(),)

    assert detector.update(palm, 0.0) is False
    assert detector.update(palm, 0.5) is True
    assert detector.update(palm, 1.0) is False
    assert detector.update((), 1.5) is False
    assert detector.update(palm, 2.0) is False
    assert detector.update(palm, 2.5) is True


def test_a_hand_passing_in_front_of_the_camera_does_not_stop() -> None:
    detector = StopGestureDetector(StopGestureSettings(hold_seconds=0.4))

    assert detector.update((_open_palm(),), 0.0) is False
    assert detector.update((), 0.2) is False
    assert detector.update((_open_palm(),), 0.3) is False


def test_cooldown_blocks_a_second_stop_too_soon() -> None:
    detector = StopGestureDetector(StopGestureSettings(hold_seconds=0.0, cooldown_seconds=2.0))
    palm = (_open_palm(),)

    assert detector.update(palm, 0.0) is True
    detector.update((), 0.5)
    assert detector.update(palm, 1.0) is False
    detector.update((), 1.5)
    assert detector.update(palm, 3.0) is True


def test_pointing_hand_is_not_a_stop_gesture() -> None:
    detector = StopGestureDetector()

    assert not detector.palm_visible((_pointing_hand(),))
    assert detector.palm_visible((_open_palm(),))


class FakeEstimator:
    def __init__(self, hands) -> None:
        self.hands = hands

    async def estimate(self, frame):
        return HandPoseResult(frame_id=frame.frame_id, hands=self.hands)

    async def close(self) -> None:
        pass


def _pipeline(hands, now):
    scene_detector = Mock(spec=SceneDetectorPort)
    scene_detector.analyze = AsyncMock(return_value=SceneAnalysisResult(is_change=True))
    scene_detector.commit = AsyncMock()
    rate_limiter = Mock(spec=RateLimiter)
    rate_limiter.can_execute.return_value = True
    pipeline = CaptionPipeline(
        scene_detector=scene_detector,
        caption_generator=FakeCaptionGenerator("Titolo: Le derivate."),
        speech_synthesizer=FakeSpeechSynthesizer(),
        rate_limiter=rate_limiter,
        hand_pose_estimator=FakeEstimator(hands),
        stop_gesture=StopGestureDetector(StopGestureSettings(hold_seconds=0.4)),
        clock=lambda: now[0],
    )
    return pipeline, scene_detector


def _frame(frame_id: int) -> Frame:
    return Frame(frame_id=frame_id, image_bytes=b"jpeg", caption_mode=CaptionMode.AUTO)


@pytest.mark.asyncio
async def test_held_palm_sends_stop_and_never_describes_the_hand() -> None:
    now = [0.0]
    pipeline, scene_detector = _pipeline((_open_palm(),), now)
    stops: list[int] = []

    async def on_stop_audio(frame_id: int) -> None:
        stops.append(frame_id)

    first = [r async for r in pipeline.process(_frame(1), on_stop_audio=on_stop_audio)]
    now[0] = 0.5
    second = [r async for r in pipeline.process(_frame(2), on_stop_audio=on_stop_audio)]

    assert first == [] and second == []
    assert stops == [2]
    scene_detector.analyze.assert_not_called()


@pytest.mark.asyncio
async def test_without_a_palm_the_slide_is_described_as_usual() -> None:
    now = [0.0]
    pipeline, scene_detector = _pipeline((_pointing_hand(),), now)

    results = [r async for r in pipeline.process(_frame(1))]

    assert [r.caption for r in results] == ["Titolo: Le derivate."]
    scene_detector.analyze.assert_called_once()
