"""
Atomic balance transfer with conservation invariant.

Bug AI generates: Debit account A, then credit account B as two separate
operations. If the credit fails (timeout, crash), money disappears. Also:
no check that the source has sufficient balance before debiting.

Correct pattern: Check balance, debit, and credit inside a single lock
(simulating a database transaction). If any step fails, nothing changes.
"""

import threading


class InsufficientFunds(Exception):
    pass


class TransferFailed(Exception):
    pass


class Account:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance


class TransferService:
    """Thread-safe transfer service with atomic debit+credit."""

    def __init__(self):
        self._lock = threading.Lock()

    def transfer(
        self, source: Account, target: Account, amount: int,
        credit_fn=None,
    ) -> None:
        """Atomically transfer amount from source to target.

        credit_fn: optional hook called during credit (for fault injection).
        Raises InsufficientFunds or TransferFailed; either way, both
        balances remain unchanged on failure.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with self._lock:
            if source.balance < amount:
                raise InsufficientFunds(
                    f"{source.account_id} has {source.balance}, need {amount}"
                )
            # Debit and credit inside the same lock = atomic
            source.balance -= amount
            try:
                if credit_fn:
                    credit_fn()  # fault injection point
                target.balance += amount
            except Exception:
                source.balance += amount  # rollback
                raise TransferFailed("Credit failed, debit rolled back")
