from dataclasses import dataclass
from typing import Protocol

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.pointing import PointingEvent


@dataclass(frozen=True)
class PointingImages:
    context_jpeg: bytes
    focus_jpeg: bytes
    clean_jpeg: bytes


class PointingImagePreparerPort(Protocol):
    async def prepare(
        self,
        frame: Frame,
        event: PointingEvent,
    ) -> PointingImages:
        """Prepara contesto, focus del corridoio e immagine pulita."""
        ...
