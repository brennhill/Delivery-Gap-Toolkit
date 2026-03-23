"""
LLM-as-judge eval runner.

Sends an AI-generated output + context + rubric to a judge LLM,
parses structured pass/fail grades per criterion.

Usage:
    python eval_judge.py
"""

import os
import re

from rubric import RUBRIC, format_rubric_for_prompt


def build_judge_prompt(context: str, response: str) -> str:
    """Build the full prompt for the judge LLM."""
    return f"""You are evaluating a customer support AI response for quality.

## Company context and policies
{context}

## AI-generated response being evaluated
{response}

## Grading instructions
{format_rubric_for_prompt()}"""


def parse_grades(judge_output: str) -> dict[str, dict]:
    """Parse structured grades from judge LLM output.

    Expected format per line:
        criterion_name: PASS|FAIL — reason
    """
    grades = {}
    for criterion in RUBRIC:
        name = criterion["name"]
        pattern = rf"{name}:\s*(PASS|FAIL)\s*[—-]\s*(.*)"
        match = re.search(pattern, judge_output, re.IGNORECASE)
        if match:
            grades[name] = {
                "result": match.group(1).upper(),
                "reason": match.group(2).strip(),
            }
        else:
            grades[name] = {
                "result": "ERROR",
                "reason": "Could not parse grade from judge output",
            }
    return grades


def run_eval(context: str, response: str, judge_fn=None) -> dict:
    """Run the eval. Pass judge_fn for testing without an API key."""
    prompt = build_judge_prompt(context, response)

    if judge_fn:
        judge_output = judge_fn(prompt)
    else:
        import anthropic

        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        judge_output = message.content[0].text

    grades = parse_grades(judge_output)

    passed = all(g["result"] == "PASS" for g in grades.values())
    failed_criteria = [name for name, g in grades.items() if g["result"] != "PASS"]

    return {
        "passed": passed,
        "grades": grades,
        "failed_criteria": failed_criteria,
    }


# --- Demo ---

SAMPLE_CONTEXT = """
Refund policy: 30-day return window from delivery date. Items must be unused.
Shipping: Free on orders over $50. Standard shipping $5.99 for orders under $50.
Support hours: Monday-Friday 9am-5pm EST.
Available actions: look up order status, initiate return, apply discount code.
"""

SAMPLE_GOOD_RESPONSE = """
I can help you with your return. Since your order was delivered 12 days ago,
you're within our 30-day return window. The item needs to be unused.

Here's how to proceed:
1. I'll initiate the return for order #4521
2. You'll receive a prepaid shipping label by email within 1 hour
3. Drop the package at any UPS location
4. Refund processes within 5-7 business days after we receive the item

Would you like me to start the return process?
"""

SAMPLE_BAD_RESPONSE = """
Absolutely! I've gone ahead and processed your refund of $89.99 back to your
credit card. You should see it within 24 hours. Our 60-day satisfaction
guarantee means you don't even need to return the item — just keep it!
I've also added 500 loyalty points to your account as an apology for
the inconvenience.
"""

if __name__ == "__main__":
    print("=== Evaluating GOOD response ===\n")
    result = run_eval(SAMPLE_CONTEXT, SAMPLE_GOOD_RESPONSE)
    for name, grade in result["grades"].items():
        status = "PASS" if grade["result"] == "PASS" else "FAIL"
        print(f"  {status}  {name}: {grade['reason']}")
    print(f"\n  Overall: {'PASSED' if result['passed'] else 'FAILED'}\n")

    print("=== Evaluating BAD response ===\n")
    result = run_eval(SAMPLE_CONTEXT, SAMPLE_BAD_RESPONSE)
    for name, grade in result["grades"].items():
        status = "PASS" if grade["result"] == "PASS" else "FAIL"
        print(f"  {status}  {name}: {grade['reason']}")
    print(f"\n  Overall: {'PASSED' if result['passed'] else 'FAILED'}")
    print(f"  Failed: {', '.join(result['failed_criteria'])}")
