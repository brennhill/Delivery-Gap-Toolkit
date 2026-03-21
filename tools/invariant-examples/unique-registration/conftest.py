"""
pytest fixtures for unique registration tests.

The UserStore uses a threading.Lock to simulate the atomicity of
INSERT ... ON CONFLICT DO NOTHING. Without the lock, two concurrent
signups with the same email can both see the email as absent and both
insert, creating duplicate accounts.

Production equivalents:
- Postgres: INSERT INTO users (email, name) VALUES ($1, $2) ON CONFLICT (email) DO NOTHING
- DynamoDB: PutItem with ConditionExpression attribute_not_exists(email)
- Redis: SET email user_data NX
"""

import pytest

from registration import UserStore


@pytest.fixture
def store():
    return UserStore()
