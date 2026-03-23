# Contract Gate Examples

Contract tests verify **interface shape** — that API responses match their documented schema. They catch a different failure class than invariant tests:

- **Invariant tests** verify business rules (no double charge, balances never negative)
- **Contract tests** verify interface agreements (this endpoint returns these fields in this format)

Both are deterministic. Both run in CI. Both catch failures that AI-generated code introduces silently.

## Examples

| Example | What it catches |
|---------|----------------|
| [api-schema-contract](api-schema-contract/) | Field renames, type changes, undocumented fields leaking to clients |

## Why AI code needs contract tests

When an AI refactors a handler, it often renames fields to something "cleaner" — `total` becomes `amount`, `user_id` becomes `userId`. Unit tests generated alongside the refactor pass because they test the new names. The contract test breaks because the *clients* still expect the old names.

This is the same pattern the book describes in Chapter 6: without a spec, your gates have nothing to verify against. The contract schema *is* the spec, made executable.
