"""
Unique registration with atomic insert-if-absent.

Bug AI generates: SELECT to check if email exists, then INSERT if not. Two
concurrent signups with the same email both see "not exists" and both insert,
creating duplicate accounts.

Correct pattern: Atomic insert_if_absent (INSERT ... ON CONFLICT DO NOTHING).
Returns whether the insert succeeded. If it didn't, the email already exists.
"""

import threading
from dataclasses import dataclass


@dataclass
class RegistrationResult:
    success: bool
    message: str


class UserStore:
    """Thread-safe user store with atomic insert-if-absent."""

    def __init__(self):
        self._users: dict[str, dict] = {}
        self._lock = threading.Lock()

    def register(self, email: str, name: str) -> RegistrationResult:
        """Atomically register a user. Returns conflict if email exists."""
        with self._lock:
            if email in self._users:
                return RegistrationResult(False, "Email already registered")
            self._users[email] = {"email": email, "name": name}
            return RegistrationResult(True, "Registered")

    def count(self) -> int:
        with self._lock:
            return len(self._users)

    def get(self, email: str) -> dict | None:
        with self._lock:
            return self._users.get(email)
