# Idempotent Webhook Receiver

A runnable invariant test suite demonstrating idempotent payment processing under retry pressure, concurrent races, and partial failures.

## The bug

A webhook handler uses the provider's `X-Request-Id` as an idempotency key. The provider changes the request ID on retry. Two retries of the same invoice produce two charges.

## The fix

Use the business entity ID (`invoice_id`) as the idempotency key. On every request, verify the state of *all* side effects (charge and entitlement grant) before executing any of them. Use atomic insert (INSERT ... ON CONFLICT DO NOTHING) to prevent races.

## Run

```bash
pytest test_idempotency.py -v
```

## What the tests prove

| Test | Invariant | What breaks without it |
|------|-----------|----------------------|
| `test_idempotency_under_retry_pressure` | Same key twice = exactly one charge | Double charges on provider retry |
| `test_concurrent_retry_idempotency` | Two threads racing = exactly one charge | Race condition between SELECT and INSERT |
| `test_partial_failure_recovery` | Charge succeeded + grant timed out on retry = no re-charge, grant completes | Naive retry re-charges because it only checks one side effect |
| `test_high_concurrency_stress` | 10 threads = exactly one charge, one grant | Any gap in atomicity surfaces under load |

## Files

| File | What it does |
|------|-------------|
| `webhook_handler.py` | Reference implementation using atomic `insert_if_absent` |
| `conftest.py` | Thread-safe in-memory DB with lock-based atomicity |
| `test_idempotency.py` | Four invariant tests |

## Concurrency note

The `InMemoryTable` uses `threading.Lock` to simulate the atomicity you would get from a real database. Without this lock, concurrency tests pass by accident due to Python's GIL — not because the code is safe. For production, replace with:

- **Postgres**: `INSERT ... ON CONFLICT DO NOTHING`
- **DynamoDB**: Conditional `PutItem` with `attribute_not_exists`
- **Redis**: `SET NX` (set if not exists)

The invariant is the same regardless of storage: check-then-act must be atomic.
