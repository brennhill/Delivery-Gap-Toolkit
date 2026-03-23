# Spec Best Practices

A spec is the document that makes verification possible. Without it, every gate downstream is checking against nothing.

## What a spec must contain

1. **User-facing change** — what the user will see or experience differently
2. **Non-negotiable constraints** — what must never break (e.g., "no double charges", "response under 200ms")
3. **Out of scope** — what this change explicitly does not do
4. **Architectural boundaries** — which services, databases, and APIs are touched
5. **Acceptance criteria** — how you know it works, stated as testable conditions

## What a spec is not

- A Jira ticket title
- A one-line prompt
- A "we'll figure it out as we go" placeholder
- A copy of the PR description written after the code

## When to write a spec

Before AI-assisted implementation begins on any change above Risk Tier 1. The spec exists so the AI has constraints. Without constraints, the AI fills every gap with confident fiction.

## Enforcement

PRs without a linked spec for Risk Tier 2+ changes go back before review starts. This is a process decision, not a technical one:

- Add a "Spec Link" field to your PR template (required, not optional)
- CI can check: does the field contain a valid URL or ticket ID?
- Placeholders like "TBD", "pending", or empty fields count as no-spec

## Spec quality attributes

Existence is not enough. A spec that says "handle errors appropriately" is not a spec. Four decades of requirements engineering research (IEEE 830 through Montgomery et al.'s systematic review of 105 empirical studies) converge on four measurable quality attributes:

1. **Completeness** — all required sections present, edge cases addressed, acceptance criteria defined
2. **Unambiguous** — no vague terms ("fast enough", "user-friendly", "handle errors appropriately")
3. **Consistent** — no contradictions between sections (e.g., scope says X is excluded, acceptance criteria tests for X)
4. **Testable** — you can write a pass/fail check from the acceptance criteria as written

If you cannot write a deterministic test from the spec, the spec is not finished.

Nazir et al. found that automated ambiguity detection outperforms human review — humans miss syntactic ambiguity at high rates. LLMs (GPT-4 specifically) outperform other approaches for identifying inconsistency, ambiguity, and missing elements in requirements. This means you can use an LLM to grade your spec *before* you use an LLM to write the code.

## How to know if your specs are working

Run `spec-coverage.py` to measure coverage. Then run `rework-by-spec.py` to compare rework rates. If spec'd changes have the same rework rate as unspec'd changes, your specs are performative — they exist but don't constrain anything useful.

**Bucket by PR size to control for complexity.** Use lines changed (`gh pr view --json additions,deletions`) to split PRs into small (<100 lines), medium (100-500), and large (500+). Compare spec'd vs unspec'd rework rate, review cycle count, and time-to-merge within each bucket. Without bucketing, the global comparison is confounded — small tasks naturally rework less regardless of spec status. The spec signal is strongest in medium and large changes, where ambiguity has room to compound. If specs appear to help globally but not within size buckets, the benefit is just task-difficulty selection bias, not spec quality.

## The one-page spec template

See [templates/specs/01-one-page-spec-template.md](../../templates/specs/01-one-page-spec-template.md) for a ready-to-use template.

## Research basis

- CodeScout (arXiv:2603.05744): converting underspecified problem statements into detailed specifications improved resolution rates by 20% on SWE-bench Verified
- Montgomery et al. (2022): systematic review of 105 empirical studies confirms completeness, ambiguity, consistency, and correctness as the four most-studied spec quality attributes
- Stephen & Mit (2020): IEEE 830-based evaluation framework for spec quality — completeness, correctness, preciseness, consistency
- Nazir et al. (2021): automated ambiguity detection outperforms human review; Clarity Score metric for ambiguous term frequency
- LLMs in Requirements Engineering (2025): GPT-4 outperforms other models for identifying inconsistency, ambiguity, and missing elements
- Albayrak et al.: incomplete requirements force engineers to fill gaps with assumptions, pushing risk downstream
