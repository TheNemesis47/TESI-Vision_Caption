import time


class RateLimiter:
    def __init__(self, min_interval_seconds: int = 5):
        self.min_interval_seconds = min_interval_seconds
        self._last_executed_time = None

    def can_execute(self) -> bool:
        if self._last_executed_time is None:
            return True
        if (time.monotonic() - self._last_executed_time) >= self.min_interval_seconds:
            return True
        return False

    def record(self):
        self._last_executed_time = time.monotonic()

    @property
    def seconds_until_next(self) -> float:
        if self._last_executed_time is None:
            return 0.0
        elapsed = time.monotonic() - self._last_executed_time
        return self.min_interval_seconds - elapsed