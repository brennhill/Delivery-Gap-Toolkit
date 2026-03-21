"""
pytest fixtures: thread-safe in-memory database and fake entitlements API.

The InMemoryTable uses a threading.Lock to simulate the atomicity guarantees
you would get from a real database (INSERT ... ON CONFLICT DO NOTHING or
SELECT FOR UPDATE). Without this, concurrency tests pass by accident due to
Python's GIL, not because the code is actually safe.

For production: replace InMemoryTable with a database that supports
INSERT ... ON CONFLICT (Postgres) or conditional writes (DynamoDB).
"""

import threading

import pytest

from webhook_handler import handle_invoice_paid


class InMemoryTable:
    """Thread-safe in-memory table with atomic insert_if_absent."""

    def __init__(self):
        self._rows = []
        self._lock = threading.Lock()

    def insert(self, **kwargs):
        with self._lock:
            self._rows.append(kwargs)

    def insert_if_absent(self, key_field: str, **kwargs) -> bool:
        """Atomic check-and-insert. Returns True if inserted, False if key exists.

        This simulates INSERT ... ON CONFLICT DO NOTHING in Postgres or
        a conditional PutItem in DynamoDB. The lock ensures two concurrent
        callers cannot both see the key as absent and both insert.
        """
        key_value = kwargs[key_field]
        with self._lock:
            for row in self._rows:
                if row.get(key_field) == key_value:
                    return False
            self._rows.append(kwargs)
            return True

    def get(self, timeout_ms=None, **filters):
        with self._lock:
            for row in self._rows:
                if all(row.get(k) == v for k, v in filters.items()):
                    return row
        return None

    def count(self, **filters):
        with self._lock:
            return sum(
                1
                for row in self._rows
                if all(row.get(k) == v for k, v in filters.items())
            )


class InMemoryDB:
    def __init__(self):
        self.payments = InMemoryTable()
        self.entitlements = InMemoryTable()


class FakeEntitlementsAPI:
    def __init__(self, db):
        self._db = db

    def grant_access(self, invoice_id, idempotency_key=None):
        # The handler already did the atomic insert — this is a no-op
        # in the test fixture. In production, this would call the real API.
        pass


class WebhookClient:
    def __init__(self, db):
        self._db = db
        self._entitlements = FakeEntitlementsAPI(db)

    def post(self, payload, idempotency_key):
        return handle_invoice_paid(
            invoice_id=idempotency_key,
            amount_cents=payload["amount"],
            db=self._db,
            entitlements_api=self._entitlements,
        )


@pytest.fixture
def db():
    return InMemoryDB()


@pytest.fixture
def webhook_client(db):
    return WebhookClient(db)
