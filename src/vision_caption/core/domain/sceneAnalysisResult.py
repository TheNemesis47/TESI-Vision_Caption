from pydantic import BaseModel, ConfigDict

from vision_caption.core.domain import detection


class SceneAnalysisResult(BaseModel):
    is_change: bool
    detections: tuple[detection.Detection, ...] = ()
    ssim_score: float | None = None
    execution_ms: float | None = None
    # Livello che ha soppresso il candidato quando is_change è False:
    # "ssim" per il filtro strutturale, "semantic" per il confronto fra le
    # classi rilevate. Serve a distinguere i due livelli in fase di misura.
    suppressed_by: str | None = None
    # Nitidezza del frame (varianza del laplaciano a 640 pixel di larghezza):
    # bassa per immagini mosse o sfocate, su cui il modello non legge nulla.
    sharpness: float | None = None
    model_config = ConfigDict(frozen=True)