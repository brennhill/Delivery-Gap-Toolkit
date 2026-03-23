"""
Reference checkout handler. Returns structured responses
that must conform to the contract in schemas.py.
"""

import uuid


def handle_checkout(items: list[dict], discount_code: str | None = None) -> dict:
    """Process a checkout and return a response matching CHECKOUT_RESPONSE_SCHEMA."""
    if not items:
        return {
            "error": "Cart is empty",
            "code": "EMPTY_CART",
            "request_id": str(uuid.uuid4()),
        }

    subtotal = sum(item["price"] * item.get("quantity", 1) for item in items)
    tax = round(subtotal * 0.08, 2)

    discount_applied = None
    if discount_code == "SAVE10":
        subtotal = round(subtotal * 0.9, 2)
        discount_applied = "SAVE10"

    total = round(subtotal + tax, 2)

    return {
        "order_id": str(uuid.uuid4()),
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "currency": "USD",
        "discount_applied": discount_applied,
    }
