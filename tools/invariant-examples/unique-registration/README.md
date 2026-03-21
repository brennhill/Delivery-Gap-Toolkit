# Unique Registration

Invariant test suite proving that concurrent signups with the same email produce exactly one account.

## How AI fails

AI generates registration that does `SELECT` to check if email exists, then `INSERT` if not. Two concurrent signups with the same email both see "not exists" and both insert, creating duplicate accounts.

## The correct pattern

Atomic `insert_if_absent`: check and insert in a single locked operation (simulating `INSERT ... ON CONFLICT DO NOTHING`). If the email already exists, return a conflict result. No window between check and insert.

## Tests

| Test | Invariant |
|------|-----------|
| `test_single_registration` | One signup creates one account |
| `test_duplicate_email_rejected` | Same email twice produces one account |
| `test_concurrent_duplicate_registration` | Two threads, same email, exactly one account |
| `test_high_concurrency_same_email` | 10 threads, same email, exactly one account |
| `test_different_emails_independent` | Different emails all succeed concurrently |

## Run

```bash
pytest test_registration.py -v
```

## Production note

Replace the `threading.Lock` with a database unique constraint: `INSERT ... ON CONFLICT (email) DO NOTHING` in Postgres, or a conditional `PutItem` in DynamoDB. The invariant is the same: check-and-insert must be one atomic operation.
