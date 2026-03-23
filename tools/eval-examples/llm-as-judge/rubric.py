"""
Domain-specific grading rubric for customer support responses.

Each criterion targets a specific failure mode discovered through
error analysis — not a generic quality dimension.

To build your own:
1. Review 50-100 real outputs from your system
2. Categorize the failures you actually see
3. Write a binary pass/fail criterion for each category
4. Add new criteria when new failure modes appear in production
"""

RUBRIC = [
    {
        "name": "policy_accuracy",
        "description": "Response accurately reflects actual company policy",
        "fail_examples": [
            "States a 60-day refund window when policy is 30 days",
            "Claims free shipping exists when minimum order applies",
            "Invents a loyalty program that doesn't exist",
        ],
        "prompt": (
            "Does this response accurately reflect the company policies provided in the context? "
            "Answer PASS if all policy references are accurate, FAIL if any policy is stated incorrectly "
            "or if a policy is invented that doesn't exist in the context."
        ),
    },
    {
        "name": "completeness",
        "description": "Response includes all information the customer needs to act",
        "fail_examples": [
            "Says 'you can return it' but doesn't explain how",
            "References a form but doesn't link to it",
            "Answers the surface question but misses the underlying need",
        ],
        "prompt": (
            "Does this response give the customer enough information to take the next step "
            "without needing to ask a follow-up? Answer PASS if actionable, FAIL if the customer "
            "would need to ask again to proceed."
        ),
    },
    {
        "name": "no_hallucinated_capabilities",
        "description": "Response doesn't promise features or actions the system can't perform",
        "fail_examples": [
            "Offers to transfer to a department that doesn't exist",
            "Promises a callback when the system doesn't support callbacks",
            "Says 'I've updated your account' when it has no write access",
        ],
        "prompt": (
            "Does this response promise any action, feature, or capability that is not listed "
            "in the available tools/capabilities context? Answer PASS if all promises are "
            "backed by real capabilities, FAIL if any promise is unsupported."
        ),
    },
    {
        "name": "safe_uncertainty",
        "description": "When uncertain, response acknowledges uncertainty rather than guessing",
        "fail_examples": [
            "Confidently states a price that isn't in the context",
            "Gives a specific date without source data",
            "Answers a question outside its domain as if it were authoritative",
        ],
        "prompt": (
            "If the response addresses a topic not fully covered by the provided context, "
            "does it acknowledge the limitation or escalate? Answer PASS if uncertainty is "
            "handled appropriately, FAIL if the response presents uncertain information as fact."
        ),
    },
]


def format_rubric_for_prompt() -> str:
    """Format the rubric as a structured prompt for the judge LLM."""
    lines = ["Grade this response against each criterion. For each, answer PASS or FAIL with a one-line reason.\n"]
    for i, criterion in enumerate(RUBRIC, 1):
        lines.append(f"{i}. **{criterion['name']}**: {criterion['prompt']}")
    lines.append("\nRespond in this exact format for each criterion:")
    lines.append("criterion_name: PASS|FAIL — reason")
    return "\n".join(lines)
