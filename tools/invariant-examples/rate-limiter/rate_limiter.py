"""
Rate limiter with atomic increment-and-check.

Bug AI generates: GET count, check limit, then INCREMENT as three separate
operations. Under concurrent requests, multiple threads read the same count
before any increment, allowing bursts past the limit.

Correct pattern: Atomic increment-and-check. The counter is incremented and
the new value returned in a single locked operation. If the new value exceeds
the limit, the request is denied — no window for a race.
"""

import threading
import time


class RateLimiter:
    """Thread-safe rate limiter using atomic increment-and-check."""

    def __init__(self):
        self._lock = threading.Lock()
        self._windows: dict[str, dict[str, int | float]] = {}

    def allow(self, client_id: str, limit: int, window_seconds: float) -> bool:
        """Return True if the request is within the rate limit.

        Atomically increments the counter and checks the limit in one step.
        """
        now = time.monotonic()
        with self._lock:
            entry = self._windows.get(client_id)
            if entry is None or now - entry["start"] >= window_seconds:
                self._windows[client_id] = {"count": 1, "start": now}
                return True
            entry["count"] += 1
            return entry["count"] <= limit
