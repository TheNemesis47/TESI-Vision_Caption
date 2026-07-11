from loguru import logger
from collections import Counter
import numpy as np
import cv2

from vision_caption.adapters.scene.RfdetrSceneDetectorAdapter import RfdetrSceneDetectorAdapter
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import SsimSceneDetectorAdapter
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult


class HybridSceneDetectorAdapter:
    def __init__(self, ssim_detector: SsimSceneDetectorAdapter, rfdetr_detector: RfdetrSceneDetectorAdapter):
        self._ssim_detector = ssim_detector
        self._rfdetr_detector = rfdetr_detector
        # STATO: ricorda cosa c'era nell'ultimo frame cambiato
        self._last_detected_objects: Counter[str] | None = None
        self._pending_img = None
        self._pending_objects: Counter[str] | None = None


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
                execution_ms=ssim_result.execution_ms
            )
            
        # 3. Se SSIM dice che la struttura è cambiata (es. dondolio), interroghiamo l'AI (RF-DETR)
        score_display = f"{ssim_result.ssim_score:.3f}" if ssim_result.ssim_score is not None else "N/A"
        logger.info(f"SSIM structural change (score: {score_display}). Checking semantic meaning with RF-DETR...")
        rfdetr_result = await self._rfdetr_detector.analyze(frame)
        
        # 4. Estrarre gli oggetti attuali contando le occorrenze (es. {"person": 1, "laptop": 2})
        current_objects = Counter([d.class_name for d in rfdetr_result.detections])
        
        # 5. Controllo di Identità Semantica
        # Se non è il primo frame e la lista degli oggetti è ESATTAMENTE UGUALE alla precedente
        if self._last_detected_objects is not None and current_objects == self._last_detected_objects:
            logger.info(f"Semantic meaning is identical {dict(current_objects)}. Suppressing false positive! 🚫")
            return SceneAnalysisResult(
                is_change=False,
                detections=rfdetr_result.detections,
                ssim_score=ssim_result.ssim_score,
                execution_ms=(ssim_result.execution_ms or 0.0) + (rfdetr_result.execution_ms or 0.0)
            )

        # Aggiorniamo lo stato con i nuovi oggetti
        logger.warning(f"True semantic change detected! Old: {dict(self._last_detected_objects or {})}, New: {dict(current_objects)}")
        self._pending_img = img
        self._pending_objects = current_objects

        return SceneAnalysisResult(
            is_change=True,
            detections=rfdetr_result.detections,
            ssim_score=ssim_result.ssim_score,
            execution_ms=(ssim_result.execution_ms or 0.0) + (rfdetr_result.execution_ms or 0.0)
        )

    async def commit(self):
        self._last_detected_objects = Counter(self._pending_objects)
        await self._ssim_detector.update_old_image(self._pending_img)