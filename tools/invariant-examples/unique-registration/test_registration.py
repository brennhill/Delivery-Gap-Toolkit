"""
Invariant tests for unique registration.

Invariant: Two concurrent signups with the same email produce exactly one
account, never two.

Run: pytest test_registration.py -v
"""

import threading


def test_single_registration(store):
    """One signup -> one account."""
    result = store.register("alice@example.com", "Alice")
    assert result.success is True
    assert store.count() == 1


def test_duplicate_email_rejected(store):
    """Same email twice -> one account, second returns conflict."""
    r1 = store.register("bob@example.com", "Bob")
    r2 = store.register("bob@example.com", "Bob Again")
    assert r1.success is True
    assert r2.success is False
    assert store.count() == 1


def test_concurrent_duplicate_registration(store):
    """Two threads, same email -> exactly one account."""
    results = []
    barrier = threading.Barrier(2)

    def signup():
        barrier.wait()
        results.append(store.register("race@example.com", "Racer"))

    t1 = threading.Thread(target=signup)
    t2 = threading.Thread(target=signup)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert store.count() == 1
    successes = sum(1 for r in results if r.success)
    assert successes == 1


def test_high_concurrency_same_email(store):
    """10 threads, same email -> exactly one account."""
    results = []
    barrier = threading.Barrier(10)

    def signup():
        barrier.wait()
        results.append(store.register("popular@example.com", "Popular"))

    threads = [threading.Thread(target=signup) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert store.count() == 1
    successes = sum(1 for r in results if r.success)
    assert successes == 1
    assert sum(1 for r in results if not r.success) == 9


def test_different_emails_independent(store):
    """Concurrent signups with different emails -> all succeed."""
    results = []
    barrier = threading.Barrier(5)

    def signup(email):
        barrier.wait()
        results.append(store.register(email, f"User {email}"))

    emails = [f"user{i}@example.com" for i in range(5)]
    threads = [threading.Thread(target=signup, args=(e,)) for e in emails]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert store.count() == 5
    assert all(r.success for r in results)
