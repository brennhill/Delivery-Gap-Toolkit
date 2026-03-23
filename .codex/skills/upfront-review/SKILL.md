---
name: upfront-review
description: Grade a specification against UPFRONT's machine-usability rubric — completeness, ambiguity, consistency, testability
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Grep, Glob
---

# UPFRONT Spec Review

Grade a specification against the UPFRONT machine-usability rubric. If the user provides a file path, read that file. If no argument is provided, look for SPEC.md, spec.md, requirements.md, or .specify/spec.md in the current directory.

## Step 1: Detect the Format

Check for these signals in order. Use the first match:

- **Spec Kit**: contains `FR-001` or `SC-001` patterns, or `Priority: P[0-3]`, or `.specify/` directory exists
- **Kiro**: contains `THE SYSTEM SHALL` (EARS syntax), or `.kiro/specs/` directory exists, or has `requirements.md` + `design.md` + `tasks.md`
- **OpenSpec**: contains `ADDED Requirements` or `MODIFIED Requirements`, or `.openspec/` directory exists
- **Delivery Gap**: contains `## Constraints` AND (`Contract check:` or `Invariant check:` or `## Acceptance criteria`)
- **RFC/Design Doc**: contains `## Motivation` or `## Alternatives Considered` or `## Decision`
- **Freeform**: none of the above match

Tell the user which format was detected. This determines which sections count toward completeness.

## Step 2: Score on Four Attributes

### 1. Completeness (30%)

For the detected format, check which machine-usable sections are present. Only count sections the format is expected to have in the denominator. WARN (but don't penalize) for any absent section from the full list.

**Full list of machine-usable sections (highest to lowest impact):**

| Section | What to look for | Impact |
|---------|-----------------|--------|
| Acceptance criteria | Given/When/Then, EARS WHEN/SHALL, contract/invariant/policy, MUST statements | High |
| Edge cases | Enumerated boundary conditions with expected behavior | High |
| Constraints | Testable non-functional requirements with thresholds | High |
| Scope boundaries | Explicit "out of scope" exclusions | High |
| Context anchors | References to existing files, patterns, modules | High |
| I/O contracts | Request/response shapes, schemas, type definitions | High |
| Architectural constraints | Testable boundaries (can grep for violations) | Medium |
| State transitions | Valid states, valid transitions, terminal states | Medium |
| Error contract | Shape and codes of error responses | Medium |
| Data model | Entity definitions, relationships, field types | Medium |
| Side effects | Events, notifications, external calls, audit trails | Medium |

**Not scored (note if present but do not count in denominator):**
Success criteria, priority levels, motivation, alternatives considered, user satisfaction metrics.

**Format-specific expected sections:**

| Format | Expected sections (count in denominator) |
|--------|----------------------------------------|
| Spec Kit | Acceptance criteria, edge cases, requirements, entities |
| Kiro | Acceptance criteria (EARS), functional reqs, non-functional reqs, data reqs |
| OpenSpec | Acceptance criteria (Given/When/Then), requirements |
| Delivery Gap | Acceptance criteria, constraints, scope, context anchors, ownership |
| RFC | Requirements, constraints, scope |
| Freeform | Acceptance criteria, scope (minimal denominator) |

### 2. Ambiguity (30%)

Search machine-usable sections for these terms. Flag each with its line and a **concrete suggestion for what to write instead**:

**Vague terms to flag:**
appropriate, appropriately, fast, fast enough, user-friendly, properly, correctly, reasonable, as needed, as appropriate, etc., and so on, handle errors, handle gracefully, should work, simple, easy, intuitive, flexible, robust, scalable, secure, efficient, performant, clean, modular, maintainable, good, better, best practice, industry standard, state of the art, when possible, if applicable, as much as possible, adequate, sufficient, normal, typical, usual

**Also flag:**
- Acceptance criteria that cannot be converted to a pass/fail test. For each, suggest a rewrite.
- Constraints without measurable thresholds. Suggest: "What number makes this pass or fail?"
- "should" where "MUST" is meant. Suggest: "If this is a requirement, use MUST. If it's optional, use MAY."

**Scoring:** Normalized by spec length to avoid penalizing thoroughness.
```
raw_deductions = (5 × vague_terms_in_high_impact) + (3 × vague_terms_in_medium_impact)
words = total words in machine-usable sections (floor 100)
ambiguity = max(0, 100 - (raw_deductions / words × 100))
```

### 3. Testability (25%)

Extract every stated goal, requirement, or feature claim. For each:
- Check whether at least one acceptance criterion covers it
- If missing, flag it with: "**Goal without test:** '[goal text]' — add an acceptance criterion like: Given [setup], When [action], Then [expected result]"

Report: "X of Y goals have matching acceptance criteria"

**Also check:**
- Can each acceptance criterion be implemented as an automated test? If not, suggest how.
- Are edge cases specific enough to generate test cases? If "handle edge cases" appears, suggest 3 concrete edge cases.
- Do architectural constraints have a verification method? Suggest: "You could verify this with: grep -r 'import.*db' src/handlers/"

**Scoring:** `(goals_with_criteria / total_goals) * 100`. If no goals are stated, score 0.

### 4. Consistency (15%)

Cross-reference sections for contradictions:
- Scope says "out of scope: X" but acceptance criteria test for X → flag both locations
- Constraint says "under 200ms" but another section says "no performance requirements" → flag both
- Requirements that contradict each other → flag both with the contradiction explained
- State transitions that allow impossible paths → flag the specific transition

**Scoring:** Start at 100. Deduct 25 per contradiction. Floor at 0.

## Step 3: Output

```
## UPFRONT Spec Review: [filename]

**Format detected:** [format name]
**Sections found:** [list of detected sections]

### Scores
| Attribute | Score | Details |
|-----------|-------|---------|
| Completeness | XX/100 | N of M expected sections present |
| Ambiguity | XX/100 | N vague terms flagged |
| Testability | XX/100 | N of M goals have acceptance criteria |
| Consistency | XX/100 | N contradictions found |
| **Overall** | **XX/100** | weighted: completeness×0.3 + ambiguity×0.3 + testability×0.25 + consistency×0.15 |
```

### For each issue, provide actionable guidance:

**DO NOT** just say "missing section" or "ambiguity found." That's useless.

**DO** say exactly what to add and give an example. For every issue:
1. What's wrong (specific location)
2. Why it matters (what will go wrong if not fixed)
3. How to fix it (concrete example the user can adapt)

Example:

```
### Ambiguity: Line 14
> "The system should handle errors appropriately"

**Problem:** "Appropriately" is not testable. The AI will invent error handling
that looks reasonable but may not match your expectations.

**Fix — replace with specific behavior:**
> When a payment fails, the API MUST return 402 with body
> {"error": "payment_declined", "code": "PAY_002", "request_id": "<uuid>"}
> and log the failure to the audit trail with level WARN.

**Why:** This gives the AI an exact error code, response shape, and logging
requirement. The acceptance criterion writes itself.
```

Another example:

```
### Missing: Edge Cases

**Problem:** No edge cases section found. The AI will generate happy-path code
only. The first unusual input will break it.

**Fix — add 3-5 edge cases with expected behavior:**
> - What happens when [input] is empty? → Return 400 with EMPTY_INPUT error
> - What happens when [input] exceeds [limit]? → Return 413 with size in error body
> - What happens when [external service] is unreachable? → Retry 3x with exponential backoff, then return 503

**Why:** Each edge case generates a guard clause or error handler. Without them,
you'll find these bugs in code review or production.
```

### Warnings (not scored)

For every machine-usable section that's absent (regardless of format), emit a warning explaining what the user is leaving on the table:

- **No context anchors:** "Without reference files, the AI will invent its own patterns. Add: 'Follow the pattern in src/routes/users.ts' or 'Use the BaseRepository from src/db/base.ts'"
- **No I/O contracts:** "Without explicit shapes, the AI invents request/response formats. Add: 'POST /api/X — Request: {field: type}, Response: {field: type}'"
- **No side effects:** "The AI will implement the primary action but miss events, notifications, and audit logging. Add: 'When X happens, also: emit event Y, send notification Z, log to audit trail'"
- **No state transitions:** "If this feature involves stateful entities, the AI may allow invalid transitions. Add: 'Valid states: A → B → C. Terminal: D. B cannot go directly to D.'"
- **No error contract:** "Without a standard error shape, every function will invent its own. Add: 'All errors return {error: string, code: string, request_id: string}'"

### Verdict

- **PASS** (overall >= 70, no high-impact sections missing) — spec is ready for AI-assisted implementation
- **REVIEW** (overall 40-69, or 1-2 high-impact sections missing) — spec needs improvement but has a foundation
- **REWRITE** (overall < 40, or 3+ high-impact sections missing) — spec is not useful for AI-assisted implementation; better to fix the spec than to debug the AI output

End with: "Want me to help fix the [highest-priority issue]?"
