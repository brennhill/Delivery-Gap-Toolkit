# Metrics — The Verification Triangle

The Verification Triangle has three vertices: spec quality, eval quality, and cost. Each vertex is measured through a family of metrics. If any vertex is weak, the system fails — strong specs with weak evals leave gaps, strong evals without cost measurement hide degradation, and cost measurement without specs has nothing to measure against.

This directory contains scripts that measure all three vertices from your git history and CI data.

---

## The Three Vertices

### Spec Quality — "Are we building the right thing?"

Spec quality measures whether work is guided by explicit intent before AI generates code. Without a spec, every downstream gate is checking against nothing.

| Metric | What it tells you | Script |
|--------|------------------|--------|
| **Spec coverage** | % of merged PRs with a valid linked spec | `spec-quality/spec-coverage.py` |
| **Rework rate by spec status** | Whether specs actually reduce waste | `spec-quality/rework-by-spec.py` |

Research basis: CodeScout found that converting underspecified problems into detailed specs improved resolution rates by 20%. Montgomery et al. showed ambiguity and incompleteness remain central quality concerns with downstream delivery effects.

### Eval Quality — "Are defects caught early enough?"

Eval quality measures whether automated gates are absorbing verification load and whether human reviewers are sustainable.

| Metric | What it tells you | Script |
|--------|------------------|--------|
| **Machine catch rate** | % of changes that pass gates, review, and survive 14 days | `eval-quality/machine-catch-rate.py` |
| **Reviewer-minutes per accepted change** | Whether human review load is scaling | `eval-quality/reviewer-minutes.py` |
| **Review cycle count** | Pre-merge friction per PR (review rounds before merge) | `eval-quality/review-cycles.py` |
| **Time-to-merge** | How long changes spend in the verification pipeline | `eval-quality/time-to-merge.py` |
| **Defect escape rate** | % of bugs reaching production | `eval-quality/defect-escape-rate.py` |
| **Change fail rate** | % of deploys causing failure (DORA) | `eval-quality/change-fail-rate.py` |

Research basis: SmartBear/Cisco (2,500 reviews, 3.2M lines) — review effectiveness collapses after 400 lines and 60 minutes. CodeRabbit found AI-authored code carries 1.7x more issues. DORA established change fail rate as a core delivery metric.

**Important:** Bucket by PR size when comparing spec'd vs unspec'd metrics. Without size bucketing, the comparison is confounded by complexity — small tasks naturally rework less regardless of spec status. Use `gh pr view --json additions,deletions` and split into small (<100 lines), medium (100-500), and large (500+).

### Cost — "How much does each trusted change actually cost?"

Cost measures the full unit economics of delivery, not just the model bill. The formula:

```
cost per accepted change = (model + infra + human engineering + review + rework) / accepted changes
```

"Human engineering" includes discussion, whiteboarding, spec writing, prompting, and context preparation — not just time at the keyboard. This is often the largest hidden cost.

| Metric | What it tells you | Script |
|--------|------------------|--------|
| **Cost per accepted change** | Full unit cost of trusted delivery | `cost-per-accepted-change/cost-calculator.py` |
| **Rework detection** | Which changes were reverted/patched within 14 days | `rework-detection/rework-detector.py` |
| **Delivery baseline** | Merged PRs, reverts, cycle time, PR size | `delivery-baseline/delivery-metrics.sh` |

---

## The Pipeline

These scripts chain together. The rework detector feeds real data into the cost calculator, which generates a branded HTML report with warnings:

```bash
# 1. Detect rework from git history
python rework-detection/rework-detector.py --lookback 30 --json rework.json

# 2. Measure spec coverage
python spec-quality/spec-coverage.py --repo owner/repo --json spec.json

# 3. Measure machine catch rate
python eval-quality/machine-catch-rate.py --repo owner/repo --json catches.json

# 3b. Measure pre-merge friction (zero-instrumentation, GitHub API only)
python eval-quality/review-cycles.py --repo owner/repo --json cycles.json
python eval-quality/time-to-merge.py --repo owner/repo --json ttm.json

# 4. Calculate cost per accepted change with HTML report
python cost-per-accepted-change/cost-calculator.py \
  --json costs.json \
  --from-rework rework.json \
  --html report.html
```

---

## Agent Cost Tracking

For agentic workflows, the equivalent of "cost per accepted change" is **iteration budget per run**: tokens, retries, tool calls, and compute consumed per task. Track this with per-run cost tools like Stripe's `@stripe/token-meter`, LangSmith, AgentOps, or Langfuse. Set hard caps on turns, tokens, and wall-clock time per agent run. See [`../gates/agent-monitoring/README.md`](../gates/agent-monitoring/README.md#step-6-track-iteration-budget-per-run) for SDK defaults and implementation details.

---

## Further Reading

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Production monitoring + automated evals + human review
- [DORA: Software delivery performance metrics](https://dora.dev/guides/dora-metrics/) — The industry standard for delivery measurement
- [Faros AI: AI Productivity Paradox](https://www.faros.ai/ai-productivity-paradox) — PR volume up 98%, net throughput zero
