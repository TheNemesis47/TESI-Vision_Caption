import cv2
import numpy as np
import pytest

from vision_caption.adapters.scene.HybridSceneDetectorAdapter import (
    HybridSceneDetectorAdapter,
)
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import (
    SsimSceneDetectorAdapter,
)
from vision_caption.core.domain.detection import BoundingBox, Detection
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult


def _jpeg(value: int) -> bytes:
    image = np.full((64, 64, 3), value, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def _detection(x_min: float, x_max: float) -> Detection:
    return Detection(
        class_name="chair",
        confidence=0.9,
        bbox=BoundingBox(
            x_min=x_min,
            y_min=10,
            x_max=x_max,
            y_max=40,
        ),
    )


class SequencedDetector:
    def __init__(self, detections: list[tuple[Detection, ...]]) -> None:
        self._detections = iter(detections)
        self.calls = 0

    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        self.calls += 1
        return SceneAnalysisResult(
            is_change=True,
            detections=next(self._detections),
        )

    async def commit(self) -> None:
        return None


def _frame(frame_id: int, value: int) -> Frame:
    return Frame(
        frame_id=frame_id,
        image_bytes=_jpeg(value),
        caption_mode=CaptionMode.AUTO,
    )


@pytest.mark.asyncio
async def test_same_classes_and_stable_boxes_are_suppressed() -> None:
    detector = SequencedDetector(
        [(_detection(10, 40),), (_detection(11, 41),)]
    )
    hybrid = HybridSceneDetectorAdapter(
        ssim_detector=SsimSceneDetectorAdapter(threshold=0.55),
        rfdetr_detector=detector,
        semantic_box_iou_threshold=0.65,
    )

    first = await hybrid.analyze(_frame(1, 0))
    await hybrid.commit()
    second = await hybrid.analyze(_frame(2, 255))

    assert first.is_change
    assert not second.is_change
    assert second.suppressed_by == "semantic"


@pytest.mark.asyncio
async def test_same_class_with_moved_box_is_a_semantic_change() -> None:
    detector = SequencedDetector(
        [(_detection(5, 25),), (_detection(35, 55),)]
    )
    hybrid = HybridSceneDetectorAdapter(
        ssim_detector=SsimSceneDetectorAdapter(threshold=0.55),
        rfdetr_detector=detector,
        semantic_box_iou_threshold=0.65,
    )

    await hybrid.analyze(_frame(1, 0))
    await hybrid.commit()
    result = await hybrid.analyze(_frame(2, 255))

    assert result.is_change


@pytest.mark.asyncio
async def test_rfdetr_candidate_refreshes_structural_keyframe() -> None:
    detector = SequencedDetector(
        [(_detection(5, 25),), (_detection(35, 55),)]
    )
    hybrid = HybridSceneDetectorAdapter(
        ssim_detector=SsimSceneDetectorAdapter(threshold=0.55),
        rfdetr_detector=detector,
    )

    await hybrid.analyze(_frame(1, 0))
    await hybrid.commit()
    changed = await hybrid.analyze(_frame(2, 255))
    repeated = await hybrid.analyze(_frame(3, 255))

    assert changed.is_change
    assert not repeated.is_change
    assert repeated.suppressed_by == "ssim"
    assert detector.calls == 2
