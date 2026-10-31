from typing import Protocol

from vision_caption.core.domain.pointing import PointingEvent
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages


class PointingCaptionGeneratorPort(Protocol):
    async def generate(
        self,
        event: PointingEvent,
        images: PointingImages,
        context: str | None = None,
    ) -> PointingCaption | None:
        """Genera e valida una risposta completa per un evento POINTING.

        ``context`` porta ciò che il sistema ricorda, per esempio le slide già
        descritte a lezione.
        """
        ...
