# API Schema Contract Test

A runnable contract test demonstrating schema validation for a REST API. Verifies that API responses match their documented contract — field names, types, required fields, and status codes.

## The bug

A checkout endpoint returns `{ "total": 42.50 }`. An AI refactors the handler and renames the field to `{ "amount": 42.50 }`. All unit tests pass (they were generated alongside the refactor). The mobile client silently displays $0.00 because it reads `total`.

## The fix

A contract test that validates response shape against a schema definition. The schema is the spec. If the response doesn't match, the build breaks before any client sees the change.

## Run

```bash
pytest test_contract.py -v
```

## What the tests prove

| Test | Contract | What breaks without it |
|------|----------|----------------------|
| `test_checkout_response_matches_schema` | Response contains all required fields with correct types | Silent field rename breaks downstream clients |
| `test_error_response_matches_schema` | Error responses follow a standard envelope | Inconsistent error formats across endpoints |
| `test_no_extra_fields_leak` | Response contains only documented fields | Internal fields (user_id, debug info) leak to clients |
| `test_field_types_enforced` | `total` is a number, not a string `"42.50"` | Type coercion bugs in serialization |
| `test_nullable_fields_documented` | Nullable fields are explicitly marked, not silently absent | Client crashes on missing field vs null |

## Files

| File | What it does |
|------|-------------|
| `schemas.py` | Contract definitions: required fields, types, nullability |
| `checkout_handler.py` | Reference implementation of a checkout endpoint |
| `test_contract.py` | Five contract tests against the schema |

## How this differs from invariant tests

Invariant tests verify *business rules* (no double charge, balances never negative). Contract tests verify *interface shape* (this endpoint returns these fields in this format). Both are deterministic. Both run in CI. They catch different failure classes.

## Connecting to your spec

The schema in `schemas.py` should be derived from your one-page spec's acceptance criteria (Section 6). When the spec says "the checkout response includes a breakdown of tax, subtotal, and total," that becomes a contract. The contract is the spec made executable.
