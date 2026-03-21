"""
pytest fixtures for event log tests.

The EventLog uses a threading.Lock to ensure that sequence number assignment
and event append are atomic. Without the lock, concurrent writers can read
the same counter value and assign duplicate sequence numbers.

Production equivalents:
- Postgres: INSERT with a SERIAL or GENERATED ALWAYS AS IDENTITY column
- DynamoDB: Atomic counter via UpdateItem ADD, then PutItem with the returned value
- Kafka: Partition offsets assigned by the broker (inherently sequential)
"""

import pytest

from event_log import EventLog


@pytest.fixture
def log():
    return EventLog()
