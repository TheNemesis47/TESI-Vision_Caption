from pydantic import BaseModel, ConfigDict

from vision_caption.core.domain import detection


class SceneAnalysisResult(BaseModel):
    is_change: bool
    detections: tuple[detection.Detection, ...] = ()
    ssim_score: float | None = None
    execution_ms: float | None = None
    model_config = ConfigDict(frozen=True)