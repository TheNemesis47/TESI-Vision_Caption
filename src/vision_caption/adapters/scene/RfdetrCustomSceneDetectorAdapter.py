import time
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
import rfdetr
from loguru import logger

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.sceneAnalysisResult import SceneAnalysisResult
from vision_caption.core.domain.detection import BoundingBox, Detection


class RfdetrCustomSceneDetectorAdapter:
    """Adapter RF-DETR per un checkpoint addestrato su dataset custom.

    A differenza di ``RfdetrSceneDetectorAdapter`` — che riceve un modello COCO
    già costruito (``RFDETRMedium``) — questo adapter carica un checkpoint
    fine-tunato (es. ``checkpoint_best_total.pth``) tramite
    ``rfdetr.from_checkpoint``. Quella funzione deduce automaticamente dai
    metadati salvati nel checkpoint sia la variante del modello
    (Nano/Small/Medium/Large) sia il ``num_classes``, quindi non serve
    conoscerli a priori.

    I nomi delle classi vengono presi da quelli salvati nel checkpoint; se il
    checkpoint non li contiene (capita con alcuni run di training), passa
    ``class_names`` esplicitamente: devono essere nello stesso ordine degli id
    del dataset COCO usato per l'addestramento.
    """

    def __init__(self, model: rfdetr.RFDETR, threshold: float = 0.5):
        self.model = model
        self.threshold = threshold

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: str,
        device: str = "cuda",
        threshold: float = 0.5,
        class_names: list[str] | None = None,
        optimize: bool = True,
    ) -> "RfdetrCustomSceneDetectorAdapter":
        """Costruisce l'adapter caricando un checkpoint custom da disco.

        Args:
            checkpoint_path: percorso al file ``.pth`` (es. checkpoint_best_total.pth).
            device: ``"cuda"`` (GPU AMD/NVIDIA) o ``"cpu"``.
            threshold: soglia di confidenza minima per tenere una detection.
            class_names: opzionale, nomi classi nell'ordine degli id del dataset.
            optimize: se True applica ``optimize_for_inference`` (compile su GPU, fp16).
        """
        path = Path(checkpoint_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(
                f"Checkpoint RF-DETR non trovato: {path}. "
                f"Verifica il percorso o la variabile d'ambiente RFDETR_CHECKPOINT."
            )

        kwargs: dict = {"device": device}
        if class_names is not None:
            kwargs["class_names"] = class_names

        logger.info(f"Loading custom RF-DETR checkpoint from: {path} (device={device})")
        model = rfdetr.from_checkpoint(str(path), **kwargs)

        if optimize:
            use_gpu = device.lower() != "cpu"
            inference_dtype = "float16" if use_gpu else "float32"
            logger.info(
                f"Optimizing custom RF-DETR for inference "
                f"(compile={use_gpu}, batch_size=1, dtype={inference_dtype})..."
            )
            model.optimize_for_inference(
                compile=use_gpu,
                batch_size=1,
                dtype=inference_dtype,
            )

        return cls(model=model, threshold=threshold)

    async def analyze(self, frame: Frame) -> SceneAnalysisResult:
        t0 = time.perf_counter()
        nparr = np.frombuffer(frame.image_bytes, np.uint8)
        image = cv2.cvtColor(cv2.imdecode(nparr, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

        sv_detections: sv.Detections = self.model.predict(image, self.threshold)

        # Per un checkpoint fine-tunato predict popola data["class_name"];
        # se manca (checkpoint senza nomi) ripieghiamo sull'id numerico.
        class_names = sv_detections.data.get("class_name")

        detections: list[Detection] = []
        for i, (box, conf) in enumerate(zip(sv_detections.xyxy, sv_detections.confidence)):
            xmin, ymin, xmax, ymax = box
            if class_names is not None:
                name = str(class_names[i])
            else:
                name = str(sv_detections.class_id[i])
            detections.append(
                Detection(
                    class_name=name,
                    confidence=float(conf),
                    bbox=BoundingBox(
                        x_min=float(xmin),
                        y_min=float(ymin),
                        x_max=float(xmax),
                        y_max=float(ymax),
                    ),
                )
            )

        execution_time = (time.perf_counter() - t0) * 1000
        return SceneAnalysisResult(
            is_change=True,
            detections=tuple(detections),
            execution_ms=execution_time,
        )

    async def commit(self):
        # Questo detector è stateless: nessun keyframe/oggetto da confermare.
        ...
