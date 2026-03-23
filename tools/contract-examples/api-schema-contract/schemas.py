"""
Contract definitions for the checkout API.

Each schema is a dict of field_name -> {type, required, nullable}.
This is the executable form of your spec's acceptance criteria.
"""

CHECKOUT_RESPONSE_SCHEMA = {
    "order_id": {"type": str, "required": True, "nullable": False},
    "subtotal": {"type": (int, float), "required": True, "nullable": False},
    "tax": {"type": (int, float), "required": True, "nullable": False},
    "total": {"type": (int, float), "required": True, "nullable": False},
    "currency": {"type": str, "required": True, "nullable": False},
    "discount_applied": {"type": str, "required": False, "nullable": True},
}

ERROR_RESPONSE_SCHEMA = {
    "error": {"type": str, "required": True, "nullable": False},
    "code": {"type": str, "required": True, "nullable": False},
    "request_id": {"type": str, "required": True, "nullable": False},
}

# All schemas for this service, keyed by response type.
SCHEMAS = {
    "checkout": CHECKOUT_RESPONSE_SCHEMA,
    "error": ERROR_RESPONSE_SCHEMA,
}


def validate_response(response: dict, schema: dict) -> list[str]:
    """Validate a response dict against a schema. Returns list of violations."""
    violations = []

    # Check required fields are present
    for field, rules in schema.items():
        if rules["required"] and field not in response:
            violations.append(f"missing required field: {field}")
            continue

        if field not in response:
            continue

        value = response[field]

        # Check nullability
        if value is None and not rules["nullable"]:
            violations.append(f"field '{field}' is null but not nullable")
            continue

        # Check type (skip if null and nullable)
        if value is not None and not isinstance(value, rules["type"]):
            expected = rules["type"].__name__ if isinstance(rules["type"], type) else str(rules["type"])
            violations.append(
                f"field '{field}' has type {type(value).__name__}, expected {expected}"
            )

    # Check for undocumented fields
    extra = set(response.keys()) - set(schema.keys())
    for field in extra:
        violations.append(f"undocumented field: {field}")

    return violations
