from loguru import logger
from collections import Counter
import numpy as np
import cv2

from vision_caption.adapters.scene.SsimSceneDetectorAdapter import SsimSceneDetectorAdapter
from vision_caption.core.domain.detection import BoundingBox, Detection
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.ports.SceneDetectorPort import SceneDetectorPort


class HybridSceneDetectorAdapter:
    def __init__(
        self,
        ssim_detector: SsimSceneDetectorAdapter,
        rfdetr_detector: SceneDetectorPort,
        suppress_unchanged_class_counts: bool = True,
        semantic_box_iou_threshold: float = 0.65,
    ):
        self._ssim_detector = ssim_detector
        self._rfdetr_detector = rfdetr_detector
        self._suppress_unchanged_class_counts = suppress_unchanged_class_counts
        self._semantic_box_iou_threshold = semantic_box_iou_threshold
        self._last_announced_detections: tuple[Detection, ...] | None = None
        self._pending_detections: tuple[Detection, ...] | None = None

    @staticmethod
    def _box_iou(first: BoundingBox, second: BoundingBox) -> float:
        intersection_width = max(
            0.0,
            min(first.x_max, second.x_max) - max(first.x_min, second.x_min),
        )
        intersection_height = max(
            0.0,
            min(first.y_max, second.y_max) - max(first.y_min, second.y_min),
        )
        intersection = intersection_width * intersection_height
        first_area = max(0.0, first.x_max - first.x_min) * max(
            0.0,
            first.y_max - first.y_min,
        )
        second_area = max(0.0, second.x_max - second.x_min) * max(
            0.0,
            second.y_max - second.y_min,
        )
        union = first_area + second_area - intersection
        return intersection / union if union > 0.0 else 0.0

    def _same_announced_scene(
        self,
        current: tuple[Detection, ...],
    ) -> bool:
        previous = self._last_announced_detections
        if previous is None:
            return False

        current_counts = Counter(item.class_name for item in current)
        previous_counts = Counter(item.class_name for item in previous)
        if current_counts != previous_counts:
            return False

        for class_name in current_counts:
            current_class = [
                item for item in current if item.class_name == class_name
            ]
            available_previous = [
                item for item in previous if item.class_name == class_name
            ]
            for current_item in current_class:
                best_index, best_previous = max(
                    enumerate(available_previous),
                    key=lambda pair: self._box_iou(
                        current_item.bbox,
                        pair[1].bbox,
                    ),
                )
                best_iou = self._box_iou(
                    current_item.bbox,
                    best_previous.bbox,
                )
                if best_iou < self._semantic_box_iou_threshold:
                    return False
                available_previous.pop(best_index)

        return True
    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        # 1. Analisi rapida con SSIM e decodifica frame
        nparr = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        ssim_result = await self._ssim_detector.analyze(img)

        # 2. Se non c'è, early exit
        if not ssim_result.is_change:
            return SceneAnalysisResult(
                is_change=False,
                detections=(),
                ssim_score=ssim_result.ssim_score,
                execution_ms=ssim_result.execution_ms,
                suppressed_by="ssim",
            )

        # 3. Se SSIM rileva un candidato, verifichiamo il significato con RF-DETR.
        score_display = (
            f"{ssim_result.ssim_score:.3f}"
            if ssim_result.ssim_score is not None
            else "N/A"
        )
        logger.debug(
            f"SSIM structural change (score: {score_display}). "
            "Checking semantic meaning with RF-DETR..."
        )
        rfdetr_result = await self._rfdetr_detector.analyze(frame)

        # Il keyframe strutturale rappresenta l'ultimo candidato già analizzato
        # da RF-DETR. In questo modo piccoli movimenti si accumulano fino alla
        # soglia SSIM, ma lo stesso cambiamento non richiama RF-DETR a ogni frame
        # soltanto perché VLM o rate limiter non sono ancora disponibili.
        await self._ssim_detector.update_old_image(img)

        # 4. Contiamo le occorrenze, ad esempio person=1 e laptop=2.
        current_objects = Counter(
            detection.class_name for detection in rfdetr_result.detections
        )

        # 5. Controllo di identità semantica: non bastano classi e quantità;
        # anche la posizione degli oggetti deve essere sufficientemente stabile.
        if (
            self._suppress_unchanged_class_counts
            and self._same_announced_scene(rfdetr_result.detections)
        ):
            logger.debug(
                "Semantic scene is unchanged "
                f"{dict(current_objects)}; suppressing structural noise."
            )
            return SceneAnalysisResult(
                is_change=False,
                detections=rfdetr_result.detections,
                ssim_score=ssim_result.ssim_score,
                execution_ms=(ssim_result.execution_ms or 0.0)
                + (rfdetr_result.execution_ms or 0.0),
                suppressed_by="semantic",
            )

        previous_objects = Counter(
            item.class_name
            for item in (self._last_announced_detections or ())
        )
        logger.debug(
            "Semantic change detected. "
            f"Old: {dict(previous_objects)}, New: {dict(current_objects)}"
        )
        self._pending_detections = rfdetr_result.detections

        return SceneAnalysisResult(
            is_change=True,
            detections=rfdetr_result.detections,
            ssim_score=ssim_result.ssim_score,
            execution_ms=(ssim_result.execution_ms or 0.0)
            + (rfdetr_result.execution_ms or 0.0),
        )

    async def commit(self):
        if self._pending_detections is not None:
            self._last_announced_detections = self._pending_detections
