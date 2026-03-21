"""
Invariant tests for event log.

Invariant: Sequence numbers are strictly monotonic and gap-free.
After N appends, sequences are exactly [1, 2, ..., N].

Run: pytest test_event_log.py -v
"""

import threading


def test_sequential_append(log):
    """10 events -> sequence 1-10, no gaps."""
    for i in range(10):
        log.append(f"event_{i}")

    seqs = log.sequences()
    assert seqs == list(range(1, 11))


def test_concurrent_append(log):
    """20 threads each appending 1 event -> 20 events, sequences 1-20."""
    barrier = threading.Barrier(20)

    def do_append(i):
        barrier.wait()
        log.append(f"concurrent_{i}", writer_id=f"writer_{i}")

    threads = [threading.Thread(target=do_append, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    seqs = sorted(log.sequences())
    assert seqs == list(range(1, 21)), f"Gaps or duplicates: {seqs}"
    assert len(set(log.sequences())) == 20, "Duplicate sequence numbers"


def test_high_volume_concurrent(log):
    """100 threads -> 100 sequential events, no gaps, no duplicates."""
    barrier = threading.Barrier(100)

    def do_append(i):
        barrier.wait()
        log.append(f"high_vol_{i}", writer_id=f"w_{i}")

    threads = [threading.Thread(target=do_append, args=(i,)) for i in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    seqs = sorted(log.sequences())
    assert seqs == list(range(1, 101))
    assert len(set(log.sequences())) == 100


def test_ordering_preserved(log):
    """Events from a single writer maintain causal order."""
    for i in range(5):
        log.append(f"step_{i}", writer_id="single_writer")

    events = log.events()
    writer_events = [e for e in events if e.writer_id == "single_writer"]
    for i in range(len(writer_events) - 1):
        assert writer_events[i].sequence < writer_events[i + 1].sequence
