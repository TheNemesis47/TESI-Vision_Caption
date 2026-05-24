import time

from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult

class SsimSceneDetectorAdapter:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.old_img: cv2.typing.MatLike = None

    async def analyze(self, new_frame: Frame) -> SceneAnalysisResult:
        t0 = time.perf_counter()
        new_nparr = np.frombuffer(new_frame.image_bytes, dtype=np.uint8)
        new_img = cv2.imdecode(new_nparr, cv2.IMREAD_GRAYSCALE)

        # controllo se il vecchio frame c'e', in caso negativo vuol dire che e' il primo frame
        if self.old_img is None:
            # aggiorno l old img
            self.old_img = new_img
            return SceneAnalysisResult(
                is_change=True
            )

        ssim_result: float = ssim(self.old_img, new_img)

        # aggiorno l old img
        self.old_img = new_img
        t1 = time.perf_counter()
        execution_time: float = t1 - t0
        if ssim_result < self.threshold:
            return SceneAnalysisResult(
                is_change=True,
                ssim_score=ssim_result,
                execution_ms=execution_time
            )
        return SceneAnalysisResult(
            is_change=False,
            ssim_score=ssim_result,
            execution_ms=execution_time
        )