"""
Event log with atomic sequence number assignment.

Bug AI generates: Uses len(events) + 1 as the next sequence number. Under
concurrency, two writers read the same length and both assign the same
sequence number, creating duplicates and gaps.

Correct pattern: Atomic counter for sequence numbers. Each append atomically
increments the counter and returns the next number inside a single lock.
"""

import threading
from dataclasses import dataclass


@dataclass
class Event:
    sequence: int
    payload: str
    writer_id: str


class EventLog:
    """Thread-safe event log with gap-free sequence numbers."""

    def __init__(self):
        self._events: list[Event] = []
        self._counter = 0
        self._lock = threading.Lock()

    def append(self, payload: str, writer_id: str = "default") -> Event:
        """Atomically assign a sequence number and append the event."""
        with self._lock:
            self._counter += 1
            event = Event(sequence=self._counter, payload=payload, writer_id=writer_id)
            self._events.append(event)
            return event

    def events(self) -> list[Event]:
        with self._lock:
            return list(self._events)

    def sequences(self) -> list[int]:
        with self._lock:
            return [e.sequence for e in self._events]
