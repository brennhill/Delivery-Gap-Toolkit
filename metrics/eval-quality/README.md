# Eval Quality Metrics

Tools for measuring whether your gates are catching defects and whether your review process is sustainable.

## Scripts

- **machine-catch-rate.py** — What percentage of changes pass all gates, survive review without modification, and remain in production for 14 days. Measures end-to-end pipeline trustworthiness. Also reports human save rate and escape rate (all three sum to 100%).
- **reviewer-minutes.py** — How long humans spend reviewing each change. Pulls review timestamps from GitHub API.
- **review-cycles.py** — Review rounds before merge per PR. The clearest pre-merge signal of spec quality — well-specced changes pass in fewer rounds. Pulls from `gh pr view --json reviews`.
- **time-to-merge.py** — Time from PR creation to merge. Reports median per period. Read alongside defect escape rate: shorter + stable = efficient, shorter + rising = sloppy. Pulls from `gh pr view --json createdAt,mergedAt`.
- **defect-escape-rate.py** — What percentage of bugs reach production vs caught pre-prod. Supports GitHub Issues (with labels) or manual input for Jira/Linear.
- **change-fail-rate.py** — DORA metric: what percentage of deployments cause production failure. Supports GitHub Actions, GitHub Deployments API, or manual input.

## Quick Start

```bash
# Machine catch rate
python machine-catch-rate.py --repo owner/repo

# Reviewer-minutes per accepted change
python reviewer-minutes.py --repo owner/repo

# Review cycles per PR
python review-cycles.py --repo owner/repo

# Time-to-merge (median)
python time-to-merge.py --repo owner/repo

# Defect escape rate (GitHub Issues with labels)
python defect-escape-rate.py --repo owner/repo

# Defect escape rate (manual, for Jira/Linear users)
python defect-escape-rate.py --production-bugs 5 --preprod-bugs 23

# Change fail rate (GitHub Actions)
python change-fail-rate.py --repo owner/repo --workflow deploy.yml

# Change fail rate (manual)
python change-fail-rate.py --total-deploys 120 --failed-deploys 8
```

See [eval_best_practices.md](eval_best_practices.md) for guidance on building effective eval gates.
