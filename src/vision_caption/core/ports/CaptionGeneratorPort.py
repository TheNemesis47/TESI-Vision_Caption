from typing import Protocol
from vision_caption.core.domain.frame import Frame

class CaptionGeneratorPort(Protocol):
    async def generate(self, frame: Frame):
        """
        Riceve un Frame e genera una descrizione testuale (caption) 
        utilizzando il VLM.
        """
        ...
