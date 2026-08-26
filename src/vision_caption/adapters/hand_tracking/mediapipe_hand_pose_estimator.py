import asyncio
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from time import monotonic_ns
from typing import Any

import cv2
import numpy as np

from vision_caption.core.domain.frame import Frame
from vision_caption.core.domain.hand_pose import (
    Handedness,
    HandObservation,
    HandPoseResult,
    ImageLandmark,
    WorldLandmark,
)
from vision_caption.core.ports.hand_pose_estimator_port import (
    HandPoseEstimatorPort,
)


def _stub_sounddevice_before_mediapipe_import() -> None:
    """Impedisce a MediaPipe di inizializzare PortAudio quando importa.

    `mediapipe.tasks.python` importa `sounddevice` per le task audio, e
    l'import di `sounddevice` esegue subito `Pa_Initialize()`. Su una macchina
    con PipeWire, PortAudio apre anche il backend JACK e avvia il data loop di
    PipeWire: da quel momento la creazione di `HandLandmarker` termina l'intero
    processo con SIGKILL, chiudendo il WebSocket senza alcun traceback.

    Il server non usa le task audio di MediaPipe, quindi al posto del modulo
    vero registriamo uno stub vuoto. Se `sounddevice` è già stato importato da
    qualcun altro non facciamo nulla: sostituirlo non annullerebbe comunque
    l'inizializzazione di PortAudio già avvenuta.
    """
    if "sounddevice" in sys.modules:
        return
    sys.modules["sounddevice"] = types.ModuleType("sounddevice")


@dataclass(frozen=True)
class MediaPipeHandPoseSettings:
    model_path: Path
    inference_max_side: int = 960
    num_hands: int = 1
    min_hand_detection_confidence: float = 0.60
    min_hand_presence_confidence: float = 0.60
    min_tracking_confidence: float = 0.60

    def __post_init__(self) -> None:
        if self.inference_max_side < 0:
            raise ValueError("inference_max_side non può essere negativo")
        if self.num_hands < 1:
            raise ValueError("num_hands deve essere almeno 1")
        confidences = (
            self.min_hand_detection_confidence,
            self.min_hand_presence_confidence,
            self.min_tracking_confidence,
        )
        if any(not 0.0 <= value <= 1.0 for value in confidences):
            raise ValueError("Le confidence MediaPipe devono essere fra 0 e 1")


def next_video_timestamp_ms(previous_timestamp_ms: int) -> int:
    current_timestamp_ms = monotonic_ns() // 1_000_000
    return max(previous_timestamp_ms + 1, current_timestamp_ms)


def _category_to_handedness(category: Any) -> Handedness:
    category_name = getattr(category, "category_name", None)
    if not isinstance(category_name, str):
        return Handedness.UNKNOWN
    try:
        return Handedness(category_name.upper())
    except ValueError:
        return Handedness.UNKNOWN


def convert_mediapipe_result(
    result: Any,
    *,
    frame_id: int,
) -> HandPoseResult:
    image_hands = getattr(result, "hand_landmarks", ()) or ()
    world_hands = getattr(result, "hand_world_landmarks", ()) or ()
    handedness_results = getattr(result, "handedness", ()) or ()
    observations: list[HandObservation] = []

    for hand_index, (image_hand, world_hand) in enumerate(
        zip(image_hands, world_hands, strict=False)
    ):
        if len(image_hand) != 21 or len(world_hand) != 21:
            continue

        categories = (
            handedness_results[hand_index]
            if hand_index < len(handedness_results)
            else ()
        )
        category = categories[0] if categories else None
        raw_score = getattr(category, "score", None)
        confidence = (
            float(raw_score)
            if isinstance(raw_score, (int, float))
            and 0.0 <= float(raw_score) <= 1.0
            else None
        )

        observations.append(
            HandObservation(
                handedness=_category_to_handedness(category),
                image_landmarks=tuple(
                    ImageLandmark(
                        x=float(landmark.x),
                        y=float(landmark.y),
                        z=float(landmark.z),
                    )
                    for landmark in image_hand
                ),
                world_landmarks=tuple(
                    WorldLandmark(
                        x=float(landmark.x),
                        y=float(landmark.y),
                        z=float(landmark.z),
                    )
                    for landmark in world_hand
                ),
                confidence=confidence,
            )
        )

    return HandPoseResult(frame_id=frame_id, hands=tuple(observations))


class MediaPipeHandPoseEstimator(HandPoseEstimatorPort):
    """Landmarker VIDEO creato soltanto al primo frame POINTING."""

    def __init__(self, settings: MediaPipeHandPoseSettings) -> None:
        self._settings = settings
        self._landmarker: Any | None = None
        self._mediapipe: Any | None = None
        self._previous_timestamp_ms = -1
        self._closed = False

    async def estimate(self, frame: Frame) -> HandPoseResult:
        if self._closed:
            raise RuntimeError("L'estimatore MediaPipe è già stato chiuso")
        return await asyncio.to_thread(self._estimate_sync, frame)

    def _estimate_sync(self, frame: Frame) -> HandPoseResult:
        if self._closed:
            raise RuntimeError("L'estimatore MediaPipe è già stato chiuso")

        landmarker = self._ensure_landmarker()
        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        bgr_frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if bgr_frame is None:
            raise ValueError("Il frame POINTING non contiene un JPEG valido")

        processing_frame = self._resize_for_inference(bgr_frame)
        rgb_frame = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2RGB)
        mediapipe_image = self._mediapipe.Image(
            image_format=self._mediapipe.ImageFormat.SRGB,
            data=rgb_frame,
        )

        timestamp_ms = next_video_timestamp_ms(self._previous_timestamp_ms)
        self._previous_timestamp_ms = timestamp_ms
        result = landmarker.detect_for_video(mediapipe_image, timestamp_ms)
        return convert_mediapipe_result(result, frame_id=frame.frame_id)

    def _resize_for_inference(self, frame: np.ndarray) -> np.ndarray:
        frame_height, frame_width = frame.shape[:2]
        longest_side = max(frame_width, frame_height)
        max_side = self._settings.inference_max_side
        if max_side == 0 or longest_side <= max_side:
            return frame

        scale = max_side / longest_side
        inference_width = max(1, round(frame_width * scale))
        inference_height = max(1, round(frame_height * scale))
        return cv2.resize(
            frame,
            (inference_width, inference_height),
            interpolation=cv2.INTER_AREA,
        )

    def _ensure_landmarker(self) -> Any:
        if self._landmarker is not None:
            return self._landmarker

        if not self._settings.model_path.is_file():
            raise FileNotFoundError(
                "Modello MediaPipe non trovato: "
                f"{self._settings.model_path}. Configura HAND_LANDMARKER_MODEL_PATH."
            )

        _stub_sounddevice_before_mediapipe_import()

        try:
            import mediapipe as mediapipe
            from mediapipe.tasks import python as mediapipe_python
            from mediapipe.tasks.python import vision
        except ImportError as error:
            raise RuntimeError(
                "MediaPipe non è installato. Installa una versione compatibile "
                "con l'interprete Python usato dal server."
            ) from error

        base_options = mediapipe_python.BaseOptions(
            model_asset_path=str(self._settings.model_path)
        )
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=self._settings.num_hands,
            min_hand_detection_confidence=(
                self._settings.min_hand_detection_confidence
            ),
            min_hand_presence_confidence=(
                self._settings.min_hand_presence_confidence
            ),
            min_tracking_confidence=self._settings.min_tracking_confidence,
        )
        self._mediapipe = mediapipe
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        return self._landmarker

    async def close(self) -> None:
        if self._landmarker is None:
            self._closed = True
            return
        await asyncio.to_thread(self._close_sync)

    def _close_sync(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None
            self._mediapipe = None
