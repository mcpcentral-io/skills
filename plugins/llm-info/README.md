# llm-info Plugin

Live LLM model registry skills, powered by [`mcpcentral-llm-info`](https://mcp.llm-info.mcpcentral.io/mcp).

Pick the right model for the job, plan a migration, estimate API spend, and stay current with what's new — all from real registry data across OpenAI, Anthropic, Gemini, Groq, Ollama, Ollama-cloud, and more.

## Install

```bash
/plugin marketplace add mcpcentral-io/skills
/plugin install llm-info@mcpcentral-skills
```

The plugin's `.mcp.json` auto-wires `mcpcentral-llm-info`. No API key required for the registry itself.

## Skills

| Skill | When to invoke |
|---|---|
| `model-picker` | "Which model should I use for X with budget Y?" |
| `model-migrate` | "I'm on model A, what changes if I move to model B?" |
| `model-cost-estimate` | "How much will this workload cost per month across these models?" |
| `model-changelog` | "What new models came out this week / month?" |

## Backing MCP Tools

| Tool | Purpose |
|---|---|
| `recommend_model` | Use-case + budget → ranked picks with rationale |
| `compare_pricing` | Side-by-side pricing across providers / model families |
| `get_model` | Full spec (capabilities, pricing, limits, dates) for one model |
| `list_models` | Filter the full registry by provider / capability / max price |
| `list_latest` | Newest releases sorted by date |
| `get_capability_matrix` | Visual matrix of features × providers |

## Evals

Each skill ships with `evals/evals.json` (skill-level) and `evals/mcp-server-evals.json` (MCP-tool-level), mirroring the pattern in `skills/mcp-registry/evals/`.
