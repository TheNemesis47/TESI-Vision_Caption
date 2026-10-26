from dataclasses import dataclass, field
from math import acos, degrees, isfinite, sqrt

from loguru import logger

from vision_caption.core.domain.hand_pose import HandObservation, Handedness
from vision_caption.core.domain.pointing import (
    FingerAngles,
    NormalizedPoint,
    PointingOverlay,
    PointingOverlayState,
    PointingRay,
    PointingVector,
)
from vision_caption.core.services.pointing.pointing_geometry import (
    calculate_finger_angles,
    calculate_pointing_vector,
    calculate_thumb_palm_ratio,
    ema,
    project_vector_to_frame,
)


OTHER_FINGERS = ("MEDIO", "ANULARE", "MIGNOLO")

# Gli alpha EMA sono tarati per fotogramma a questa cadenza. Il client invia
# molti meno fotogrammi, quindi l'alpha va riscalato sul tempo reale trascorso.
EMA_REFERENCE_FPS = 30.0


def time_scaled_alpha(alpha: float, elapsed_seconds: float) -> float:
    """Converte un alpha per fotogramma a 30 fps nell'alpha dell'intervallo reale.

    Senza questa correzione, a 4-5 fps la media impiega secondi invece di
    frazioni di secondo a seguire la mano, e la posa non supera mai le soglie
    prima che l'utente rinunci.
    """
    if alpha >= 1.0:
        return 1.0
    frames = max(0.0, elapsed_seconds) * EMA_REFERENCE_FPS
    return 1.0 - (1.0 - alpha) ** frames


def vector_moved(
    reference: PointingVector,
    current: PointingVector,
    *,
    min_angle_deg: float,
    min_shift_ratio: float,
) -> bool:
    """Indica se il raggio ha cambiato direzione o si è spostato abbastanza."""
    cosine = (
        reference.direction_x * current.direction_x
        + reference.direction_y * current.direction_y
    )
    angle = degrees(acos(max(-1.0, min(1.0, cosine))))
    shift = sqrt(
        (reference.origin.x - current.origin.x) ** 2
        + (reference.origin.y - current.origin.y) ** 2
    )
    return angle >= min_angle_deg or shift >= min_shift_ratio


@dataclass(frozen=True)
class GestureRecognizerSettings:
    index_activation_min_angle_deg: float = 135.0
    index_hold_min_angle_deg: float = 120.0
    other_finger_activation_max_angle_deg: float = 140.0
    other_finger_hold_max_angle_deg: float = 155.0
    thumb_activation_max_palm_ratio: float = 1.6
    thumb_hold_max_palm_ratio: float = 1.9
    angle_ema_alpha: float = 0.35
    ray_ema_alpha: float = 0.25
    confirmation_seconds: float = 0.15
    release_seconds: float = 5.0 / 30.0
    min_pointing_vector_length: float = 0.0125
    retarget_enabled: bool = True
    retarget_min_angle_deg: float = 20.0
    retarget_min_shift_ratio: float = 0.15
    retarget_stable_angle_deg: float = 8.0
    retarget_stable_shift_ratio: float = 0.05

    def __post_init__(self) -> None:
        if not 0.0 < self.angle_ema_alpha <= 1.0:
            raise ValueError("angle_ema_alpha deve essere compreso fra 0 e 1")
        if not 0.0 < self.ray_ema_alpha <= 1.0:
            raise ValueError("ray_ema_alpha deve essere compreso fra 0 e 1")
        if self.confirmation_seconds < 0.0 or self.release_seconds < 0.0:
            raise ValueError("Le soglie temporali non possono essere negative")
        if self.min_pointing_vector_length < 0.0:
            raise ValueError("La lunghezza minima del vettore non può essere negativa")
        if (
            self.retarget_min_angle_deg <= self.retarget_stable_angle_deg
            or self.retarget_min_shift_ratio <= self.retarget_stable_shift_ratio
        ):
            raise ValueError(
                "Le soglie di cambio bersaglio devono superare quelle di stabilità"
            )


@dataclass(frozen=True)
class PointingActivation:
    handedness: Handedness
    ray: PointingRay
    tracker_key: str = ""
    # True quando il dito, rimasto puntato, si è spostato su un altro oggetto.
    retarget: bool = False


@dataclass(frozen=True)
class PointingRecognitionResult:
    activations: tuple[PointingActivation, ...] = ()
    overlays: tuple[PointingOverlay, ...] = ()


def is_pointing_pose(
    angles: dict[str, FingerAngles],
    thumb_palm_ratio: float,
    *,
    active: bool,
    settings: GestureRecognizerSettings,
) -> bool:
    """Classifica la posa usando isteresi fra attivazione e mantenimento."""
    required_fingers = {"INDICE", *OTHER_FINGERS}
    if not required_fingers.issubset(angles):
        return False

    if active:
        index_min_angle = settings.index_hold_min_angle_deg
        other_finger_max_angle = settings.other_finger_hold_max_angle_deg
        thumb_max_ratio = settings.thumb_hold_max_palm_ratio
    else:
        index_min_angle = settings.index_activation_min_angle_deg
        other_finger_max_angle = settings.other_finger_activation_max_angle_deg
        thumb_max_ratio = settings.thumb_activation_max_palm_ratio

    index_is_extended = angles["INDICE"].extension >= index_min_angle
    other_fingers_are_folded = all(
        angles[finger_name].extension <= other_finger_max_angle
        for finger_name in OTHER_FINGERS
    )
    thumb_is_near_palm = thumb_palm_ratio <= thumb_max_ratio
    return index_is_extended and other_fingers_are_folded and thumb_is_near_palm


@dataclass
class _GestureTracker:
    settings: GestureRecognizerSettings
    filtered_angles: dict[str, FingerAngles] = field(default_factory=dict)
    filtered_thumb_palm_ratio: float | None = None
    filtered_vector: PointingVector | None = None
    candidate_since: float | None = None
    candidate_miss_since: float | None = None
    release_since: float | None = None
    active: bool = False
    # Raggio dell'ultima attivazione: tenendo il dito puntato e spostandolo
    # su un altro oggetto si ottiene una nuova descrizione senza ripuntare.
    anchor: PointingVector | None = None
    previous_anchor: PointingVector | None = None
    retarget_reference: PointingVector | None = None
    retarget_since: float | None = None
    last_timestamp: float | None = None
    angle_alpha: float = 1.0
    ray_alpha: float = 1.0

    def advance(self, timestamp: float) -> None:
        """Riscala gli alpha EMA sull'intervallo dal fotogramma precedente."""
        if self.last_timestamp is not None:
            elapsed = timestamp - self.last_timestamp
            self.angle_alpha = time_scaled_alpha(
                self.settings.angle_ema_alpha,
                elapsed,
            )
            self.ray_alpha = time_scaled_alpha(
                self.settings.ray_ema_alpha,
                elapsed,
            )
        self.last_timestamp = timestamp

    def smooth_angles(
        self,
        current_angles: dict[str, FingerAngles],
    ) -> dict[str, FingerAngles]:
        smoothed: dict[str, FingerAngles] = {}
        for finger_name, current in current_angles.items():
            previous = self.filtered_angles.get(finger_name)
            if previous is None:
                smoothed[finger_name] = current
            else:
                smoothed[finger_name] = FingerAngles(
                    pip=ema(previous.pip, current.pip, self.angle_alpha),
                    dip=ema(previous.dip, current.dip, self.angle_alpha),
                )
        self.filtered_angles = smoothed
        return smoothed

    def smooth_thumb_palm_ratio(self, current_ratio: float) -> float:
        previous = self.filtered_thumb_palm_ratio
        if (
            previous is None
            or not isfinite(previous)
            or not isfinite(current_ratio)
        ):
            smoothed = current_ratio
        else:
            smoothed = ema(previous, current_ratio, self.angle_alpha)
        self.filtered_thumb_palm_ratio = smoothed
        return smoothed

    def smooth_vector(self, current: PointingVector) -> PointingVector:
        previous = self.filtered_vector
        if previous is None:
            self.filtered_vector = current
            return current

        origin_x = ema(previous.origin.x, current.origin.x, self.ray_alpha)
        origin_y = ema(previous.origin.y, current.origin.y, self.ray_alpha)
        direction_x = ema(
            previous.direction_x,
            current.direction_x,
            self.ray_alpha,
        )
        direction_y = ema(
            previous.direction_y,
            current.direction_y,
            self.ray_alpha,
        )
        direction_length = sqrt(direction_x * direction_x + direction_y * direction_y)
        if direction_length == 0:
            return previous

        self.filtered_vector = PointingVector(
            origin=NormalizedPoint(x=origin_x, y=origin_y),
            direction_x=direction_x / direction_length,
            direction_y=direction_y / direction_length,
        )
        return self.filtered_vector

    def update_activation(self, pose_matches: bool, timestamp: float) -> bool:
        """Restituisce True quando la gesture diventa attiva o cambia bersaglio."""
        if pose_matches:
            self.release_since = None
            self.candidate_miss_since = None
            if self.active:
                return self._update_retarget(timestamp)

            if self.candidate_since is None:
                self.candidate_since = timestamp
            if (
                timestamp - self.candidate_since
                >= self.settings.confirmation_seconds
            ):
                self.candidate_since = None
                self.active = True
                self._move_anchor(None)
                return True
            return False

        if not self.active:
            self.release_since = None
            self._tolerate_candidate_miss(timestamp)
            return False

        if self.release_since is None:
            self.release_since = timestamp
        if timestamp - self.release_since >= self.settings.release_seconds:
            self.release_since = None
            self.active = False
            self.anchor = None
            self._clear_retarget()
        return False

    def _move_anchor(self, previous: PointingVector | None) -> None:
        self.previous_anchor = previous
        self.anchor = self.filtered_vector
        self._clear_retarget()

    def _clear_retarget(self) -> None:
        self.retarget_reference = None
        self.retarget_since = None

    def _update_retarget(self, timestamp: float) -> bool:
        """Riattiva quando il raggio si sposta e poi resta fermo sul nuovo punto.

        Lo spostamento deve superare le soglie di cambio bersaglio rispetto
        all'ultima attivazione, poi il raggio deve restare entro le soglie di
        stabilità per confirmation_seconds: un dito che passa sopra gli oggetti
        non li descrive tutti.
        """
        settings = self.settings
        current = self.filtered_vector
        if not settings.retarget_enabled or current is None or self.anchor is None:
            return False

        if not vector_moved(
            self.anchor,
            current,
            min_angle_deg=settings.retarget_min_angle_deg,
            min_shift_ratio=settings.retarget_min_shift_ratio,
        ):
            self._clear_retarget()
            return False

        if self.retarget_reference is None or vector_moved(
            self.retarget_reference,
            current,
            min_angle_deg=settings.retarget_stable_angle_deg,
            min_shift_ratio=settings.retarget_stable_shift_ratio,
        ):
            self.retarget_reference = current
            self.retarget_since = timestamp
            return False

        assert self.retarget_since is not None
        if timestamp - self.retarget_since < settings.confirmation_seconds:
            return False

        self._move_anchor(self.anchor)
        return True

    def cancel_activation(self) -> None:
        """Annulla l'ultima attivazione che il cooldown non ha lasciato passare.

        Così il gesto ancora mantenuto riprova al termine del cooldown invece
        di restare in silenzio fino a un nuovo puntamento.
        """
        if self.previous_anchor is None:
            self.active = False
            self.anchor = None
        else:
            self.anchor = self.previous_anchor
            self.previous_anchor = None
        self._clear_retarget()

    def _tolerate_candidate_miss(self, timestamp: float) -> None:
        """Un fotogramma storto non azzera la conferma in corso.

        Con pochi fotogrammi al secondo una sola stima sbagliata di MediaPipe
        bastava a ripartire da zero. La conferma cade soltanto se la posa
        resta non valida per release_seconds, come avviene per il rilascio.
        """
        if self.candidate_since is None:
            return
        if self.candidate_miss_since is None:
            self.candidate_miss_since = timestamp
        if timestamp - self.candidate_miss_since >= self.settings.release_seconds:
            self.candidate_since = None
            self.candidate_miss_since = None

    def confirmation_progress(self, timestamp: float) -> float:
        if self.active:
            return 1.0
        if self.candidate_since is None:
            return 0.0
        if self.settings.confirmation_seconds == 0.0:
            return 1.0
        return max(
            0.0,
            min(
                1.0,
                (timestamp - self.candidate_since)
                / self.settings.confirmation_seconds,
            ),
        )


class PointingGestureRecognizer:
    """Mantiene lo stato temporale delle gesture per una singola sessione."""

    def __init__(
        self,
        settings: GestureRecognizerSettings | None = None,
    ) -> None:
        self._settings = settings or GestureRecognizerSettings()
        self._trackers: dict[str, _GestureTracker] = {}

    def update(
        self,
        hands: tuple[HandObservation, ...],
        *,
        timestamp: float,
    ) -> PointingRecognitionResult:
        activations: list[PointingActivation] = []
        overlays: list[PointingOverlay] = []
        seen_trackers: set[str] = set()

        for hand_index, hand in enumerate(hands):
            # La chiave non include la lateralità: con la mano inclinata
            # MediaPipe la scambia spesso fra un fotogramma e l'altro, e ogni
            # scambio creava un tracker nuovo azzerando la conferma.
            tracker_key = str(hand_index)
            seen_trackers.add(tracker_key)
            tracker = self._trackers.setdefault(
                tracker_key,
                _GestureTracker(settings=self._settings),
            )
            tracker.advance(timestamp)

            angles = tracker.smooth_angles(
                calculate_finger_angles(hand.world_landmarks)
            )
            thumb_ratio = tracker.smooth_thumb_palm_ratio(
                calculate_thumb_palm_ratio(hand.world_landmarks)
            )
            raw_vector = calculate_pointing_vector(
                hand.image_landmarks,
                min_length=self._settings.min_pointing_vector_length,
            )

            ray: PointingRay | None = None
            if raw_vector is not None:
                ray = project_vector_to_frame(tracker.smooth_vector(raw_vector))

            pose_matches = (
                ray is not None
                and is_pointing_pose(
                    angles,
                    thumb_ratio,
                    active=tracker.active,
                    settings=self._settings,
                )
            )
            logger.debug(
                "POINTING posa: indice={:.0f} medio={:.0f} anulare={:.0f} "
                "mignolo={:.0f} pollice={:.2f} raggio={} attiva={} valida={}",
                angles["INDICE"].extension,
                angles["MEDIO"].extension,
                angles["ANULARE"].extension,
                angles["MIGNOLO"].extension,
                thumb_ratio,
                ray is not None,
                tracker.active,
                pose_matches,
            )
            just_activated = tracker.update_activation(pose_matches, timestamp)
            if just_activated and ray is not None:
                activations.append(
                    PointingActivation(
                        handedness=hand.handedness,
                        ray=ray,
                        tracker_key=tracker_key,
                        retarget=tracker.previous_anchor is not None,
                    )
                )

            if ray is not None and (pose_matches or tracker.active):
                state = (
                    PointingOverlayState.ACTIVE
                    if tracker.active
                    else PointingOverlayState.CANDIDATE
                )
                overlays.append(
                    PointingOverlay(
                        handedness=hand.handedness,
                        ray=ray,
                        state=state,
                        confirmation_progress=tracker.confirmation_progress(
                            timestamp
                        ),
                    )
                )

        for tracker_key, tracker in self._trackers.items():
            if tracker_key not in seen_trackers:
                tracker.update_activation(False, timestamp)

        return PointingRecognitionResult(
            activations=tuple(activations),
            overlays=tuple(overlays),
        )

    def cancel(self, activation: PointingActivation) -> None:
        tracker = self._trackers.get(activation.tracker_key)
        if tracker is not None:
            tracker.cancel_activation()

    def reset(self) -> None:
        self._trackers.clear()
