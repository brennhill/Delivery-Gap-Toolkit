"""
pytest fixtures for state machine tests.

The Order class uses a threading.Lock to ensure that two concurrent
transition() calls on the same order are serialized. Without this lock,
both threads could read the same current state, both see it as valid,
and both write — leaving the object in an inconsistent state.

Production equivalents:
- Postgres: UPDATE orders SET status = $new WHERE id = $id AND status = $old
- DynamoDB: UpdateItem with ConditionExpression attribute_equals(status, old)
- Redis: Lua script that checks and sets atomically
"""

import pytest

from state_machine import Order


@pytest.fixture
def order():
    return Order("order_001")
