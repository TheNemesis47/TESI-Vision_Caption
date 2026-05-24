from enum import Enum

from pydantic import BaseModel, ConfigDict


class AudioFormat(str, Enum):
    WAV = "wav"
    OPUS = "opus"

class Audio(BaseModel):
    audio_format: AudioFormat
    audio_bytes: bytes
    audio_duration: float
    model_config = ConfigDict(frozen=True)