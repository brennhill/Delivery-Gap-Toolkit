# The Delivery Gap — Execution Kit

Companion tools, scripts, and templates for *The Delivery Gap: Speed and Certainty in the Age of AI* by Brenn Hill.

The book describes the gap between generation velocity and verification capacity. This repo helps you close it with running code, actionable checklists, and measurement scripts you can deploy this week.

---

## Structure

```
metrics/                              Measure all three vertices of the Verification Triangle
├── cost-per-accepted-change/         The metric no commercial tool computes (yet)
├── rework-detection/                 14-day rework detection from git history
├── delivery-baseline/                Baseline metrics from git + GitHub API
├── spec-quality/                     Spec coverage scanner + rework-by-spec comparison
└── eval-quality/                     Machine catch rate, reviewer-minutes, defect escape, change fail rate

gates/                                Implement the five quality gate tiers
├── agent-production-checklist.md     Unified checklist from OpenAI, Anthropic, Google, NVIDIA, Spotify
├── observability/                    Three-layer observability: pipeline, delivery, agent
├── agent-monitoring/                 Step-by-step agent observability with code examples
├── agent-security/                   OWASP Top 10 mapped tooling for agent constraints
├── multi-pass-review/                Installable multi-perspective AI code review (code-reviewers)
├── pr-size-limits/                   400-line limit with GitHub Actions + GitLab CI configs
└── by-language/                      Gate tooling for JS/TS, Python, Go, JVM, Rust, Ruby, PHP

templates/                            Process artifacts
├── specs/                            One-page spec template
├── review/                           Code review checklist, eval definition, failure taxonomy
├── scorecard/                        Weekly scorecard CSV
└── rollout/                          AI rollout memo for leadership

tools/                                Worked examples
└── invariant-examples/               Idempotent webhook with property-based tests
```

---

## The Spec Template: Why It's Ordered This Way

The [Context-Anchor Spec](templates/specs/01-one-page-spec-template.md) has 12 sections split into two blocks:

**👤 Human context (sections 1–4)** comes first: who this is for, what success looks like, who owns it, how to roll back. These set the stage for reviewers and stakeholders. They are not scored by quality tools — humans judge whether a feature succeeded in the market, not machines.

**🤖 Machine execution (sections 5–12)** comes last: model anchors, entities, scope, constraints, style rules, error contracts, edge cases, acceptance criteria. These are the sections AI agents consume during code generation and that [upfront](https://github.com/brennhill/upfront) scores for quality.

The ordering is intentional. LLMs exhibit **recency bias** — content at the end of the context window is weighted more heavily than content at the beginning. By placing the machine-executable sections last, the acceptance criteria, error contracts, and edge cases sit in the strongest position in the AI's attention when it starts generating code.

The sections themselves were derived from a gap analysis across three spec formats:
- **[Spec Kit](https://github.com/github/spec-kit)** (GitHub) — contributed Edge Cases, Key Entities, Success Criteria
- **[Kiro](https://kiro.dev)** (AWS) — contributed Glossary/Entity definitions, Error Handling strategy
- **Delivery Gap** (original) — contributed Model Anchors, Scope Non-goals, Contract/Invariant/Policy checks, Rollback Plan

Each machine section prevents a specific class of AI hallucination:

| Section | Without it, the AI will... |
|---------|---------------------------|
| Model Anchors | Invent its own architecture instead of following existing patterns |
| Key Entities | Make up names and relationships that don't match the domain |
| Scope Boundaries | Build features you explicitly excluded |
| Constraints | Violate security, SLA, or compliance requirements |
| Style/Architecture Rules | Ignore module boundaries and conventions |
| Error Contract | Invent a different error shape in every function |
| Edge Cases | Ignore boundary conditions and failure paths |
| Acceptance Criteria | Produce code that can't be deterministically verified |

---

## Quick Start

### "I need to measure whether AI is helping or hurting"

```bash
# Detect rework from git history
python metrics/rework-detection/rework-detector.py --repo owner/repo --json rework.json

# Calculate cost per accepted change
python metrics/cost-per-accepted-change/cost-calculator.py \
  --json costs.json --from-rework rework.json --html report.html

# Check spec coverage
python metrics/spec-quality/spec-coverage.py --repo owner/repo

# Check machine catch rate
python metrics/eval-quality/machine-catch-rate.py --repo owner/repo
```

### "I have a monorepo drowning in AI PRs"

```bash
# Enforce PR size limits in CI
# See gates/pr-size-limits/ for GitHub Actions + GitLab configs

# Run multi-pass AI code review
pip install -e "gates/multi-pass-review[anthropic]"
code-reviewers --pr 123 --repo owner/repo --parallel
```

### "I'm deploying agents to production"

Start with the checklist:
→ **[gates/agent-production-checklist.md](gates/agent-production-checklist.md)**

Then set up monitoring:
→ **[gates/agent-monitoring/](gates/agent-monitoring/)**

### "I need gate tooling for my language"

→ **[gates/by-language/](gates/by-language/)** — JS/TS, Python, Go, JVM, Rust, Ruby, PHP

---

## Key External Resources

### From the model providers

| Provider | Guide | Focus |
|----------|-------|-------|
| OpenAI | [Monitoring coding agents for misalignment](https://openai.com/index/how-we-monitor-internal-coding-agents-misalignment/) | Behavioral monitoring at scale |
| OpenAI | [Practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | Guardrails, input filtering, human-in-the-loop |
| Anthropic | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Production monitoring + evals |
| Anthropic | [Building Effective AI Agents](https://resources.anthropic.com/building-effective-ai-agents) | End-to-end agent patterns |
| Anthropic | [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) | Agentic coding patterns |
| Google | [ADK Safety and Security](https://google.github.io/adk-docs/safety/) | Identity, permissions, sandboxing |

### Standards & frameworks

| Standard | What it is | URL |
|----------|-----------|-----|
| OWASP Top 10 for Agentic Applications | 10 risk categories, 100+ experts | [owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) |
| DORA Metrics | Delivery performance measurement | [dora.dev](https://dora.dev/guides/dora-metrics/) |
| NVIDIA OpenShell | Default-deny agent runtime | [github.com](https://github.com/NVIDIA/OpenShell) |
| SPIFFE/SPIRE | Cryptographic workload identity | [spiffe.io](https://spiffe.io) |
| OpenTelemetry GenAI | AI-specific observability conventions | [opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/) |

### Key research

| Study | Finding |
|-------|---------|
| Faros AI (10K developers, 1,255 teams) | PR volume +98%, net throughput: zero |
| Uplevel (800 developers) | 41% increase in bug rate after Copilot adoption |
| GitClear (211M changed lines, 2020-2024) | Code churn doubled; refactoring collapsed |
| NAV IT (20 months, 4,000 developers) | No measurable productivity change |
| CircleCI (9M workflows) | Top 5% at +97% throughput; median at +4% |

For code quality and gate-specific research, see [gates/README.md](gates/README.md#key-research).

---

## License

Apache 2.0. See [LICENSE](LICENSE).
