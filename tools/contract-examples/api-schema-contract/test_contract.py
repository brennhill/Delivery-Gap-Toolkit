"""
Contract tests for the checkout API.

These verify interface shape, not business logic.
If the response schema changes, these break before any client does.
"""

from checkout_handler import handle_checkout
from schemas import (
    CHECKOUT_RESPONSE_SCHEMA,
    ERROR_RESPONSE_SCHEMA,
    validate_response,
)


SAMPLE_ITEMS = [
    {"name": "Widget", "price": 29.99, "quantity": 2},
    {"name": "Gadget", "price": 14.50, "quantity": 1},
]


def test_checkout_response_matches_schema():
    """Every required field is present with the correct type."""
    response = handle_checkout(SAMPLE_ITEMS)
    violations = validate_response(response, CHECKOUT_RESPONSE_SCHEMA)
    assert violations == [], f"Contract violations: {violations}"


def test_error_response_matches_schema():
    """Error responses follow the standard error envelope."""
    response = handle_checkout([])  # empty cart triggers error
    violations = validate_response(response, ERROR_RESPONSE_SCHEMA)
    assert violations == [], f"Contract violations: {violations}"


def test_no_extra_fields_leak():
    """Response contains only documented fields — no internal data leaks."""
    response = handle_checkout(SAMPLE_ITEMS)
    documented = set(CHECKOUT_RESPONSE_SCHEMA.keys())
    actual = set(response.keys())
    extra = actual - documented
    assert extra == set(), f"Undocumented fields in response: {extra}"


def test_field_types_enforced():
    """Numeric fields are numbers, not string representations."""
    response = handle_checkout(SAMPLE_ITEMS)
    for field in ("subtotal", "tax", "total"):
        assert isinstance(response[field], (int, float)), (
            f"'{field}' should be numeric, got {type(response[field]).__name__}"
        )


def test_nullable_fields_documented():
    """Fields that can be null are explicitly marked nullable in the schema."""
    # Without a discount code, discount_applied should be None
    response = handle_checkout(SAMPLE_ITEMS, discount_code=None)
    assert response["discount_applied"] is None

    # With a discount code, it should be a string
    response_with_discount = handle_checkout(SAMPLE_ITEMS, discount_code="SAVE10")
    assert isinstance(response_with_discount["discount_applied"], str)

    # The schema must document this field as nullable
    assert CHECKOUT_RESPONSE_SCHEMA["discount_applied"]["nullable"] is True
