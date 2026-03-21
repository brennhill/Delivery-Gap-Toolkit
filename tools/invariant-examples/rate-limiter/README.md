# Rate Limiter

Invariant test suite proving that a rate limiter cannot be burst-bypassed under concurrency.

## How AI fails

AI generates a rate limiter that does `GET count`, `check < limit`, `INCREMENT count` as three separate operations. Under concurrent requests, multiple threads read the same count before any increment, allowing a burst of requests past the limit.

## The correct pattern

Atomic increment-and-check: increment the counter and return the new value inside a single lock (simulating Redis `INCR`). If the new value exceeds the limit, deny the request. There is no window between reading and writing where another thread can sneak through.

## Tests

| Test | Invariant |
|------|-----------|
| `test_single_client_limit` | 10 requests with limit 5 produces exactly 5 accepted |
| `test_concurrent_burst` | 20 threads hitting simultaneously with limit 5 still produces exactly 5 |
| `test_window_reset` | After window expires, new requests are accepted |
| `test_multiple_clients_isolated` | Client A's usage does not affect Client B |

## Run

```bash
pytest test_rate_limiter.py -v
```

## Production note

Replace the `threading.Lock` with Redis `INCR` + `EXPIRE`, a Redis Lua script, or DynamoDB `UpdateItem` with `ADD`. The invariant is the same: increment-and-check must be one atomic operation.
