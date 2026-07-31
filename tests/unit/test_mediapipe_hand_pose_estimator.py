from types import SimpleNamespace

import pytest

from vision_caption.adapters.hand_tracking.mediapipe_hand_pose_estimator import (
    MediaPipeHandPoseEstimator,
    MediaPipeHandPoseSettings,
    convert_mediapipe_result,
    next_video_timestamp_ms,
)
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.hand_pose import Handedness


def _landmark(index: int) -> SimpleNamespace:
    return SimpleNamespace(
        x=index / 100.0,
        y=index / 200.0,
        z=-index / 300.0,
    )


def test_convert_mediapipe_result_maps_all_landmarks() -> None:
    result = SimpleNamespace(
        hand_landmarks=[[_landmark(index) for index in range(21)]],
        hand_world_landmarks=[[_landmark(index) for index in range(21)]],
        handedness=[
            [SimpleNamespace(category_name="Right", score=0.97)]
        ],
    )

    converted = convert_mediapipe_result(result, frame_id=42)

    assert converted.frame_id == 42
    assert len(converted.hands) == 1
    assert converted.hands[0].handedness == Handedness.RIGHT
    assert converted.hands[0].confidence == pytest.approx(0.97)
    assert len(converted.hands[0].image_landmarks) == 21
    assert len(converted.hands[0].world_landmarks) == 21


def test_convert_mediapipe_result_ignores_incomplete_hands() -> None:
    result = SimpleNamespace(
        hand_landmarks=[[_landmark(index) for index in range(20)]],
        hand_world_landmarks=[[_landmark(index) for index in range(20)]],
        handedness=[],
    )

    assert convert_mediapipe_result(result, frame_id=1).hands == ()


def test_video_timestamp_is_strictly_increasing() -> None:
    first = next_video_timestamp_ms(-1)
    second = next_video_timestamp_ms(first)

    assert second > first


@pytest.mark.asyncio
async def test_estimator_is_lazy_and_rejects_use_after_close(tmp_path) -> None:
    estimator = MediaPipeHandPoseEstimator(
        MediaPipeHandPoseSettings(
            model_path=tmp_path / "missing-model.task"
        )
    )
    await estimator.close()

    with pytest.raises(RuntimeError, match="già stato chiuso"):
        await estimator.estimate(
            Frame(
                frame_id=1,
                image_bytes=b"not-used",
                caption_mode=CaptionMode.POINTING,
            )
        )
