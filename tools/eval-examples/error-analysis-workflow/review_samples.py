"""
Interactive CLI for reviewing and categorizing AI-generated code failures.

Reads samples from collect_samples.py, presents each diff,
prompts for failure categories and severity.

Usage:
    python review_samples.py --input samples.jsonl --output reviewed.jsonl
"""

import argparse
import json
import sys

SUGGESTED_CATEGORIES = [
    "silent_rename",
    "confident_fabrication",
    "scope_creep",
    "copy_paste_drift",
    "missing_edge_case",
    "security_blindspot",
    "type_error",
    "wrong_api_usage",
    "test_gap",
    "no_issue",
]


def review_sample(sample: dict, index: int, total: int) -> dict:
    """Present a sample for review and collect categorization."""
    print(f"\n{'='*60}")
    print(f"PR #{sample['pr_number']}: {sample['title']}  ({index+1}/{total})")
    print(f"Author: {sample['author']}  Merged: {sample['merged_at']}")
    print(f"{'='*60}")

    # Show truncated diff
    diff_lines = sample["diff"].split("\n")
    if len(diff_lines) > 80:
        print("\n".join(diff_lines[:80]))
        print(f"\n... ({len(diff_lines) - 80} more lines, full diff in file)")
    else:
        print(sample["diff"])

    print(f"\nSuggested categories: {', '.join(SUGGESTED_CATEGORIES)}")
    categories_input = input("Failure categories (comma-separated, or 'skip'): ").strip()

    if categories_input.lower() == "skip":
        sample["review_status"] = "skipped"
        return sample

    categories = [c.strip() for c in categories_input.split(",") if c.strip()]
    if not categories:
        categories = ["no_issue"]

    severity = None
    if categories != ["no_issue"]:
        severity_input = input("Severity (low/medium/high): ").strip().lower()
        severity = severity_input if severity_input in ("low", "medium", "high") else "medium"

    notes = input("Notes (optional): ").strip()

    sample["review_status"] = "reviewed"
    sample["failure_categories"] = categories
    sample["severity"] = severity
    sample["notes"] = notes

    return sample


def main():
    parser = argparse.ArgumentParser(description="Review and categorize AI code samples")
    parser.add_argument("--input", required=True, help="Input JSONL from collect_samples.py")
    parser.add_argument("--output", default="reviewed.jsonl", help="Output JSONL with reviews")
    parser.add_argument("--resume", action="store_true", help="Skip already-reviewed samples")
    args = parser.parse_args()

    with open(args.input) as f:
        samples = [json.loads(line) for line in f if line.strip()]

    # Load existing reviews if resuming
    reviewed = {}
    if args.resume:
        try:
            with open(args.output) as f:
                for line in f:
                    if line.strip():
                        s = json.loads(line)
                        reviewed[s["pr_number"]] = s
        except FileNotFoundError:
            pass

    pending = [s for s in samples if s["pr_number"] not in reviewed]
    print(f"{len(samples)} total samples, {len(pending)} pending review")

    results = list(reviewed.values())

    try:
        for i, sample in enumerate(pending):
            result = review_sample(sample, i, len(pending))
            results.append(result)

            # Save after each review (crash-safe)
            with open(args.output, "w") as f:
                for r in results:
                    f.write(json.dumps(r) + "\n")
    except (KeyboardInterrupt, EOFError):
        print(f"\n\nSaved {len(results)} reviews. Resume with --resume flag.")
        sys.exit(0)

    print(f"\nDone. {len(results)} reviews saved to {args.output}")


if __name__ == "__main__":
    main()
