from typing import Protocol
from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult


class SceneDetectorPort(Protocol):
    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        ...