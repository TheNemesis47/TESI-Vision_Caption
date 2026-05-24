from pydantic import BaseModel, ConfigDict

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    model_config = ConfigDict(frozen=True)

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: BoundingBox
    model_config = ConfigDict(frozen=True)