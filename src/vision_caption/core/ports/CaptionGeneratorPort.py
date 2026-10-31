from typing import Protocol
from vision_caption.core.domain.frame import Frame

class CaptionGeneratorPort(Protocol):
    async def generate(self, frame: Frame, context: str | None = None):
        """
        Riceve un Frame e genera una descrizione testuale (caption)
        utilizzando il VLM. ``context`` porta ciò che il sistema ricorda,
        per esempio le slide già descritte a lezione.
        """
        ...
