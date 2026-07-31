from pydantic import BaseModel, ConfigDict, Field


class PointingCandidate(BaseModel):
    label: str
    position_along_ray: float = Field(ge=0.0, le=1.0)
    intersects_centerline: bool
    confidence: float = Field(ge=0.0, le=1.0)

    model_config = ConfigDict(frozen=True)

class PointingCaption(BaseModel):
    target: str | None
    description: str
    visible_text: str | None
    text_confidence: float = Field(ge=0.0, le=1.0)
    text_complete: bool
    confidence: float = Field(ge=0.0, le=1.0)
    candidates: tuple[PointingCandidate, ...] = tuple()
    alternatives: tuple[str, ...] = tuple()
    needs_repointing: bool
    needs_closer_view: bool

    model_config = ConfigDict(frozen=True)