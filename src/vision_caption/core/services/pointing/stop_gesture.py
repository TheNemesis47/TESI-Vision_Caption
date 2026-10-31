"""Gesto di stop: la mano aperta davanti alla fotocamera zittisce la voce.

A lezione il sistema può parlare sopra il docente. Il gesto più naturale per
farlo tacere è il palmo aperto, il segno dello stop: quattro dita tese, con
il pollice libero. Si distingue dal puntamento, che vuole indice teso e le
altre dita piegate.

Il gesto va tenuto un attimo (hold_seconds) perché una mano che passa davanti
all'obiettivo non basti, e dopo uno stop c'è una pausa (cooldown_seconds)
prima di poterne riconoscere un altro.
"""

from dataclasses import dataclass

from vision_caption.core.domain.hand_pose import HandObservation
from vision_caption.core.services.pointing.pointing_geometry import (
    calculate_finger_angles,
)


OPEN_PALM_FINGERS = ("INDICE", "MEDIO", "ANULARE", "MIGNOLO")


@dataclass(frozen=True)
class StopGestureSettings:
    # Un dito teso ha articolazioni quasi diritte: 180 gradi è dritto.
    min_finger_extension_deg: float = 150.0
    hold_seconds: float = 0.4
    cooldown_seconds: float = 2.0

    def __post_init__(self) -> None:
        if not 0.0 < self.min_finger_extension_deg <= 180.0:
            raise ValueError("min_finger_extension_deg deve stare fra 0 e 180")
        if self.hold_seconds < 0 or self.cooldown_seconds < 0:
            raise ValueError("I tempi del gesto di stop non possono essere negativi")


def is_open_palm(hand: HandObservation, settings: StopGestureSettings) -> bool:
    angles = calculate_finger_angles(hand.world_landmarks)
    return all(
        finger in angles
        and angles[finger].extension >= settings.min_finger_extension_deg
        for finger in OPEN_PALM_FINGERS
    )


class StopGestureDetector:
    def __init__(self, settings: StopGestureSettings | None = None) -> None:
        self._settings = settings or StopGestureSettings()
        self._palm_since: float | None = None
        self._last_stop: float | None = None
        self._armed = True

    def palm_visible(self, hands: tuple[HandObservation, ...]) -> bool:
        return any(is_open_palm(hand, self._settings) for hand in hands)

    def update(self, hands: tuple[HandObservation, ...], timestamp: float) -> bool:
        """Vero una volta sola, quando il palmo è stato tenuto abbastanza."""
        if not self.palm_visible(hands):
            self._palm_since = None
            # Abbassare la mano riarma il gesto: tenerla alzata non ripete lo stop.
            self._armed = True
            return False

        if self._palm_since is None:
            self._palm_since = timestamp
        in_cooldown = (
            self._last_stop is not None
            and timestamp - self._last_stop < self._settings.cooldown_seconds
        )
        held = timestamp - self._palm_since >= self._settings.hold_seconds
        if self._armed and held and not in_cooldown:
            self._last_stop = timestamp
            self._armed = False
            return True
        return False

    def reset(self) -> None:
        self._palm_since = None
        self._armed = True
