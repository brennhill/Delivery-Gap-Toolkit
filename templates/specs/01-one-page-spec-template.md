# The Context-Anchor Spec (Delivery Spec Template)

> Sections marked **🤖 Machine** are scored by quality tools and consumed directly by AI agents during task execution.
> Sections marked **👤 Human** provide context for reviewers and stakeholders — AI reads them but they are not scored.
>
> Human sections come first to set the stage. Machine sections come last where they sit in the AI's most recent context window.

---

## 👤 1) Context: "For Whom" and "Why Now"
- Feature:
- User/problem:
- For whom:
- Why now:

## 👤 2) Success Criteria (measurable)
*Post-launch outcomes — how humans judge whether the feature succeeded. Not machine-verifiable from the spec.*
- Performance: (e.g., "p95 response time under 200ms")
- Adoption: (e.g., "80% of eligible users complete the flow")
- Quality: (e.g., "error rate below 0.1%")

## 👤 3) Ownership
- DRI:
- Reviewers:
- Decision date:

## 👤 4) Rollback Plan
- Trigger signal:
- Method: (Toggle/Revert/Fallback)
- Owner:

---

## 🤖 5) Model Anchors: "Where the AI should look"
*List specific files or docs the AI should be pinned to for context.*
- System Docs:
- Reference Code Patterns: (e.g., `src/auth/handler.ts`)
- API Specs:

## 🤖 6) Key Entities
*Shared vocabulary — prevents the AI from inventing its own names.*
- **[Entity]**: [What it represents, key attributes, relationships]
- **[Entity]**: [What it represents, key attributes, relationships]

## 🤖 7) Scope Boundaries
- In scope:
- Explicit Non-goals: (Stop the AI from inventing work here)

## 🤖 8) Constraints and Non-negotiables
- Security:
- Reliability/SLA:
- Compliance/policy:

## 🤖 9) Style and Architecture Rules
*Conventions the AI must follow — module boundaries, error patterns, naming.*
- Module boundaries:
- Error/logging conventions:

## 🤖 10) Error Contract
*What does failure look like? Prevents the AI from inventing error shapes per function.*
- Error response shape: (e.g., `{"error": "<code>", "message": "<detail>"}`)
- Expected error codes:
- Retry behavior:

## 🤖 11) Edge Cases
*What happens when things go wrong? Prevents the AI from ignoring boundary conditions.*
- What happens when [empty input / zero value]?
- What happens when [unauthorized / expired]?
- What happens when [concurrent / duplicate]?

## 🤖 12) Acceptance criteria (deterministic)
*These are your eval definitions. When a criterion here changes, the corresponding gate must update. The spec and the eval are the same artifact at different levels of formality.*

1. Contract check:
2. Invariant check:
3. Policy check:

Eval owner: *(same as DRI unless delegated — the person who updates these when requirements change)*
