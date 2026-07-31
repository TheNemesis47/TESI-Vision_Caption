class PointingEventGate:
    """Applica un cooldown fra due eventi di puntamento della stessa sessione."""

    def __init__(self, cooldown_seconds: float = 3.0) -> None:
        if cooldown_seconds < 0.0:
            raise ValueError("Il cooldown non può essere negativo")
        self._cooldown_seconds = cooldown_seconds
        self._last_event_timestamp: float | None = None

    def allow(self, timestamp: float) -> bool:
        if self._last_event_timestamp is None:
            self._last_event_timestamp = timestamp
            return True

        if timestamp - self._last_event_timestamp < self._cooldown_seconds:
            return False

        self._last_event_timestamp = timestamp
        return True

    def reset(self) -> None:
        self._last_event_timestamp = None
