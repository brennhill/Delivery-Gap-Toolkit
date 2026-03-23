# Eval Examples

Tools and patterns for building domain-specific evaluations that catch the failures your system actually produces — not generic quality metrics.

## Start here: Error Analysis

Before building any eval, run the error analysis workflow to discover what actually fails in your system:

| Step | Tool | What it does |
|------|------|-------------|
| 1 | [error-analysis-workflow/](error-analysis-workflow/) | Collect, review, and categorize 50-100 real AI outputs |
| 2 | Build targeted evals | Use the categories to pick which gate type to build |

## Eval patterns

| Pattern | Example | When to use |
|---------|---------|-------------|
| **LLM-as-judge** | [llm-as-judge/](llm-as-judge/) | Outputs that need semantic evaluation (support responses, generated docs, summaries) |
| **Contract test** | [../contract-examples/](../contract-examples/) | API responses that must match a documented schema |
| **Invariant test** | [../invariant-examples/](../invariant-examples/) | Business rules that must hold under all conditions |

## The principle

Generic metrics (ROUGE, BERTScore, "similarity score", "helpfulness") miss domain-specific failures. A customer support response can score high on fluency while giving dangerously wrong policy information.

The error analysis workflow tells you *which* failures to target. The eval patterns give you *how* to catch them. Together, they close the gap between "this output was generated" and "this output is trustworthy."

Hamel Husain calls evaluations "living product requirements documents." When you find a new failure mode in production, add a criterion. When a criterion never fires, investigate whether it's perfectly placed or testing something that can't fail.
