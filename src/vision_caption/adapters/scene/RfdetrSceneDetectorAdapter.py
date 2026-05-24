import time

import cv2
import rfdetr
from transformers import PretrainedFSMTModel
import numpy as np
import supervision as sv

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.domain.detection import BoundingBox, Detection

class RfdetrSceneDetectorAdapter:
    def __init__(self, model: rfdetr.RFDETRMedium):
        self.model = model

    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        t0 = time.perf_counter()
        nparr = np.frombuffer(frame.image_bytes, np.uint8)
        image = cv2.cvtColor(cv2.imdecode(nparr, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        sv_detections: sv.Detections = self.model.predict(image, 0.6)
        detections: list[Detection] = []
        for box, conf, class_name in zip(sv_detections.xyxy, sv_detections.confidence, sv_detections.data["class_name"]):
            xmin, ymin, xmax, ymax = box
            bbox = BoundingBox(x_min=xmin,y_min=ymin,x_max=xmax,y_max=ymax)
            core_detection: Detection = Detection(class_name=class_name, confidence=conf, bbox=bbox)
            detections.append(core_detection)
        t1 = time.perf_counter()
        execution_time = (t1 - t0) * 1000
        return SceneAnalysisResult(
            is_change=True,
            detections=tuple(detections),
            execution_ms=execution_time
        )