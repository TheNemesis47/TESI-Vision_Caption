"""Le scelte che arrivano dal telefono insieme ai fotogrammi.

Chi ascolta sa cose che il server non può sapere: se la lezione corre, se la
stanza è la sua cucina, se preferisce poche parole dette presto a una
descrizione completa che arriva tardi. Queste scelte stanno nel telefono e
viaggiano su ogni fotogramma, non in un messaggio a parte: quando i
fotogrammi si accumulano il server tiene soltanto l'ultimo, e un messaggio di
impostazioni finirebbe fra quelli scartati.

Niente di ciò che arriva da fuori viene creduto: un numero di parole assurdo
renderebbe muta la descrizione, un intervallo di zero secondi farebbe parlare
l'applicazione sopra sé stessa, e una modalità inventata sceglierebbe un
prompt che non esiste. Qui si valida; il resto del server riceve valori già
buoni oppure niente.
"""

from dataclasses import dataclass
from typing import Any, Mapping


# Sotto le dieci parole non c'è una descrizione, sopra le centocinquanta non
# c'è nessuno che ascolti fino in fondo.
MIN_MAX_WORDS = 10
MAX_MAX_WORDS = 150

# Due secondi è il minimo perché una descrizione duri meno della successiva;
# cinque minuti è il massimo oltre il quale l'applicazione sembra spenta.
MIN_INTERVAL_SECONDS = 2.0
MAX_INTERVAL_SECONDS = 300.0

MODE_MAX_LENGTH = 64


@dataclass(frozen=True)
class SessionPreferences:
    """Le scelte valide di una sessione; None significa «come il server»."""

    max_words: int | None = None
    min_interval_seconds: float | None = None
    mode: str | None = None

    @property
    def is_empty(self) -> bool:
        return (
            self.max_words is None
            and self.min_interval_seconds is None
            and self.mode is None
        )


def _clamped_int(value: Any, low: int, high: int) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return min(high, max(low, number))


def _clamped_float(value: Any, low: float, high: float) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return min(high, max(low, number))


def parse_session_preferences(
    raw: Any,
    allowed_modes: tuple[str, ...] = (),
) -> SessionPreferences:
    """Le preferenze ricavate da ciò che il telefono ha mandato.

    Un campo illeggibile non invalida gli altri: resta None e per quello
    decide il server. Una modalità che non esiste viene ignorata invece di
    fermare la sessione, perché il telefono può avere un elenco più vecchio
    di quello che il server ha caricato.
    """
    if not isinstance(raw, Mapping):
        return SessionPreferences()

    mode = raw.get("mode")
    chosen_mode: str | None = None
    if isinstance(mode, str):
        candidate = mode.strip()[:MODE_MAX_LENGTH]
        if candidate and candidate in allowed_modes:
            chosen_mode = candidate

    return SessionPreferences(
        max_words=_clamped_int(
            raw.get("max_words"), MIN_MAX_WORDS, MAX_MAX_WORDS
        ),
        min_interval_seconds=_clamped_float(
            raw.get("min_interval_seconds"),
            MIN_INTERVAL_SECONDS,
            MAX_INTERVAL_SECONDS,
        ),
        mode=chosen_mode,
    )
