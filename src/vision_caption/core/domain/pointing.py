from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from vision_caption.core.domain.hand_pose import Handedness


class NormalizedPoint(BaseModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)

    model_config = ConfigDict(frozen=True)


class FingerAngles(BaseModel):
    pip: float = Field(ge=0.0, le=180.0)
    dip: float = Field(ge=0.0, le=180.0)

    @property
    def extension(self) -> float:
        """Un dito è davvero esteso solo se PIP e DIP sono entrambi aperti."""
        return min(self.pip, self.dip)

    model_config = ConfigDict(frozen=True)


class PointingVector(BaseModel):
    origin: NormalizedPoint
    direction_x: float = Field(ge=-1.0, le=1.0)
    direction_y: float = Field(ge=-1.0, le=1.0)

    model_config = ConfigDict(frozen=True)


class PointingRay(BaseModel):
    start: NormalizedPoint
    end: NormalizedPoint

    model_config = ConfigDict(frozen=True)


class PointingOverlayState(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"


class PointingOverlay(BaseModel):
    handedness: Handedness
    ray: PointingRay
    state: PointingOverlayState
    confirmation_progress: float = Field(ge=0.0, le=1.0)

    model_config = ConfigDict(frozen=True)


class PointingEvent(BaseModel):
    handedness: Handedness
    ray: PointingRay
    frame_id: int

    model_config = ConfigDict(frozen=True)
