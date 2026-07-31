from typing import Protocol

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.hand_pose import HandPoseResult


class HandPoseEstimatorPort(Protocol):
    async def estimate(self, frame: Frame) -> HandPoseResult:
        """Estrae le osservazioni delle mani da un frame JPEG."""
        ...

    async def close(self) -> None:
        """Rilascia le risorse associate alla sessione di tracking."""
        ...
