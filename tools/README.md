# Tools — Worked Examples & Reference Implementations

Reference implementations for concepts that are easier to understand with running code than prose.

---

## invariant-examples/

Tests that verify **business rules** hold under all conditions. Tier 2 gates — not checking specific inputs/outputs, but checking whether a *property* holds for *all* inputs.

| Example | Invariant |
|---------|-----------|
| [idempotent-webhook/](invariant-examples/idempotent-webhook/) | Processing the same webhook twice produces exactly one side effect |
| [rate-limiter/](invariant-examples/rate-limiter/) | Token bucket respects limits under concurrent access |
| [state-machine/](invariant-examples/state-machine/) | Only valid state transitions are allowed |
| [balance-transfer/](invariant-examples/balance-transfer/) | No double-debit, atomic transfers |
| [unique-registration/](invariant-examples/unique-registration/) | Uniqueness constraint holds under race conditions |
| [event-log/](invariant-examples/event-log/) | Event ordering invariants across threads |

The three questions: What must never happen twice? What must always be true after this operation completes? What breaks if operations run out of order?

---

## contract-examples/

Tests that verify **interface shape** — API responses match their documented schema. Tier 1 gates — catching silent renames, type changes, and undocumented field leaks.

| Example | Contract |
|---------|----------|
| [api-schema-contract/](contract-examples/api-schema-contract/) | Checkout response fields, types, and nullability match the spec |

---

## eval-examples/

Tools for building **domain-specific evaluations** — start with error analysis to discover what actually fails, then build targeted evals.

| Example | Pattern |
|---------|---------|
| [error-analysis-workflow/](eval-examples/error-analysis-workflow/) | Step 0: collect, review, categorize real failures before building any gate |
| [llm-as-judge/](eval-examples/llm-as-judge/) | Grade AI outputs against a domain-specific rubric (not generic metrics) |

---

## Contributing

If you have a worked example of an invariant test, contract gate, or eval that others could learn from, contributions are welcome. Each example should be self-contained with its own README explaining what it catches and how to run it.
