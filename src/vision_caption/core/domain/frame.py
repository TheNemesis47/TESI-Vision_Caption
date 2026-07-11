from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class Format(str, Enum):
    JPEG = "JPEG"

class CaptionMode(str, Enum):
    AUTO = 'AUTO'
    POINTING = 'POINTING'

class PointingCoordinates(BaseModel):
    x: float
    y: float
    model_config = ConfigDict(frozen=True)

class Frame(BaseModel):
    frame_id: int = 0
    image_format: Format = Format.JPEG
    image_bytes: bytes
    caption_mode: CaptionMode
    timestamp: datetime = Field(default_factory=datetime.now)
    pointing_coordinates: PointingCoordinates | None = None
    model_config = ConfigDict(frozen=True)