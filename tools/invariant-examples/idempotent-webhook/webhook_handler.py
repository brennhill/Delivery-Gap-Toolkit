"""
Idempotent webhook handler reference implementation.

The key design decision: idempotency key is the business entity ID (invoice_id),
not the provider's X-Request-Id header. The provider can change the request ID
on retry. The invoice ID is stable.

On every request:
  1. Check if charge already exists for this invoice_id
  2. Check if entitlement grant already exists for this invoice_id
  3. Execute only the missing steps

This means the handler is safe to call multiple times with the same payload.
"""

from dataclasses import dataclass


@dataclass
class WebhookResult:
    status: int
    message: str


def handle_invoice_paid(
    invoice_id: str,
    amount_cents: int,
    db,
    entitlements_api,
    verify_timeout_ms: int = 2000,
) -> WebhookResult:
    """
    Process an invoice.paid event idempotently.

    Args:
        invoice_id: Business entity ID — used as idempotency key
        amount_cents: Amount to charge
        db: Database client (must support atomic get_or_insert)
        entitlements_api: Entitlements service client
        verify_timeout_ms: Timeout for state-verification queries.
                           Must fit within the webhook's SLA budget.
                           If exceeded, return 503 (retriable) not 500 (fatal).
    """
    # --- Step 1: Verify charge state ---
    try:
        payment = db.payments.get(
            invoice_id=invoice_id,
            timeout_ms=verify_timeout_ms,
        )
    except TimeoutError:
        # State-verification query timed out. Return retriable 503.
        # Do NOT charge — we don't know whether we already charged.
        return WebhookResult(503, "State verification timed out — safe to retry")

    charge_needed = payment is None

    # --- Step 2: Verify entitlement state ---
    try:
        entitlement = db.entitlements.get(
            invoice_id=invoice_id,
            timeout_ms=verify_timeout_ms,
        )
    except TimeoutError:
        return WebhookResult(503, "State verification timed out — safe to retry")

    grant_needed = entitlement is None

    # --- Step 3: Execute only missing steps ---
    # Use atomic insert to prevent races: if two threads both see
    # charge_needed=True, only one insert will succeed.
    if charge_needed:
        inserted = db.payments.insert_if_absent(
            key_field="invoice_id",
            invoice_id=invoice_id,
            amount_cents=amount_cents,
            status="SUCCESS",
        )
        if not inserted:
            charge_needed = False  # Lost the race — another thread charged

    if grant_needed:
        inserted = db.entitlements.insert_if_absent(
            key_field="invoice_id",
            invoice_id=invoice_id,
            status="GRANTED",
        )
        if inserted:
            # Only call the external API if we won the insert race
            entitlements_api.grant_access(
                invoice_id=invoice_id,
                idempotency_key=invoice_id,
            )

    if not charge_needed and not grant_needed:
        return WebhookResult(409, "Already processed — idempotent skip")

    return WebhookResult(202, "Accepted")
