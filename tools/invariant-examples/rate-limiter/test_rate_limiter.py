"""
Invariant tests for rate limiting.

Invariant: A client cannot exceed N requests in any window, even under
concurrent burst. The counter is never read without being incremented
atomically.

Run: pytest test_rate_limiter.py -v
"""

import threading
import time


def test_single_client_limit(limiter):
    """10 requests with limit 5 -> exactly 5 accepted."""
    results = [limiter.allow("client_a", limit=5, window_seconds=10) for _ in range(10)]
    assert sum(results) == 5
    assert results[:5] == [True] * 5
    assert results[5:] == [False] * 5


def test_concurrent_burst(limiter):
    """20 threads hitting simultaneously with limit 5 -> exactly 5 accepted."""
    results = []
    barrier = threading.Barrier(20)

    def hit():
        barrier.wait()
        results.append(limiter.allow("burst_client", limit=5, window_seconds=10))

    threads = [threading.Thread(target=hit) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sum(results) == 5, f"Expected 5 accepted, got {sum(results)}"


def test_window_reset(limiter):
    """After window expires, new requests are accepted."""
    for _ in range(5):
        limiter.allow("reset_client", limit=5, window_seconds=0.05)

    assert limiter.allow("reset_client", limit=5, window_seconds=0.05) is False
    time.sleep(0.06)
    assert limiter.allow("reset_client", limit=5, window_seconds=0.05) is True


def test_multiple_clients_isolated(limiter):
    """Client A's requests don't affect Client B's limit."""
    for _ in range(5):
        limiter.allow("client_a", limit=5, window_seconds=10)

    assert limiter.allow("client_a", limit=5, window_seconds=10) is False
    assert limiter.allow("client_b", limit=5, window_seconds=10) is True
