# MCPCentral Plugins for Claude Code

A growing marketplace of single-purpose plugins that wrap the [mcpcentral.io](https://mcpcentral.io) MCP servers. Install one, install several, or install the whole stack.

## Plugin Matrix

| Plugin | What it wraps | Skills | Install |
|---|---|---|---|
| **mcpcentral** *(core)* | mcpcentral-registry, gateway; routes through llm-info for model selection | `mcp-registry`, `totext-local`, `whoami` | `/plugin install mcpcentral@mcpcentral-skills` |
| **llm-info** | mcpcentral-llm-info | `model-picker`, `model-migrate`, `model-cost-estimate`, `model-changelog` | `/plugin install llm-info@mcpcentral-skills` |
| **totext-graph** | mcpcentral-totext-cloud | `research-graph`, `entity-dossier`, `citation-tracer`, `knowledge-onboard` | `/plugin install totext-graph@mcpcentral-skills` |
| **office-sandbox** | mcpcentral-office | `container-run`, `deck-builder` | `/plugin install office-sandbox@mcpcentral-skills` |
| **research-suite** | llm-info + totext-cloud + office | `research-deck`, `ai-news-brief` | `/plugin install research-suite@mcpcentral-skills` |

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add mcpcentral-io/skills

# Install whatever you want — they're independent
/plugin install mcpcentral@mcpcentral-skills
/plugin install llm-info@mcpcentral-skills
/plugin install totext-graph@mcpcentral-skills
/plugin install office-sandbox@mcpcentral-skills
/plugin install research-suite@mcpcentral-skills
```

Each plugin auto-wires only the MCP servers it needs.

## Plugins

### mcpcentral (core)

The original plugin, expanded:

- **`mcp-registry`** — search the official MCP Registry and mcpcentral.io REST APIs; generate setup configs.
- **`totext-local`** *(renamed from `to-text` in v1.2.0)* — extract text from images / audio / video / PDFs / Office docs / URLs and summarize. Summarization model is now **selected at runtime** via `mcpcentral-llm-info` instead of hardcoded.
- **`whoami`** — identity & tenancy introspection: tenant, plan, permissions. Bundles `mcpcentral-mcp-gateway`.

### llm-info

Live LLM model registry across OpenAI, Anthropic, Gemini, Groq, Ollama, Ollama-cloud, etc.

- **`model-picker`** — "Which model for X with budget Y?"
- **`model-migrate`** — "What changes if I move from A to B?" (pricing, capabilities, SDK headers)
- **`model-cost-estimate`** — "How much per month for this workload across N models?"
- **`model-changelog`** — "What new LLMs came out this week?"

### totext-graph

Personal document knowledge graph: hybrid search (BM25 + semantic), entity extraction, citation traversal.

- **`research-graph`** — answer a question against your library with citations.
- **`entity-dossier`** — build a profile for a person / company / topic / date / location.
- **`citation-tracer`** — trace what cites what, and lineage chains.
- **`knowledge-onboard`** — bulk-ingest URLs and verify the graph indexed them.

Pairs naturally with **`totext-local`** (extract a local file) → **`knowledge-onboard`** (push it into the graph).

### office-sandbox

Sandboxed Ubuntu container + a curated PowerPoint template engine.

- **`container-run`** — run Python / Node / shell in an ephemeral container with internet, file IO, and download URLs for artifacts.
- **`deck-builder`** — generate a real `.pptx` from an outline using one of the bundled templates (with thumbnail previews).

### research-suite

Stitched cross-server workflows for power users.

- **`research-deck`** — search your library → pick a cheap model → render a `.pptx` with citations. Three servers, one prompt.
- **`ai-news-brief`** — pull the latest model releases → enrich → render as deck or markdown → optionally store back into your library so it's searchable next week.

## Repository Structure

```
.
├── .claude-plugin/marketplace.json     # 5 plugin entries
├── .mcp.json                            # all 5 mcpcentral.io servers (dev-time)
├── skills/                              # mcpcentral core plugin
│   ├── mcp-registry/
│   ├── totext-local/                    # renamed from to-text in 1.2.0
│   └── whoami/
└── plugins/                             # one subdir per non-core plugin
    ├── llm-info/         (.mcp.json + 4 skills)
    ├── totext-graph/     (.mcp.json + 4 skills)
    ├── office-sandbox/   (.mcp.json + 2 skills)
    └── research-suite/   (.mcp.json + 2 skills)
```

## Authentication

The mcpcentral.io servers require OAuth on first use. Claude Code handles the browser flow automatically. For programmatic / API access, generate a key at [mcpcentral.io](https://mcpcentral.io).

## Evals

Every skill ships with `evals/evals.json` (skill-level) and, for skills that call MCP tools, `evals/mcp-server-evals.json` (tool-level). The eval files are JSON specs — there's no runner in this repo; they document expected behavior for review and external test harnesses.

## Links

- [MCPCentral](https://mcpcentral.io) — MCP server directory with community metrics
- [MCP Registry](https://registry.modelcontextprotocol.io) — Official MCP server registry
- [Agent Skills Standard](https://agentskills.io) — Cross-platform skill specification
- [ClawCentral](https://clawcentral.io) — Our platform
