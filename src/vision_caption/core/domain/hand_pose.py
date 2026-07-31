from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class HandLandmark(int, Enum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


class Handedness(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UNKNOWN = "UNKNOWN"


class ImageLandmark(BaseModel):
    x: float
    y: float
    z: float

    model_config = ConfigDict(frozen=True)


class WorldLandmark(BaseModel):
    x: float
    y: float
    z: float

    model_config = ConfigDict(frozen=True)


class HandObservation(BaseModel):
    handedness: Handedness
    image_landmarks: tuple[ImageLandmark, ...] = Field(
        min_length=21,
        max_length=21,
    )
    world_landmarks: tuple[WorldLandmark, ...] = Field(
        min_length=21,
        max_length=21,
    )
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    model_config = ConfigDict(frozen=True)


class HandPoseResult(BaseModel):
    frame_id: int
    hands: tuple[HandObservation, ...] = ()

    model_config = ConfigDict(frozen=True)
