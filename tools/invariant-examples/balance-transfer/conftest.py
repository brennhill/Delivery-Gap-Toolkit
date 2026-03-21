"""
pytest fixtures for balance transfer tests.

The TransferService uses a threading.Lock to simulate a database transaction.
All balance reads and writes happen inside the lock, ensuring that concurrent
transfers cannot interleave and violate the conservation invariant.

Production equivalents:
- Postgres: BEGIN; SELECT ... FOR UPDATE; UPDATE ...; COMMIT;
- DynamoDB: TransactWriteItems with ConditionExpression
- Any ACID database with serializable isolation or row-level locking
"""

import pytest

from balance_transfer import Account, TransferService


@pytest.fixture
def service():
    return TransferService()


@pytest.fixture
def account_a():
    return Account("A", balance=500)


@pytest.fixture
def account_b():
    return Account("B", balance=300)
