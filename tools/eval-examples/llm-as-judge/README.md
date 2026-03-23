# LLM-as-Judge Eval

A runnable example of using an LLM to grade AI-generated outputs against domain-specific criteria. Demonstrates the pattern described in Husain's evaluation framework: build domain-specific evals targeting identified failure modes, not generic metrics.

## The problem

Generic metrics (ROUGE, BERTScore, "similarity score") don't catch domain-specific failures. A customer support response can score high on fluency and relevance while giving dangerously wrong refund policy information. You need evals that check *your* failure modes.

## The approach

1. **Start with error analysis** — review 50-100 real outputs, categorize the actual failure modes you see (see `error-analysis-workflow/` for the process)
2. **Write domain-specific rubrics** — binary pass/fail criteria targeting each failure mode
3. **Use an LLM to grade at scale** — sample 5-10% of production outputs, grade against the rubric
4. **Track scores over time** — drift detection, not a one-time audit

## Run

```bash
# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your-key

# Run the eval
python eval_judge.py

# Run the tests (no API key needed — uses mock)
pytest test_eval.py -v
```

## What the tests prove

| Test | What it checks |
|------|---------------|
| `test_passing_response_scores_high` | A correct, policy-compliant response passes all criteria |
| `test_hallucinated_policy_fails` | A response that invents a refund policy is caught |
| `test_missing_required_info_fails` | A response that omits required fields fails the completeness criterion |
| `test_rubric_catches_confident_wrong_answer` | A fluent, confident, wrong answer still fails (this is the failure mode generic metrics miss) |

## Files

| File | What it does |
|------|-------------|
| `rubric.py` | Domain-specific grading criteria (not generic "helpfulness") |
| `eval_judge.py` | Sends output + rubric to an LLM, parses structured pass/fail grades |
| `test_eval.py` | Tests using a mock judge to verify rubric logic without API calls |

## Key principle

The rubric is a living document. When you find a new failure mode in production, add a criterion. When a criterion never fires, investigate whether it's perfectly placed or testing something that can't fail. This is Husain's insight: evals are living product requirements documents.
