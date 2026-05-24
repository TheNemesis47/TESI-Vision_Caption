from typing import Protocol
from vision_caption.core.domain.audio import Audio

class SpeechSynthesizerPort(Protocol):
    async def synthesize(self, text: str, language: str = "it") -> Audio:
        ...