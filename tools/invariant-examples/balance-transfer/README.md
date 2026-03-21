# Balance Transfer

Invariant test suite proving that money is neither created nor destroyed during transfers, even under concurrency and partial failures.

## How AI fails

AI generates a transfer that debits account A, then credits account B as two separate operations. If the credit fails (timeout, crash), money disappears from the system. It also skips the balance check, allowing accounts to go negative.

## The correct pattern

Wrap check-balance, debit, and credit inside a single lock (simulating a database transaction). If the credit fails, roll back the debit. Nothing changes on failure.

## Tests

| Test | Invariant |
|------|-----------|
| `test_basic_transfer` | A=400, B=400, total=800 after $100 transfer |
| `test_insufficient_funds_rejected` | Both accounts unchanged when source lacks funds |
| `test_conservation_under_concurrency` | 10 threads, random transfers, total balance unchanged |
| `test_failed_credit_does_not_lose_money` | Credit failure rolls back debit |
| `test_no_negative_balances` | Concurrent drains never push an account negative |

## Run

```bash
pytest test_balance_transfer.py -v
```

## Production note

Replace the `threading.Lock` with a database transaction: `BEGIN; SELECT ... FOR UPDATE; UPDATE ...; COMMIT;` in Postgres, or `TransactWriteItems` in DynamoDB. The invariant is the same: debit and credit must be atomic.
