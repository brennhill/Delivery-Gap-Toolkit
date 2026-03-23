---
name: review
description: Three parallel code review agents (correctness, performance, security) against the current diff
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Grep, Agent
---

# Multi-Pass Code Review

Run three review agents **in parallel** against the current diff. Each agent has a dedicated perspective and reviews independently.

## Get the diff

Run `git diff` to get unstaged changes. If empty, run `git diff --cached` for staged changes. If both are empty, run `git diff HEAD~1` to review the last commit. Tell the user which diff you are reviewing.

If the user passed an argument (a file path, PR number, or branch name), use that to scope the diff instead.

Save the diff to a temp file so agents can read it.

## Launch three agents in parallel

Launch all three agents in a **single message** so they run concurrently. Each agent should read the diff file.

### Agent 1: Correctness & Logic

```
Review this code diff from a correctness perspective, focusing on CORRECTNESS AND LOGIC issues.

Read the diff at: {diff_file_path}

Focus exclusively on:
- Off-by-one errors, boundary conditions, edge cases
- Null/undefined handling, empty collections, division by zero
- Missing error handling on I/O, network calls, and parsing
- Thread safety, race conditions, deadlocks
- Broken invariants (idempotency violations, double-writes)
- Wrong assumptions about data shapes or upstream behavior

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

If you find no issues, say "No correctness issues found." Do not invent problems.
Be harsh — this code is going to production.
```

### Agent 2: Performance & Maintainability

```
Review this code diff from a systems perspective, focusing on PERFORMANCE AND MAINTAINABILITY issues.

Read the diff at: {diff_file_path}

Focus primarily on:
- N+1 queries, unbounded loops over external data
- Resource leaks (unclosed connections, file handles, streams)
- Algorithmic inefficiency (O(n^2) where O(n) is possible)
- Unnecessary complexity, dead code, unreachable branches
- Code duplication that will cause maintenance drift
- Readability issues that will cause review burden on future changes

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

If you find no issues, say "No performance or maintainability issues found." Do not invent problems.
```

### Agent 3: Security & Scope

```
Review this code diff from a security perspective, focusing on SECURITY AND SCOPE issues.

Read the diff at: {diff_file_path}

Focus primarily on:
- SQL injection, XSS, command injection, path traversal
- Hardcoded credentials, API keys, secrets
- Insufficient input validation at system boundaries
- Authentication/authorization gaps
- Data exposure (PII in logs, sensitive data in error messages)
- Dependency vulnerabilities (known-bad versions)
- Scope violations (code touching resources it should not)

Prioritize security and scope issues, but flag anything else you notice.

After reviewing individual issues, look for ARCHITECTURAL CONSOLIDATION opportunities:
- Are multiple vulnerabilities symptoms of the same missing security boundary? (e.g., repeated input sanitization that a validation middleware would centralize)
- Would a structural change (input validation layer, output encoding pipeline, secrets management pattern) prevent an entire class of vulnerabilities going forward?
- Flag these as "Architecture recommendation" with the class of vulnerabilities it would prevent.

For each issue found, report:
1. File and line number
2. The specific vulnerability
3. Severity (Critical / High / Medium / Low)
4. Exploit scenario or impact
5. Suggested fix

If you find no issues, say "No security issues found." Do not invent problems.
```

## Summary

After all three agents complete, consolidate their findings and print:

### Consolidated Results

- **Correctness & Logic:** {count} issues
- **Performance & Maintainability:** {count} issues
- **Security & Scope:** {count} issues

List all issues organized by priority (P0/P1/P2), then give a one-line verdict:
- **PASS** — no critical issues
- **REVIEW** — issues found but none critical
- **BLOCK** — critical issues that must be fixed before merge
