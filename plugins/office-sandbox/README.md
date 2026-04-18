# office-sandbox Plugin

Sandboxed execution and document-generation skills, powered by [`mcpcentral-office`](https://mcp.office.mcpcentral.io/mcp).

A short-lived Ubuntu 20.04 container (Python 3, Node.js, npm, git, build-essential, curl) with internet access, plus a curated PowerPoint template library that produces real `.pptx` decks.

## Install

```bash
/plugin marketplace add mcpcentral-io/skills
/plugin install office-sandbox@mcpcentral-skills
```

The plugin's `.mcp.json` auto-wires `mcpcentral-office`. The container must be initialized via `container_initialize` before any `_exec` or template call — both bundled skills handle this for you.

## Skills

| Skill | When to invoke |
|---|---|
| `container-run` | "Run this Python / Node / shell snippet for me", "fetch this URL and parse it", "execute this script in a clean environment" |
| `deck-builder` | "Build me a deck on X", "turn this outline into a PowerPoint", "render slides from these bullet points" |

## Backing MCP Tools

Container lifecycle:
- `container_initialize`, `container_ping`, `container_exec`

File operations:
- `container_file_read`, `container_file_write`, `container_file_delete`
- `container_files_list`, `container_file_upload_url`, `container_file_download_url`

PowerPoint templates:
- `container_template_categories`, `container_template_list`
- `container_template_info`, `container_template_preview`

## Evals

Each skill ships with `evals/evals.json` and `evals/mcp-server-evals.json`.
