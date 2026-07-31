from dataclasses import dataclass, field
from math import isfinite, sqrt

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


@dataclass(frozen=True)
class GestureRecognizerSettings:
    index_activation_min_angle_deg: float = 145.0
    index_hold_min_angle_deg: float = 135.0
    other_finger_activation_max_angle_deg: float = 125.0
    other_finger_hold_max_angle_deg: float = 140.0
    thumb_activation_max_palm_ratio: float = 1.25
    thumb_hold_max_palm_ratio: float = 1.45
    angle_ema_alpha: float = 0.35
    ray_ema_alpha: float = 0.25
    confirmation_seconds: float = 8.0 / 30.0
    release_seconds: float = 5.0 / 30.0
    min_pointing_vector_length: float = 0.0125

    def __post_init__(self) -> None:
        if not 0.0 < self.angle_ema_alpha <= 1.0:
            raise ValueError("angle_ema_alpha deve essere compreso fra 0 e 1")
        if not 0.0 < self.ray_ema_alpha <= 1.0:
            raise ValueError("ray_ema_alpha deve essere compreso fra 0 e 1")
        if self.confirmation_seconds < 0.0 or self.release_seconds < 0.0:
            raise ValueError("Le soglie temporali non possono essere negative")
        if self.min_pointing_vector_length < 0.0:
            raise ValueError("La lunghezza minima del vettore non può essere negativa")


@dataclass(frozen=True)
class PointingActivation:
    handedness: Handedness
    ray: PointingRay


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
    release_since: float | None = None
    active: bool = False

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
                    pip=ema(
                        previous.pip,
                        current.pip,
                        self.settings.angle_ema_alpha,
                    ),
                    dip=ema(
                        previous.dip,
                        current.dip,
                        self.settings.angle_ema_alpha,
                    ),
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
            smoothed = ema(
                previous,
                current_ratio,
                self.settings.angle_ema_alpha,
            )
        self.filtered_thumb_palm_ratio = smoothed
        return smoothed

    def smooth_vector(self, current: PointingVector) -> PointingVector:
        previous = self.filtered_vector
        if previous is None:
            self.filtered_vector = current
            return current

        origin_x = ema(
            previous.origin.x,
            current.origin.x,
            self.settings.ray_ema_alpha,
        )
        origin_y = ema(
            previous.origin.y,
            current.origin.y,
            self.settings.ray_ema_alpha,
        )
        direction_x = ema(
            previous.direction_x,
            current.direction_x,
            self.settings.ray_ema_alpha,
        )
        direction_y = ema(
            previous.direction_y,
            current.direction_y,
            self.settings.ray_ema_alpha,
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
        """Restituisce True una sola volta quando la gesture diventa attiva."""
        if pose_matches:
            self.release_since = None
            if self.active:
                return False

            if self.candidate_since is None:
                self.candidate_since = timestamp
            if (
                timestamp - self.candidate_since
                >= self.settings.confirmation_seconds
            ):
                self.candidate_since = None
                self.active = True
                return True
            return False

        self.candidate_since = None
        if not self.active:
            self.release_since = None
            return False

        if self.release_since is None:
            self.release_since = timestamp
        if timestamp - self.release_since >= self.settings.release_seconds:
            self.release_since = None
            self.active = False
        return False

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
            tracker_key = f"{hand.handedness.value}:{hand_index}"
            seen_trackers.add(tracker_key)
            tracker = self._trackers.setdefault(
                tracker_key,
                _GestureTracker(settings=self._settings),
            )

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
            just_activated = tracker.update_activation(pose_matches, timestamp)
            if just_activated and ray is not None:
                activations.append(
                    PointingActivation(
                        handedness=hand.handedness,
                        ray=ray,
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

    def reset(self) -> None:
        self._trackers.clear()
