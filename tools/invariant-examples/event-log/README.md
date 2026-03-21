# Event Log

Invariant test suite proving that event sequence numbers are strictly monotonic and gap-free under concurrency.

## How AI fails

AI generates an event log that uses `len(events) + 1` as the next sequence number. Under concurrency, two writers read the same length and both assign the same sequence number, creating duplicates and gaps in the log.

## The correct pattern

Atomic counter: increment the sequence counter and append the event inside a single lock. Each writer gets a unique, sequential number. No window between reading the counter and writing the event.

## Tests

| Test | Invariant |
|------|-----------|
| `test_sequential_append` | 10 events produce sequences 1-10 |
| `test_concurrent_append` | 20 threads produce sequences 1-20, no gaps, no duplicates |
| `test_high_volume_concurrent` | 100 threads produce sequences 1-100 |
| `test_ordering_preserved` | Events from a single writer maintain causal order |

## Run

```bash
pytest test_event_log.py -v
```

## Production note

Replace the `threading.Lock` with a database-managed sequence: `SERIAL` or `GENERATED ALWAYS AS IDENTITY` in Postgres, or an atomic counter in DynamoDB. The invariant is the same: sequence assignment must be atomic with the append.
