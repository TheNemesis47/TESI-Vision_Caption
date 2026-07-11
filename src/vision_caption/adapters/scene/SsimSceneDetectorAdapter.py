import time

from skimage.metrics import structural_similarity as ssim
import cv2

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult

class SsimSceneDetectorAdapter:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.old_img: cv2.typing.MatLike = None

    async def analyze(self, img: cv2.Mat) -> SceneAnalysisResult:
        t0 = time.perf_counter()

        # controllo se il vecchio frame c'e', in caso negativo vuol dire che e' il primo frame
        if self.old_img is None:
            # aggiorno l old img
            self.old_img = img
            return SceneAnalysisResult(
                is_change=True
            )

        # Se le dimensioni sono diverse, è sicuramente un cambio scena totale
        if self.old_img.shape != img.shape:
            self.old_img = img
            return SceneAnalysisResult(
                is_change=True,
                ssim_score=0.0, # Punteggio fittizio per indicare un cambio totale
                execution_ms=(time.perf_counter() - t0) * 1000
            )

        ssim_result: float = ssim(self.old_img, img)

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

    async def update_old_image(self, img: cv2.Mat):
        self.old_img = img