"""
Collect AI-assisted PR diffs from GitHub for error analysis.

Identifies AI-assisted PRs by:
- Co-authored-by trailers mentioning AI tools
- PR labels (e.g., "ai-assisted", "copilot")
- Bot-authored PRs from coding agents

Usage:
    python collect_samples.py --repo owner/repo --count 100 --output samples.jsonl
    python collect_samples.py --repo owner/repo --label ai-assisted --output samples.jsonl
"""

import argparse
import json
import subprocess
import sys


def fetch_prs(repo: str, count: int, label: str | None = None) -> list[dict]:
    """Fetch recent merged PRs from GitHub using gh CLI."""
    cmd = [
        "gh", "pr", "list",
        "--repo", repo,
        "--state", "merged",
        "--limit", str(count),
        "--json", "number,title,author,labels,body,mergedAt",
    ]
    if label:
        cmd.extend(["--label", label])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PRs: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return json.loads(result.stdout)


def fetch_diff(repo: str, pr_number: int) -> str:
    """Fetch the diff for a specific PR."""
    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--repo", repo],
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def is_ai_assisted(pr: dict) -> bool:
    """Heuristic: check if PR was likely AI-assisted."""
    ai_signals = [
        "copilot", "claude", "cursor", "ai-assisted", "ai-generated",
        "aider", "cody", "devin", "codegen",
    ]

    # Check labels
    label_names = [l.get("name", "").lower() for l in pr.get("labels", [])]
    if any(signal in name for name in label_names for signal in ai_signals):
        return True

    # Check author (bot accounts)
    author = pr.get("author", {}).get("login", "").lower()
    if any(signal in author for signal in ai_signals):
        return True

    # Check body for co-authored-by
    body = (pr.get("body") or "").lower()
    if any(signal in body for signal in ai_signals):
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Collect AI-assisted PR diffs for error analysis")
    parser.add_argument("--repo", required=True, help="GitHub repo (owner/repo)")
    parser.add_argument("--count", type=int, default=100, help="Number of PRs to fetch")
    parser.add_argument("--label", help="Filter by label (e.g., 'ai-assisted')")
    parser.add_argument("--output", default="samples.jsonl", help="Output file (JSONL)")
    parser.add_argument("--all", action="store_true", help="Include all PRs, not just AI-detected")
    args = parser.parse_args()

    print(f"Fetching {args.count} merged PRs from {args.repo}...")
    prs = fetch_prs(args.repo, args.count, args.label)

    if not args.all:
        prs = [pr for pr in prs if is_ai_assisted(pr)]
        print(f"Found {len(prs)} AI-assisted PRs")

    samples = []
    for i, pr in enumerate(prs):
        print(f"  Fetching diff {i+1}/{len(prs)}: #{pr['number']}")
        diff = fetch_diff(args.repo, pr["number"])
        samples.append({
            "pr_number": pr["number"],
            "title": pr["title"],
            "author": pr.get("author", {}).get("login", "unknown"),
            "merged_at": pr.get("mergedAt", ""),
            "diff": diff,
            "review_status": "pending",
            "failure_categories": [],
            "severity": None,
            "notes": "",
        })

    with open(args.output, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

    print(f"Wrote {len(samples)} samples to {args.output}")


if __name__ == "__main__":
    main()
