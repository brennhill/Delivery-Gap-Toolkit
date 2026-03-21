"""
Three invariant tests for idempotent webhook processing.

These test correctness under the conditions that actually cause double charges:
  - Provider retry with same idempotency key
  - Two simultaneous retries racing (with real thread concurrency)
  - Partial failure: charge succeeded but downstream grant timed out

Run: pytest test_idempotency.py -v
"""

import threading


def test_idempotency_under_retry_pressure(webhook_client, db):
    """Same idempotency key sent twice must produce exactly one charge."""
    payload = {"invoice_id": "inv_789", "amount": 100}
    idempotency_key = "inv_789"

    result1 = webhook_client.post(payload, idempotency_key=idempotency_key)
    result2 = webhook_client.post(payload, idempotency_key=idempotency_key)

    assert result1.status in (200, 202)
    assert result2.status in (200, 202, 409)  # Accepted or conflict — never 500
    assert db.payments.count(invoice_id="inv_789") == 1
    assert db.entitlements.count(invoice_id="inv_789") == 1


def test_concurrent_retry_idempotency(webhook_client, db):
    """Two simultaneous retries with the same key must not double-charge.

    This test is meaningful because InMemoryTable uses a lock to simulate
    the atomicity of INSERT ... ON CONFLICT DO NOTHING. Without that lock,
    both threads would see the key as absent and both would insert — which
    is exactly the bug this invariant catches.
    """
    payload = {"invoice_id": "inv_790", "amount": 100}
    idempotency_key = "inv_790"
    results = []
    barrier = threading.Barrier(2)  # Force both threads to start simultaneously

    def do_call():
        barrier.wait()  # Ensure true concurrency, not sequential execution
        results.append(webhook_client.post(payload, idempotency_key=idempotency_key))

    t1 = threading.Thread(target=do_call)
    t2 = threading.Thread(target=do_call)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    statuses = {r.status for r in results}
    assert statuses <= {200, 202, 409}, f"Unexpected statuses: {statuses}"
    assert db.payments.count(invoice_id="inv_790") == 1  # Still only one charge
    assert db.entitlements.count(invoice_id="inv_790") == 1


def test_partial_failure_recovery(webhook_client, db):
    """
    Charge succeeded but entitlement grant timed out before the first attempt
    completed. On retry: must NOT re-charge, MUST complete the grant.

    This is the scenario the naive implementation gets wrong:
    - Charge: verified idempotent (correctly skipped)
    - Grant: not checked — runs again and either fails or double-grants

    The correct behavior: verify BOTH side effects before deciding what to do.
    """
    payload = {"invoice_id": "inv_791", "amount": 100}
    idempotency_key = "inv_791"

    # Simulate: charge wrote successfully, entitlement call timed out
    db.payments.insert(invoice_id="inv_791", amount_cents=100, status="SUCCESS")
    # entitlements table is intentionally empty — grant never completed

    result = webhook_client.post(payload, idempotency_key=idempotency_key)

    assert result.status in (200, 202, 409)
    assert db.payments.count(invoice_id="inv_791") == 1  # No double charge
    assert db.entitlements.count(invoice_id="inv_791") == 1  # Grant completed on retry


def test_high_concurrency_stress(webhook_client, db):
    """10 concurrent threads hitting the same invoice must produce exactly one charge."""
    payload = {"invoice_id": "inv_stress", "amount": 500}
    idempotency_key = "inv_stress"
    results = []
    barrier = threading.Barrier(10)

    def do_call():
        barrier.wait()
        results.append(webhook_client.post(payload, idempotency_key=idempotency_key))

    threads = [threading.Thread(target=do_call) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert db.payments.count(invoice_id="inv_stress") == 1
    assert db.entitlements.count(invoice_id="inv_stress") == 1
    # Exactly one 202, rest are 409
    accepted = sum(1 for r in results if r.status == 202)
    conflicts = sum(1 for r in results if r.status == 409)
    assert accepted == 1
    assert conflicts == 9
