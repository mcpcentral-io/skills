# research-suite Plugin

End-to-end research workflows that wire together the **knowledge graph** (`mcpcentral-totext-cloud`), the **model registry** (`mcpcentral-llm-info`), and the **sandbox + decks** (`mcpcentral-office`).

If you've installed `totext-graph`, `llm-info`, and `office-sandbox` separately, you don't strictly need this plugin — but it adds two opinionated cross-server skills that orchestrate all three at once.

## Install

```bash
/plugin marketplace add mcpcentral-io/skills
/plugin install research-suite@mcpcentral-skills
```

The plugin's `.mcp.json` auto-wires all three backing servers.

## Skills

| Skill | Pipeline |
|---|---|
| `research-deck` | totext-graph search → llm-info picks a summarization model → office-sandbox renders a `.pptx` with citations |
| `ai-news-brief` | llm-info `list_latest` → enrich with `get_model` → render a one-pager (deck or markdown) → optional store back into totext-cloud |

## Why a Single Plugin

The single-server plugins (`totext-graph`, `llm-info`, `office-sandbox`) are great for users who want one capability. `research-suite` exists for users who explicitly want the **stitched** experience and don't want to compose three plugins themselves.

## Evals

Each skill ships with `evals/evals.json` and `evals/mcp-server-evals.json` covering the multi-server orchestration.
