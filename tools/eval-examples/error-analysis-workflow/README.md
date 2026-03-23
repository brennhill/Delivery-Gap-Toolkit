# Error Analysis Workflow

Step 0 before building any eval gate: look at your actual failures first.

Most teams skip this step. They jump straight to adding linters, gates, or LLM-as-judge evals based on what they *think* will fail. The result is gates that catch theoretical problems while real failures slip through unchecked.

This workflow is adapted from Hamel Husain's evaluation framework: manually review real outputs, categorize the failure modes you actually see, then build domain-specific evals targeting those modes.

## The process

### 1. Collect 50-100 real outputs

Pull recent AI-generated outputs from your system. Not cherry-picked examples — a random sample from the last 1-2 weeks.

```bash
# Example: export recent AI-assisted PRs
python collect_samples.py --repo owner/repo --count 100 --output samples.jsonl
```

### 2. Categorize failures manually

Review each output. For every problem you find, tag it with a failure category. Don't use predefined categories — let them emerge from the data.

```bash
# Interactive review tool
python review_samples.py --input samples.jsonl --output reviewed.jsonl
```

Common categories that emerge (yours will differ):

| Category | Example |
|----------|---------|
| **Silent rename** | AI renames a field/function, all local tests pass, downstream breaks |
| **Confident fabrication** | AI invents a plausible API, library, or config option that doesn't exist |
| **Scope creep** | AI adds "helpful" features not in the spec |
| **Copy-paste drift** | AI duplicates code with slight variations instead of extracting |
| **Missing edge case** | Happy path works, error/null/empty/concurrent case is wrong |
| **Security blindspot** | No input validation, hardcoded secrets, SQL injection |

### 3. Prioritize by frequency and severity

```bash
# Summarize categories from reviewed samples
python summarize.py --input reviewed.jsonl
```

Output:
```
Failure categories (sorted by frequency):
  missing_edge_case:       23 occurrences (14 high-severity)
  scope_creep:             18 occurrences (4 high-severity)
  copy_paste_drift:        15 occurrences (2 high-severity)
  confident_fabrication:    9 occurrences (9 high-severity)
  silent_rename:            7 occurrences (7 high-severity)
  security_blindspot:       3 occurrences (3 high-severity)
```

### 4. Build one eval per top failure mode

For each of your top 3-5 failure categories, build a binary pass/fail eval:

- **missing_edge_case** → invariant test (see `invariant-examples/`)
- **silent_rename** → contract test (see `contract-examples/`)
- **confident_fabrication** → existence check (see sloppy-joe for dependencies; grep for undefined imports in code)
- **scope_creep** → diff-size gate + spec linkage check
- **copy_paste_drift** → duplication detector (jscpd, PMD CPD)
- **security_blindspot** → policy gate (semgrep, bandit)

### 5. Repeat quarterly

Failure modes shift as your team and tools evolve. Run this analysis every quarter to check whether your gates are still catching what actually fails.

## Files

| File | What it does |
|------|-------------|
| `collect_samples.py` | Pulls AI-assisted PR diffs from GitHub |
| `review_samples.py` | Interactive CLI for categorizing failures |
| `summarize.py` | Aggregates and ranks failure categories |

## Why this matters

Without error analysis, you build gates based on assumptions. With it, you build gates based on evidence. The difference is whether your machine catch rate improves or just your gate count.

This is the eval quality equivalent of the spec quality principle: understanding before action.
