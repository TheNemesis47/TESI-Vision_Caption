from pydantic import BaseModel
from vision_caption.core.domain.audio import Audio

class CaptionResult(BaseModel):
    frame_id: int = 0
    caption: str
    audio: Audio
