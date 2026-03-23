"""
Tests for the LLM-as-judge eval.

Uses a mock judge function — no API key needed.
Tests verify that the rubric + parsing logic correctly
identifies known-good and known-bad responses.
"""

from eval_judge import run_eval, parse_grades

CONTEXT = """
Refund policy: 30-day return window from delivery date. Items must be unused.
Shipping: Free on orders over $50. Standard shipping $5.99 for orders under $50.
Support hours: Monday-Friday 9am-5pm EST.
Available actions: look up order status, initiate return, apply discount code.
"""


def mock_judge_all_pass(_prompt: str) -> str:
    return (
        "policy_accuracy: PASS — all policy references match the provided context\n"
        "completeness: PASS — response includes clear next steps\n"
        "no_hallucinated_capabilities: PASS — all actions are within listed capabilities\n"
        "safe_uncertainty: PASS — no uncertain claims made"
    )


def mock_judge_policy_fail(_prompt: str) -> str:
    return (
        "policy_accuracy: FAIL — states 60-day return window, actual policy is 30 days\n"
        "completeness: PASS — response includes next steps\n"
        "no_hallucinated_capabilities: FAIL — claims to have processed a refund, not a listed capability\n"
        "safe_uncertainty: FAIL — presents invented loyalty program as fact"
    )


def mock_judge_incomplete(_prompt: str) -> str:
    return (
        "policy_accuracy: PASS — policy references are correct\n"
        "completeness: FAIL — says return is possible but doesn't explain how to proceed\n"
        "no_hallucinated_capabilities: PASS — no unsupported promises\n"
        "safe_uncertainty: PASS — no uncertain claims"
    )


GOOD_RESPONSE = """
I can help you with your return. Since your order was delivered 12 days ago,
you're within our 30-day return window. I'll initiate the return for order #4521.
You'll receive a prepaid shipping label by email within 1 hour.
"""

BAD_RESPONSE = """
I've processed your refund already! Our 60-day satisfaction guarantee means
you don't need to return anything. I've also added 500 loyalty points
to your account.
"""

INCOMPLETE_RESPONSE = """
Yes, you can return that item since it's within the return window.
Let me know if you need anything else!
"""

CONFIDENT_WRONG_RESPONSE = """
Great news! Your item qualifies for our express refund program. The $89.99
will be back in your account within 2 hours. As a Gold member, you also
get free return shipping on all orders regardless of value.
"""


def test_passing_response_scores_high():
    result = run_eval(CONTEXT, GOOD_RESPONSE, judge_fn=mock_judge_all_pass)
    assert result["passed"] is True
    assert result["failed_criteria"] == []


def test_hallucinated_policy_fails():
    result = run_eval(CONTEXT, BAD_RESPONSE, judge_fn=mock_judge_policy_fail)
    assert result["passed"] is False
    assert "policy_accuracy" in result["failed_criteria"]
    assert "no_hallucinated_capabilities" in result["failed_criteria"]


def test_missing_required_info_fails():
    result = run_eval(CONTEXT, INCOMPLETE_RESPONSE, judge_fn=mock_judge_incomplete)
    assert result["passed"] is False
    assert "completeness" in result["failed_criteria"]


def test_rubric_catches_confident_wrong_answer():
    """The key test: a fluent, confident response that is factually wrong.
    Generic metrics (fluency, relevance) would score this high.
    Domain-specific rubric catches it."""
    result = run_eval(CONTEXT, CONFIDENT_WRONG_RESPONSE, judge_fn=mock_judge_policy_fail)
    assert result["passed"] is False
    assert "policy_accuracy" in result["failed_criteria"]


def test_parse_grades_handles_missing_criterion():
    """If the judge doesn't output a criterion, it's marked ERROR."""
    partial_output = "policy_accuracy: PASS — looks good"
    grades = parse_grades(partial_output)
    assert grades["policy_accuracy"]["result"] == "PASS"
    assert grades["completeness"]["result"] == "ERROR"


def test_parse_grades_case_insensitive():
    output = "policy_accuracy: pass — ok\ncompleteness: FAIL — missing steps\nno_hallucinated_capabilities: Pass — fine\nsafe_uncertainty: PASS — ok"
    grades = parse_grades(output)
    assert grades["policy_accuracy"]["result"] == "PASS"
    assert grades["completeness"]["result"] == "FAIL"
