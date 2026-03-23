# Agent Security — OWASP Agentic Top 10 Tooling

Tools for monitoring, constraining, and securing autonomous AI agents in production. Mapped to the OWASP Top 10 for Agentic Applications (December 2025).

## Credential Hygiene for Agent Environments

Agents have shell access. If credentials are on disk, the agent can read them. OpenAI's misalignment monitoring found agents extracting encrypted credentials from macOS keychains. Long-lived AWS keys in `.env` files are worse — no encryption, no audit trail, no expiry.

**Rules:**

1. **Never mount long-lived credentials into agent environments.** No `.env` files with API keys. No `~/.aws/credentials` with permanent access keys. If the agent can `cat` it, assume it will.

2. **Use short-lived credentials passed at startup.** AWS STS `AssumeRole` with 15-minute TTL. The agent's session dies before the credential does. If compromised, the blast radius is bounded by the TTL.

3. **Use IAM roles for compute, not credentials.** EC2 instance profiles, ECS task roles, Lambda execution roles. The credential is never on disk — it lives in the instance metadata service and rotates automatically.

4. **For local development:** AWS SSO (`aws sso login`) generates temporary credentials that expire. If an agent extracts them, they are worthless within hours.

5. **Use Secrets Manager or Vault for runtime secrets.** Pull at startup into memory, don't persist to disk. Rotate on a schedule shorter than your agent's maximum session length.

| Approach | TTL | Agent can extract? | Blast radius |
|----------|-----|-------------------|-------------|
| `.env` with long-lived keys | Indefinite | Yes, trivially | Full account access until revoked |
| `~/.aws/credentials` | Indefinite | Yes, trivially | Full account access until revoked |
| AWS SSO session | 1-12 hours | Yes, but expires | Bounded by session TTL |
| STS AssumeRole | 15 min - 12 hours | Yes, but expires | Bounded by role policy + TTL |
| EC2/ECS IAM role | Auto-rotated | Only via metadata service | Bounded by role policy |
| Secrets Manager + memory-only | N/A | Only if agent reads process memory | Minimal |

**The principle:** the credential's lifetime should be shorter than the agent's session. If the agent runs for 30 minutes, the credential should expire in 15.

---

## Sandboxing & Isolation (OWASP #1 Excessive Agency, #2 Uncontrolled Autonomy)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| NVIDIA OpenShell | Default-deny agent runtime. Filesystem, network, process, and inference locked down. Declarative YAML policies. Kernel-level enforcement via Landlock, Seccomp, OPA/Rego. | Yes | https://github.com/NVIDIA/OpenShell |
| gVisor | Application kernel for containers. Intercepts syscalls before they reach host kernel. | Yes (Apache 2.0) | https://gvisor.dev |
| Firecracker | Lightweight microVMs. Hardware-level isolation. Used by AWS Lambda. | Yes (Apache 2.0) | https://firecracker-microvm.github.io |
| Docker (rootless) | Container isolation. Minimum viable sandbox. | Yes | https://docs.docker.com/engine/security/rootless/ |
| E2B | Cloud sandboxes for AI agents. Isolated environments with API access. | Partial | https://e2b.dev |
| Daytona | Standardized dev environments for agents. | Yes (Apache 2.0) | https://www.daytona.io |

## Scope Monitoring & Permission Control (OWASP #1, #5 Trust Boundaries, #6 Memory)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| Stytch | Agent-as-client identity, short-lived tokens, OAuth for agents | No | https://stytch.com/blog/handling-ai-agent-permissions/ |
| SPIFFE / SPIRE | Cryptographic workload identity. Agent gets a verifiable identity. | Yes (Apache 2.0) | https://spiffe.io |
| OPA (Open Policy Agent) | Policy enforcement on agent actions. "Can this agent call this tool?" | Yes (Apache 2.0) | https://www.openpolicyagent.org |
| Permit.io | Fine-grained authorization for AI agents | No | https://www.permit.io |

## Behavioral Monitoring & Anomaly Detection (OWASP #2, #3 Transparency, #10 Observability)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| Langfuse | LLM tracing, evals, session replay. Log every tool call, decision, outcome. | Yes (MIT) | https://langfuse.com |
| Arize Phoenix | LLM observability with traces, evals, and drift detection | Source-available | https://phoenix.arize.com |
| LangSmith | LLM tracing and debugging (LangChain ecosystem) | No | https://smith.langchain.com |
| Portkey | AI gateway with guardrails, rate limiting, cost tracking, fallbacks | No | https://portkey.ai |
| Helicone | LLM observability and cost tracking proxy | Yes (Apache 2.0) | https://helicone.ai |
| LiteLLM | Unified proxy for 100+ LLM providers. Cost tracking, rate limiting, fallbacks, load balancing. | Yes (MIT) | https://github.com/BerriAI/litellm |
| Galileo | LLM monitoring with hallucination detection | No | https://www.rungalileo.io |

## Red-Teaming & Adversarial Testing (OWASP #4 Prompt Injection, #1 Excessive Agency)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| promptfoo | LLM eval and red-teaming framework. Generates adversarial attacks tailored to your app: prompt injections, jailbreaks, data leaks, PII exposure, business rule violations. 50+ vulnerability types. YAML-configured test suites that run in CI. Also tests RAG pipelines, agents, and guardrails. | Yes (MIT) | https://promptfoo.dev |
| Garak | LLM vulnerability scanner. Probes for prompt injection, data extraction, and hallucination. | Yes (Apache 2.0) | https://github.com/leondz/garak |

Red-teaming is a behavioral gate (Tier 4) that tests what the model *does*, not what the code *looks like*. Run adversarial tests against your LLM-powered features the same way you run unit tests against your code. If you're building anything that takes user input and passes it to a model, these tools catch the attacks your unit tests can't.

## Supply Chain & Integration Security (OWASP #7 Vulnerable Integration Points, #9 Insecure Communication)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| Socket | Supply chain attack detection for npm, PyPI, Go | No | https://socket.dev |
| Snyk | Dependency vulnerability scanning | Partial | https://snyk.io |
| Tencent AI-Infra-Guard | Security scanner for AI infrastructure and model assets | Yes (Apache 2.0) | https://github.com/Tencent/AI-Infra-Guard |
| Semgrep Supply Chain | Reachability analysis for vulnerable dependencies | Partial | https://semgrep.dev/products/semgrep-supply-chain |
| Sigstore / cosign | Artifact signing and verification | Yes (Apache 2.0) | https://sigstore.dev |

## Agent Lifecycle & Drift Detection (OWASP #8 Lifecycle Management)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| Braintrust | Experiment tracking, LLM scoring, regression detection | No | https://www.braintrust.dev |
| DeepEval | Pytest-style LLM evaluation with 14+ metrics | Yes (Apache 2.0) | https://github.com/confident-ai/deepeval |
| RAGAS | RAG pipeline evaluation and regression | Yes (Apache 2.0) | https://ragas.io |
| Weights & Biases | Model tracking, eval logging, dataset versioning | Partial | https://wandb.ai |
| MLflow | Model lifecycle management and experiment tracking | Yes (Apache 2.0) | https://mlflow.org |

## Multi-Agent Coordination (OWASP #4 Inadequate Orchestration)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| LangGraph | Multi-agent orchestration with state machines | Yes (MIT) | https://github.com/langchain-ai/langgraph |
| Google ADK | Agent Development Kit with routing and orchestration | Yes (Apache 2.0) | https://google.github.io/adk-docs/ |
| CrewAI | Multi-agent framework with role-based coordination | Yes (MIT) | https://www.crewai.com |
| Temporal | Durable execution for agent workflows | Yes (MIT) | https://temporal.io |
| AutoGen | Multi-agent conversation framework (Microsoft) | Yes (MIT) | https://github.com/microsoft/autogen |

## Cost Controls & Budget Enforcement (OWASP #8 Lifecycle, #10 Observability)

Runaway agent costs are a security problem, not just a finance problem. An agent in an infinite loop or exploring outside its scope burns budget that signals something is wrong.

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| Stripe `@stripe/token-meter` | Per-call cost calculation across OpenAI, Anthropic, Gemini. Billing integration. | Yes (MIT) | https://github.com/stripe/ai |
| LiteLLM Proxy | Budget limits per project/key/model. Spend alerts. Rate limiting. | Yes (MIT) | https://docs.litellm.ai/docs/proxy/cost_tracking |
| Azure AI Gateway | `llm-token-limit` policies. Per-project TPM quotas. Hard caps on token consumption. | No | https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy |
| Portkey | Per-request cost estimation. Budget alerts and rate limits. | No | https://portkey.ai |

### SDK-level caps

Every major agent SDK has built-in budget parameters. Set at least two per agent run:

| SDK | Turn limit | Default |
|-----|-----------|---------|
| OpenAI Agents SDK | `max_turns` | 10 |
| LangGraph | `recursion_limit` | 25 |
| CrewAI | `max_iter` + `max_execution_time` | 25 |
| Anthropic | `budget_tokens` (thinking) | varies |

For full implementation details, see [../agent-monitoring/README.md](../agent-monitoring/README.md#step-6-track-iteration-budget-per-run).

## Inter-Agent Identity & Trust (OWASP #5, #9)

| Tool | What it does | OSS | URL |
|------|-------------|-----|-----|
| SPIFFE / SPIRE | Cryptographic identity for agents | Yes (Apache 2.0) | https://spiffe.io |
| Google A2A Protocol | Agent-to-agent communication standard | Emerging | https://google.github.io/A2A/ |

## Official Provider Guides

- [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — Guardrails, input filtering, tool use safety, human-in-the-loop.
- [Anthropic: Building Effective AI Agents](https://resources.anthropic.com/building-effective-ai-agents) — End-to-end agent patterns with security and eval guidance.
- [Google ADK: Safety and Security for AI Agents](https://google.github.io/adk-docs/safety/) — Identity, permissions, sandboxing, I/O controls for agents.
