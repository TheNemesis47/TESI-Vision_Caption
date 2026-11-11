"""Gesto di cambio modalità: due dita a V passano da automatica a puntamento.

Chi non vede non può cercare un pulsante sullo schermo mentre cammina o
mentre segue una lezione. Il gesto è l'indice e il medio tesi, anulare e
mignolo piegati - il segno della vittoria - perché si distingue dagli altri
due gesti già in uso senza ambiguità: il puntamento vuole il solo indice
teso, lo stop vuole tutte e quattro le dita tese.

Vale nei due versi: in automatica porta al puntamento, nel puntamento
riporta in automatica. Il riconoscitore è uno solo per connessione, così la
mano tenuta alzata dopo il primo scatto non fa rimbalzare le modalità: per
scattare di nuovo bisogna abbassarla, e comunque dopo la pausa di cooldown.
"""

from dataclasses import dataclass

from vision_caption.core.domain.hand_pose import HandObservation
from vision_caption.core.services.pointing.pointing_geometry import (
    calculate_finger_angles,
)


EXTENDED_FINGERS = ("INDICE", "MEDIO")
FOLDED_FINGERS = ("ANULARE", "MIGNOLO")


@dataclass(frozen=True)
class ModeGestureSettings:
    # Un dito teso ha le articolazioni quasi diritte; uno piegato sta sotto.
    min_extended_deg: float = 150.0
    max_folded_deg: float = 125.0
    # Più lungo dello stop: cambiare modalità per sbaglio costa di più che
    # zittire la voce per sbaglio.
    hold_seconds: float = 0.7
    cooldown_seconds: float = 3.0

    def __post_init__(self) -> None:
        if not 0.0 < self.max_folded_deg < self.min_extended_deg <= 180.0:
            raise ValueError(
                "Le soglie del gesto di modalità devono stare fra 0 e 180, "
                "con il dito piegato sotto quello teso"
            )
        if self.hold_seconds < 0 or self.cooldown_seconds < 0:
            raise ValueError("I tempi del gesto di modalità non possono essere negativi")


def is_two_finger_sign(hand: HandObservation, settings: ModeGestureSettings) -> bool:
    angles = calculate_finger_angles(hand.world_landmarks)
    if any(finger not in angles for finger in EXTENDED_FINGERS + FOLDED_FINGERS):
        return False
    return all(
        angles[finger].extension >= settings.min_extended_deg
        for finger in EXTENDED_FINGERS
    ) and all(
        angles[finger].extension <= settings.max_folded_deg
        for finger in FOLDED_FINGERS
    )


class ModeGestureDetector:
    def __init__(self, settings: ModeGestureSettings | None = None) -> None:
        self._settings = settings or ModeGestureSettings()
        self._sign_since: float | None = None
        self._last_switch: float | None = None
        self._armed = True

    def sign_visible(self, hands: tuple[HandObservation, ...]) -> bool:
        return any(is_two_finger_sign(hand, self._settings) for hand in hands)

    def update(self, hands: tuple[HandObservation, ...], timestamp: float) -> bool:
        """Vero una volta sola, quando la V è stata tenuta abbastanza."""
        if not self.sign_visible(hands):
            self._sign_since = None
            self._armed = True
            return False

        if self._sign_since is None:
            self._sign_since = timestamp
        in_cooldown = (
            self._last_switch is not None
            and timestamp - self._last_switch < self._settings.cooldown_seconds
        )
        held = timestamp - self._sign_since >= self._settings.hold_seconds
        if self._armed and held and not in_cooldown:
            self._last_switch = timestamp
            self._armed = False
            return True
        return False

    def reset(self) -> None:
        self._sign_since = None
        self._armed = True
