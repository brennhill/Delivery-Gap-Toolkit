"""
Summarize failure categories from reviewed samples.

Reads reviewed JSONL and outputs category frequency,
severity distribution, and recommended gate types.

Usage:
    python summarize.py --input reviewed.jsonl
"""

import argparse
import json
from collections import Counter

# Maps failure categories to recommended gate types
GATE_RECOMMENDATIONS = {
    "silent_rename": ("contract test", "tools/contract-examples/"),
    "confident_fabrication": ("existence check", "sloppy-joe for deps; grep for undefined imports"),
    "scope_creep": ("diff-size gate + spec linkage", "gates/pr-size-limits/"),
    "copy_paste_drift": ("duplication detector", "jscpd, PMD CPD, Simian"),
    "missing_edge_case": ("invariant test", "tools/invariant-examples/"),
    "security_blindspot": ("policy gate", "semgrep, bandit — see gates/by-language/"),
    "type_error": ("type checker", "mypy, tsc --strict — see gates/by-language/"),
    "wrong_api_usage": ("contract test", "tools/contract-examples/"),
    "test_gap": ("coverage gate", "see gates/by-language/"),
}


def main():
    parser = argparse.ArgumentParser(description="Summarize error analysis results")
    parser.add_argument("--input", required=True, help="Reviewed JSONL file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    with open(args.input) as f:
        samples = [json.loads(line) for line in f if line.strip()]

    reviewed = [s for s in samples if s.get("review_status") == "reviewed"]
    skipped = [s for s in samples if s.get("review_status") == "skipped"]
    no_issue = [s for s in reviewed if s.get("failure_categories") == ["no_issue"]]
    with_issues = [s for s in reviewed if s.get("failure_categories") != ["no_issue"]]

    # Count categories
    category_counts = Counter()
    category_severity = {}
    for sample in with_issues:
        for cat in sample.get("failure_categories", []):
            category_counts[cat] += 1
            if cat not in category_severity:
                category_severity[cat] = Counter()
            if sample.get("severity"):
                category_severity[cat][sample["severity"]] += 1

    if args.json:
        output = {
            "total_samples": len(samples),
            "reviewed": len(reviewed),
            "skipped": len(skipped),
            "with_issues": len(with_issues),
            "no_issues": len(no_issue),
            "failure_rate": round(len(with_issues) / max(len(reviewed), 1) * 100, 1),
            "categories": {
                cat: {
                    "count": count,
                    "severity": dict(category_severity.get(cat, {})),
                    "recommendation": GATE_RECOMMENDATIONS.get(cat, ("custom eval", "")),
                }
                for cat, count in category_counts.most_common()
            },
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print(f"\n{'='*60}")
    print("ERROR ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"  Reviewed:    {len(reviewed)} samples")
    print(f"  With issues: {len(with_issues)} ({round(len(with_issues)/max(len(reviewed),1)*100)}%)")
    print(f"  Clean:       {len(no_issue)}")
    print(f"  Skipped:     {len(skipped)}")

    print(f"\nFailure categories (sorted by frequency):")
    for cat, count in category_counts.most_common():
        severity = category_severity.get(cat, {})
        high = severity.get("high", 0)
        severity_str = f"({high} high-severity)" if high else ""
        print(f"  {cat:30s} {count:3d} occurrences {severity_str}")

    print(f"\nRecommended gates:")
    for cat, count in category_counts.most_common(5):
        gate_type, reference = GATE_RECOMMENDATIONS.get(cat, ("custom eval", ""))
        print(f"  {cat:30s} → {gate_type}")
        if reference:
            print(f"  {'':30s}   See: {reference}")

    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
