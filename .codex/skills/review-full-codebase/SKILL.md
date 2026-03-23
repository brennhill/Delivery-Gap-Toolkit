---
name: review-full-codebase
description: Deep three-agent codebase audit (correctness, performance, security) across all source files
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob, Agent
---

# Full Codebase Review

Run three review agents **in parallel** against the entire codebase. Each agent reads all source files and reviews independently from its dedicated perspective.

This is a deep audit — use it periodically (before releases, after major refactors, when onboarding to a new codebase), not on every PR. For diff-level review, use `/review` instead.

## Identify source files

Use Glob to find all source files in the project. Exclude:
- `node_modules/`, `.venv/`, `venv/`, `target/`, `dist/`, `build/`, `__pycache__/`
- Lock files, generated files, vendored dependencies
- Binary files, images, fonts

Tell the user how many source files were found and in which languages.

If the user passed an argument (a directory path or glob pattern), scope the review to that.

## Launch three agents in parallel

Launch all three agents in a **single message** so they run concurrently. Each agent prompt should instruct it to read all source files in the project.

### Agent 1: Correctness & Logic

```
Review the codebase at {project_dir} from a correctness perspective, focusing on CORRECTNESS AND LOGIC issues.

Read ALL source files in the project. This is a deep audit, not a diff review.

Focus exclusively on:
- Off-by-one errors in calculations or date/time math
- Null/None/undefined handling — what happens with missing data, empty inputs, zero values
- Edge cases: empty collections, boundary values, negative numbers, overflow
- Division by zero risks
- Error handling gaps — what fails silently vs what should fail loud
- Logic errors in core algorithms
- Data type mismatches or incorrect assumptions about input shapes
- Race conditions or ordering dependencies
- Broken invariants across function boundaries

Prioritize correctness and logic issues, but flag anything else you notice.

After reviewing individual issues, look for ARCHITECTURAL CONSOLIDATION opportunities:
- Are multiple bugs symptoms of the same missing abstraction? (e.g., repeated null checks that a type-safe wrapper would eliminate)
- Would a structural change (new type, validation layer, shared utility) prevent an entire class of bugs going forward?
- Flag these as "Architecture recommendation" with the class of bugs it would prevent.

For each issue found, report:
1. File and line number
2. The specific bug or edge case
3. What breaks (with an example if possible)
4. Suggested fix

Prioritize by severity. Be harsh — this is a deep audit.
If you find no issues, say "No correctness issues found." Do not invent problems.
```

### Agent 2: Performance & Maintainability

```
Review the codebase at {project_dir} from a systems perspective, focusing on PERFORMANCE AND MAINTAINABILITY issues.

Read ALL source files in the project. This is a deep audit, not a diff review.

Focus primarily on:
- N+1 queries or subprocess calls (one call per item in a loop)
- Unbounded loops over external data without pagination
- Resource leaks (unclosed connections, file handles, streams)
- Algorithmic inefficiency (O(n^2) where O(n) is possible)
- Memory usage patterns that scale poorly
- Unnecessary complexity, dead code, unreachable branches
- Code duplication that will cause maintenance drift
- Functions doing too many things (mixed I/O, calculation, and presentation)
- Missing abstractions that make the code harder to extend
- Anything that makes the code harder to maintain for a future contributor

Prioritize performance and maintainability, but flag anything else you notice.

After reviewing individual issues, look for ARCHITECTURAL CONSOLIDATION opportunities:
- Are there repeated patterns (e.g., multiple N+1 queries) that a shared data-fetching layer would eliminate?
- Would consolidating duplicated logic into a single module prevent future maintenance drift?
- Are there structural improvements (caching layer, connection pool, batch API) that would eliminate entire categories of performance issues?
- Flag these as "Architecture recommendation" with the class of issues it would prevent.

For each issue found, report:
1. File and line number
2. The specific concern
3. Impact (how bad is it in practice?)
4. Suggested improvement
```

### Agent 3: Security & Scope

```
Review the codebase at {project_dir} from a security perspective, focusing on SECURITY AND SCOPE issues.

Read ALL source files in the project. This is a deep audit, not a diff review.

Focus primarily on:
- Command injection via subprocess calls (are arguments properly escaped? shell=True?)
- SQL injection, XSS, template injection
- Path traversal in file operations
- Hardcoded credentials, API keys, secrets
- Insufficient input validation at system boundaries (user input, external APIs, file parsing)
- Authentication/authorization gaps
- Data exposure (PII in logs, sensitive data in error messages, secrets in HTML reports)
- Scope violations — does any function do something unexpected beyond its stated purpose?
- Dependency supply chain (unnecessary dependencies, known-vulnerable versions)
- Permission assumptions (what access does this code assume?)

Prioritize security and scope issues, but flag anything else you notice.

After reviewing individual issues, look for ARCHITECTURAL CONSOLIDATION opportunities:
- Are multiple vulnerabilities symptoms of the same missing security boundary? (e.g., repeated input sanitization that a validation middleware would centralize)
- Would a structural change (input validation layer, output encoding pipeline, secrets management pattern) prevent an entire class of vulnerabilities going forward?
- Flag these as "Architecture recommendation" with the class of vulnerabilities it would prevent.

For each issue found, report:
1. File and line number
2. The specific vulnerability or concern
3. Severity (Critical / High / Medium / Low)
4. Exploit scenario or impact
5. Suggested fix
```

## Summary

After all three agents complete, consolidate their findings into a single prioritized report:

### Consolidated Audit Results

- **Correctness & Logic:** {count} issues
- **Performance & Maintainability:** {count} issues
- **Security & Scope:** {count} issues

Organize all issues into priority tiers:

**P0 — Fix now** (blocks release, data corruption, security vulnerability)

| # | Issue | Source |
|---|-------|--------|
| ... | ... | Correctness/Performance/Security |

**P1 — Fix before sharing widely** (significant but not blocking)

| # | Issue | Source |
|---|-------|--------|

**P2 — Nice to have** (improvements, not bugs)

| # | Issue | Source |
|---|-------|--------|

Then ask: "Want me to fix the P0s and P1s?"
