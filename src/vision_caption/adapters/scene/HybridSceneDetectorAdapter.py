from loguru import logger

from vision_caption.adapters.scene.RfdetrSceneDetectorAdapter import RfdetrSceneDetectorAdapter
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import SsimSceneDetectorAdapter
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult


class HybridSceneDetectorAdapter:
    def __init__(self, ssim_detector: SsimSceneDetectorAdapter, rfdetr_detector: RfdetrSceneDetectorAdapter):
        self._ssim_detector = ssim_detector
        self._rfdetr_detector = rfdetr_detector

    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        # 1. Analisi rapida con SSIM
        ssim_result = await self._ssim_detector.analyze(frame)
        
        # 2. Se non c'è, early exit
        if not ssim_result.is_change:
            return SceneAnalysisResult(
                is_change=False,
                detections=(),
                ssim_score=ssim_result.ssim_score,
                execution_ms=ssim_result.execution_ms
            )
            
        # 3. Se c'è, eseguiamo RF-DETR
        logger.info(
            "SSIM detected structural change",
            ssim_score=ssim_result.ssim_score
        )
        
        rfdetr_result = await self._rfdetr_detector.analyze(frame)
        
        # Calcolo del tempo totale di esecuzione
        total_execution_time = (ssim_result.execution_ms or 0.0) + (rfdetr_result.execution_ms or 0.0)
        
        return SceneAnalysisResult(
            is_change=True,
            detections=rfdetr_result.detections,
            ssim_score=ssim_result.ssim_score,
            execution_ms=total_execution_time
        )