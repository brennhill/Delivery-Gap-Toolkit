"""
pytest fixtures for rate limiter tests.

The RateLimiter uses a threading.Lock to simulate the atomicity you would get
from Redis INCR + EXPIRE or a Lua script. Without the lock, concurrent
requests can all read the same count before any increment lands.

Production equivalents:
- Redis: INCR key; if result == 1 then EXPIRE key window_seconds
- DynamoDB: UpdateItem with ADD + ConditionExpression
- Postgres: INSERT ... ON CONFLICT DO UPDATE SET count = count + 1 RETURNING count
"""

import pytest

from rate_limiter import RateLimiter


@pytest.fixture
def limiter():
    return RateLimiter()
