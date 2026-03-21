"""
Order state machine with explicit transition guards.

Bug AI generates: A set_status() method that accepts any status string. Orders
can go from "delivered" back to "pending", or skip from "pending" to
"delivered" without passing through intermediate states.

Correct pattern: Define an explicit transition map. The transition() method
checks the map and raises InvalidTransition if the move is not allowed.
Thread-safe via a lock to prevent concurrent transitions from corrupting state.
"""

import threading


class InvalidTransition(Exception):
    pass


VALID_TRANSITIONS = {
    "pending": {"paid"},
    "paid": {"shipped"},
    "shipped": {"delivered"},
    "delivered": set(),  # terminal state
}


class Order:
    """Thread-safe order with guarded state transitions."""

    def __init__(self, order_id: str, status: str = "pending"):
        if status not in VALID_TRANSITIONS:
            raise ValueError(f"Unknown status: {status}")
        self.order_id = order_id
        self._status = status
        self._lock = threading.Lock()

    @property
    def status(self) -> str:
        return self._status

    def transition(self, target: str) -> str:
        """Atomically transition to target status. Returns new status.

        Raises InvalidTransition if the move is not in the transition map.
        """
        with self._lock:
            allowed = VALID_TRANSITIONS.get(self._status, set())
            if target not in allowed:
                raise InvalidTransition(
                    f"Cannot transition from '{self._status}' to '{target}'"
                )
            self._status = target
            return self._status
