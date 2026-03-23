# Eval Quality Best Practices

Eval quality answers one question: are defects being caught early enough, and are machines absorbing enough of the verification load?

## The six eval metrics

### Machine catch rate

`changes_that_passed_gates_and_review_untouched_and_survived_14_days / total_changes`

This measures end-to-end pipeline trustworthiness — what percentage of changes your automated pipeline gets right without any human intervention. It has two complement metrics:

- **Human save rate** = changes that humans modified during review before merge / total changes
- **Escape rate** = changes that passed both gates AND human review but were rolled back within 14 days / total changes

All three sum to 100%. If machine catch rate is 85%, human save rate is 10%, and escape rate is 5%, your pipeline is trustworthy but your gates are missing 15% of problems (10% caught by reviewers, 5% caught by nobody).

Target: above 80%. Below 70% means your pipeline is producing more rework than it should — either gates are too weak or specs are too vague. Below 50% means the pipeline is not trustworthy and human review is doing most of the verification work.

How to improve:
- Add a gate tier you're missing (see the gate tooling by language)
- Make warning-only gates blocking
- Improve spec quality (vague specs produce code that passes gates but fails in review)
- Add AI code review (CodeRabbit, Anthropic Code Review, or the multi-pass review skill)
- Track the escape rate separately — if human save rate is high but escape rate is low, your reviewers are compensating for weak gates

### Reviewer-minutes per accepted change

`total_reviewer_minutes / accepted_changes`

Watch the trend, not the absolute number. If this is rising, your review layer is being overwhelmed by volume. If it's falling, your gates are absorbing more of the load.

Warning threshold: if median review exceeds 60 minutes, the SmartBear/Cisco research says effectiveness has already collapsed.

### Defect escape rate

`production_defects / (production_defects + pre_production_defects)`

Target: below 15%. Above 30% means most bugs are reaching production — your gates are not catching enough.

Requires issue tracker integration or manual labeling:
- Label bugs with where they were found: "production" or "found-in-review" / "found-in-ci"
- Count each bug once using first-finder-wins

What NOT to count as defects: style comments, formatting nits, flaky CI timeouts, duplicate findings.

### Change fail rate (DORA)

`failed_deployments / total_deployments`

DORA benchmarks:
- Elite: < 5%
- High: 5-10%
- Medium: 10-15%
- Low: > 15%

### Review cycle count

`review_rounds_before_merge`

Count distinct review rounds per PR. A round is a review submission (approved, changes requested, or commented). Available from the GitHub API with zero instrumentation: `gh pr view --json reviews`.

This is the clearest pre-merge signal of spec quality. Well-specced changes pass review in fewer rounds because the intent is unambiguous. If review cycle count is rising while spec coverage is flat, your specs are not detailed enough for reviewers (or agents) to evaluate against.

Target: median of 1-2 rounds. Above 3 consistently means specs are too vague or the review process has unclear standards.

### Time-to-merge

`merged_at - created_at`

How long changes spend in the verification pipeline. Available from the GitHub API: `gh pr view --json createdAt,mergedAt`. Report as median per period, not mean, to avoid skew from long-lived PRs.

Read alongside defect escape rate:
- Shorter time-to-merge + stable escape rate = pipeline getting more efficient
- Shorter time-to-merge + rising escape rate = pipeline getting sloppy
- Longer time-to-merge + stable escape rate = review bottleneck building

## Step 0: Error analysis before gate building

Before adding gates, look at what actually fails. Most teams skip this and build gates based on what they *think* will go wrong. The result: gates that catch theoretical problems while real failures slip through.

1. **Collect 50-100 real outputs** — random sample from the last 1-2 weeks, not cherry-picked
2. **Categorize failures manually** — let categories emerge from the data, don't use predefined lists
3. **Prioritize by frequency × severity** — your top 3-5 categories become your first gates
4. **Build one eval per failure mode** — targeted pass/fail checks, not generic quality scores

See [tools/eval-examples/error-analysis-workflow/](../../tools/eval-examples/error-analysis-workflow/) for runnable scripts that automate the collection and summarization steps.

Generic metrics (ROUGE, BERTScore, "similarity score") are the eval equivalent of measuring PR volume instead of accepted outcomes. They optimize a proxy, not the thing you care about. Domain-specific evals targeting your actual failure modes are what move the machine catch rate.

## Building gates that actually work

### Gates must block, not warn

A gate that logs a warning but doesn't fail the build is not a gate. It's a suggestion. Engineers will train themselves to ignore it within weeks.

### Audit quarterly

A gate that never fires is either perfectly placed or completely broken. Run the audit table from the Quality Gates chapter every quarter. If a tier scores "healthy" but your defect escape rate is rising, your audit criteria are wrong.

### The three invariant questions

Before shipping any feature, ask:
1. What must never happen twice?
2. What must always be true after this operation completes?
3. What breaks if operations run out of order?

If the answers are clear, they define your invariant tests. If they're not clear, the feature may not be understood well enough to ship safely.

## Official provider guides

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Production monitoring + automated evals + human review as a combined approach. Drift detection post-launch.
- [Anthropic: Building Effective AI Agents](https://resources.anthropic.com/building-effective-ai-agents) — End-to-end agent patterns with eval guidance.

## Research basis

- SmartBear/Cisco: 2,500 reviews, 3.2M lines. 70-90% defect discovery at 200-400 lines. Effectiveness collapses after 60 minutes.
- CodeRabbit: AI-authored code carries 1.7x more issues than human-authored code
- DORA: change fail rate and deployment rework rate as core delivery metrics
- CodeX-Verify (arXiv 2511.16708): multi-perspective review improves accuracy from 32.8% to 72.4%
