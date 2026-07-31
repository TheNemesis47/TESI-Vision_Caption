from pathlib import Path

import cv2
import numpy as np
import pytest

from vision_caption.adapters.pointing.opencv_pointing_image_preparer import (
    OpenCVPointingImagePreparer,
    PointingImageSettings,
    build_corridor_polygon,
)
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.hand_pose import Handedness
from vision_caption.core.domain.pointing import (
    NormalizedPoint,
    PointingEvent,
    PointingRay,
)


def _jpeg(width: int = 160, height: int = 100) -> bytes:
    image = np.full((height, width, 3), 180, dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


def _event() -> PointingEvent:
    return PointingEvent(
        handedness=Handedness.RIGHT,
        ray=PointingRay(
            start=NormalizedPoint(x=0.25, y=0.5),
            end=NormalizedPoint(x=1.0, y=0.5),
        ),
        frame_id=7,
    )


@pytest.mark.asyncio
async def test_preparer_returns_three_valid_images_and_keeps_clean_frame() -> None:
    frame_bytes = _jpeg()
    frame = Frame(
        frame_id=7,
        image_bytes=frame_bytes,
        caption_mode=CaptionMode.POINTING,
    )

    images = await OpenCVPointingImagePreparer().prepare(frame, _event())

    context = cv2.imdecode(
        np.frombuffer(images.context_jpeg, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )
    focus = cv2.imdecode(
        np.frombuffer(images.focus_jpeg, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )
    clean = cv2.imdecode(
        np.frombuffer(images.clean_jpeg, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )
    assert context is not None
    assert focus is not None
    assert clean is not None
    assert context.shape == clean.shape
    assert focus.shape[0] <= clean.shape[0]
    assert focus.shape[1] <= clean.shape[1]
    assert images.clean_jpeg == frame_bytes
    assert not np.array_equal(context, clean)


@pytest.mark.asyncio
async def test_debug_flag_saves_the_exact_three_images_sent_to_vlm(
    tmp_path: Path,
) -> None:
    frame = Frame(
        frame_id=7,
        image_bytes=_jpeg(),
        caption_mode=CaptionMode.POINTING,
    )
    preparer = OpenCVPointingImagePreparer(
        settings=PointingImageSettings(
            debug_save_images=True,
            debug_output_dir=tmp_path,
        )
    )

    images = await preparer.prepare(frame, _event())

    capture_dirs = list(tmp_path.iterdir())
    assert len(capture_dirs) == 1
    capture_dir = capture_dirs[0]
    assert capture_dir.name.startswith("frame_00000007_")
    assert (
        capture_dir / "01_context_with_corridor.jpg"
    ).read_bytes() == images.context_jpeg
    assert (
        capture_dir / "02_focus_darkened_and_cropped.jpg"
    ).read_bytes() == images.focus_jpeg
    assert (
        capture_dir / "03_clean_original.jpg"
    ).read_bytes() == images.clean_jpeg


@pytest.mark.asyncio
async def test_debug_images_are_not_saved_when_flag_is_disabled(
    tmp_path: Path,
) -> None:
    frame = Frame(
        frame_id=7,
        image_bytes=_jpeg(),
        caption_mode=CaptionMode.POINTING,
    )
    preparer = OpenCVPointingImagePreparer(
        settings=PointingImageSettings(
            debug_save_images=False,
            debug_output_dir=tmp_path,
        )
    )

    await preparer.prepare(frame, _event())

    assert list(tmp_path.iterdir()) == []


def test_corridor_polygon_is_clipped_to_frame() -> None:
    polygon = build_corridor_polygon(
        _event().ray,
        frame_width=160,
        frame_height=100,
        settings=PointingImageSettings(),
    )

    assert polygon is not None
    assert np.all(polygon[:, 0] >= 0)
    assert np.all(polygon[:, 0] < 160)
    assert np.all(polygon[:, 1] >= 0)
    assert np.all(polygon[:, 1] < 100)
