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


def _slide_jpeg(blur: int = 0, shift: int = 0) -> bytes:
    image = np.full((480, 640, 3), 255, dtype=np.uint8)
    cv2.putText(image, "Le derivate", (40 + shift, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 3)
    for row, text in enumerate(["- limite", "- catena", "- prodotto"]):
        cv2.putText(image, text, (60 + shift, 180 + row * 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    if blur:
        image = cv2.GaussianBlur(image, (blur, blur), 0)
    return cv2.imencode(".jpg", image)[1].tobytes()


def _blank_slide_frame(frame_id: int, data: bytes) -> Frame:
    return Frame(frame_id=frame_id, image_bytes=data, caption_mode=CaptionMode.AUTO)


@pytest.mark.asyncio
async def test_blurry_frame_waits_for_a_steady_one_without_moving_the_reference() -> None:
    rfdetr = SequencedDetector([(), ()])
    detector = HybridSceneDetectorAdapter(
        # Soglia alta: anche la slide sfocata deve risultare un cambiamento,
        # così è il filtro di nitidezza, non SSIM, a fermarla.
        ssim_detector=SsimSceneDetectorAdapter(threshold=0.995),
        rfdetr_detector=rfdetr,
        min_sharpness=25.0,
    )
    blank = np.full((480, 640, 3), 255, dtype=np.uint8)
    await detector.analyze(
        _blank_slide_frame(1, cv2.imencode(".jpg", blank)[1].tobytes())
    )

    blurry = await detector.analyze(_blank_slide_frame(2, _slide_jpeg(blur=15)))
    sharp = await detector.analyze(_blank_slide_frame(3, _slide_jpeg()))

    assert blurry.suppressed_by == "blur"
    assert blurry.sharpness < 25.0
    assert sharp.is_change
    assert sharp.sharpness > 25.0
    assert rfdetr.calls == 1


@pytest.mark.asyncio
async def test_without_threshold_blurry_frames_are_still_analysed() -> None:
    rfdetr = SequencedDetector([(), ()])
    detector = HybridSceneDetectorAdapter(
        ssim_detector=SsimSceneDetectorAdapter(threshold=0.9),
        rfdetr_detector=rfdetr,
    )
    blank = np.full((480, 640, 3), 255, dtype=np.uint8)
    await detector.analyze(
        _blank_slide_frame(1, cv2.imencode(".jpg", blank)[1].tobytes())
    )

    result = await detector.analyze(_blank_slide_frame(2, _slide_jpeg(blur=15)))

    assert result.suppressed_by != "blur"
