"""
Invariant tests for balance transfers.

Invariant: sum(all balances) is constant before and after any transfer,
even failed ones. No account goes negative.

Run: pytest test_balance_transfer.py -v
"""

import random
import threading

import pytest

from balance_transfer import (
    Account,
    InsufficientFunds,
    TransferFailed,
    TransferService,
)


def test_basic_transfer(service, account_a, account_b):
    """$100 from A(500) to B(300) -> A=400, B=400, total=800."""
    service.transfer(account_a, account_b, 100)
    assert account_a.balance == 400
    assert account_b.balance == 400
    assert account_a.balance + account_b.balance == 800


def test_insufficient_funds_rejected(service, account_a, account_b):
    """Transfer more than balance -> both accounts unchanged."""
    total_before = account_a.balance + account_b.balance
    with pytest.raises(InsufficientFunds):
        service.transfer(account_a, account_b, 999)
    assert account_a.balance == 500
    assert account_b.balance == 300
    assert account_a.balance + account_b.balance == total_before


def test_conservation_under_concurrency(service):
    """10 threads doing random transfers -> total balance unchanged."""
    accounts = [Account(f"acct_{i}", balance=1000) for i in range(5)]
    total_before = sum(a.balance for a in accounts)
    barrier = threading.Barrier(10)

    def do_transfers():
        barrier.wait()
        for _ in range(20):
            src, dst = random.sample(accounts, 2)
            try:
                service.transfer(src, dst, random.randint(1, 100))
            except (InsufficientFunds, TransferFailed):
                pass

    threads = [threading.Thread(target=do_transfers) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_after = sum(a.balance for a in accounts)
    assert total_after == total_before, f"Money created/destroyed: {total_before} -> {total_after}"


def test_failed_credit_does_not_lose_money(service, account_a, account_b):
    """Simulate credit failure -> debit is rolled back."""
    total_before = account_a.balance + account_b.balance

    def explode():
        raise RuntimeError("Credit service timeout")

    with pytest.raises(TransferFailed):
        service.transfer(account_a, account_b, 100, credit_fn=explode)

    assert account_a.balance == 500
    assert account_b.balance == 300
    assert account_a.balance + account_b.balance == total_before


def test_no_negative_balances(service):
    """Concurrent drains on same account -> none go negative."""
    source = Account("drain_src", balance=100)
    targets = [Account(f"drain_{i}", balance=0) for i in range(20)]
    barrier = threading.Barrier(20)

    def drain(target):
        barrier.wait()
        try:
            service.transfer(source, target, 50)
        except (InsufficientFunds, TransferFailed):
            pass

    threads = [threading.Thread(target=drain, args=(t,)) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert source.balance >= 0, f"Source went negative: {source.balance}"
    total = source.balance + sum(t.balance for t in targets)
    assert total == 100
