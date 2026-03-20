# MCP Server Evals Design

**Date:** 2026-03-20
**Scope:** Evaluation test cases for the `mcpcentral-tool-search` MCP server

## Background

The `mcp-registry` skill already has 5 evals (`skills/mcp-registry/evals/evals.json`) covering direct REST API calls via WebFetch. Those evals do not cover the `mcpcentral-tool-search` MCP server, which exposes distinct capabilities: semantic search, BM25 keyword search, hybrid search, tool schema retrieval, and similarity/task-based recommendations.

This spec defines 6 new evals targeting those unique capabilities.

## Out of Scope

- `list_my_servers` — requires authentication, excluded
- `execute` — deprecated per README
- `list_approved_servers` — marked deprecated in the MCP server tooling ("use search_tools + execute instead"); excluded
- Re-testing capabilities already covered by skill evals (keyword registry search, star-sorted browsing, config generation)

## File

`skills/mcp-registry/evals/mcp-server-evals.json`

Separate from `evals.json` so skill evals and MCP server evals are independently runnable.

Top-level structure uses `skill_name` to match the existing `evals.json` convention, with the value identifying the MCP server:

```json
{
  "skill_name": "mcpcentral-tool-search",
  "evals": [...]
}
```

## Format

Each eval mirrors the existing `evals.json` structure with one addition — a `tool` field identifying which MCP tool the eval targets:

```json
{
  "id": 1,
  "tool": "search_tools",
  "prompt": "...",
  "expected_output": "...",
  "assertions": ["...", "..."]
}
```

The `tool` field enables grouping and filtering by tool. All other fields are identical to `evals.json`.

## Evals

### Eval 1 — `search_tools` (semantic mode)

**Tool:** `search_tools`
**Prompt:** "Find MCP tools that help AI agents persist memory and context between sessions."

**Why semantic:** The query is conceptual — no exact keyword like "memory" or "context" is guaranteed to appear verbatim in matching tool names or descriptions. Semantic vector embeddings should surface relevant tools (vector stores, memory managers, context backends) that BM25 keyword matching would miss. Note: whether results differ from BM25 is an expected behavioral property of the mode, not a checkable assertion within a single eval run; it is stated here as rationale only.

**Expected output:** A list of tools related to agent memory and context persistence, surfaced via `search_tools` with `mode: "semantic"`. Results reflect conceptual relevance, not just literal keyword overlap.

**Assertions:**
- `search_tools` is called with `mode: "semantic"`
- At least 3 results are returned
- Results are conceptually relevant to memory or context persistence (e.g., vector stores, embedding tools, session managers, knowledge bases)

---

### Eval 2 — `search_tools` (bm25 mode)

**Tool:** `search_tools`
**Prompt:** "Search for MCP servers with 'postgres' in the name or description."

**Why bm25:** The user explicitly wants literal keyword matching — tools whose names or descriptions contain the exact term "postgres". BM25 is the right mode for this. Note: whether results differ from semantic mode is an expected behavioral property, stated here as rationale only, not a checkable assertion within a single eval run.

**Expected output:** A list of tools whose names or descriptions contain the exact term "postgres", retrieved via `search_tools` with `mode: "bm25"`.

**Assertions:**
- `search_tools` is called with `mode: "bm25"`
- At least 1 result is returned
- All results contain "postgres" in the tool name or description (no semantically-adjacent-but-unrelated tools like generic "database" or "SQL" servers that don't mention postgres)

---

### Eval 3 — `search_tools` (hybrid mode)

**Tool:** `search_tools`
**Prompt:** "Find tools for working with GitHub — include both well-known tools and ones I might not know about."

**Why hybrid:** The phrase "well-known tools" calls for BM25 (exact "GitHub" keyword matches), while "ones I might not know about" calls for semantic search (adjacent tools: code review, CI/CD, issue tracking, repository management). Hybrid mode combines both via RRF fusion.

**Expected output:** A list of GitHub-related and adjacent tools from `search_tools` with `mode: "hybrid"`. Results include directly-named GitHub tools plus semantically adjacent tools the user may not have thought to search for.

**Assertions:**
- `search_tools` is called with `mode: "hybrid"`
- At least 3 results are returned
- Results include tools directly named or described as GitHub tools
- Results include at least one tool in an adjacent domain (code review, CI/CD, issue tracking, or repository management)

---

### Eval 4 — `get_tool_schema`

**Tool:** `get_tool_schema`
**Prompt:** "What exact parameters do I need to call the postgres query tool?"

**Why get_tool_schema:** This is the only way to retrieve a full JSON Schema and TypeScript interface for a specific tool. The skill (WebFetch path) has no equivalent — it can only retrieve package-level metadata, not tool-level call signatures. The `get_tool_schema` tool requires two parameters: `serverId` (the server identifier, e.g., `"github/modelcontextprotocol/servers/postgres"`) and `toolName` (the specific tool within that server, e.g., `"query"`). Since the prompt provides no server ID, the agent must first call `search_tools` to resolve a real `serverId`. The `toolName` ("query") is inferred from the prompt text — no prior resolution step is required for it.

**Expected output:** A full JSON schema for a postgres query tool, including parameter names, types, and required/optional status.

**Assertions:**
- `search_tools` is first called to identify a valid postgres-related server ID (the ID is not invented)
- `get_tool_schema` is called with both a `serverId` and a `toolName` (not a single combined ID string)
- The `serverId` is obtained from the prior `search_tools` result, not fabricated
- The response includes a JSON schema with a `properties` block
- Each property in the schema includes a type and description
- Required vs. optional parameters are distinguished in the response

---

### Eval 5 — `recommend_tools` (similar_to)

**Tool:** `recommend_tools`
**Prompt:** "What MCP servers are similar to the GitHub MCP server?"

**Why similar_to:** The user is starting from a known server and wants to discover adjacent options. `recommend_tools` with `type: "similar_to"` uses vector similarity over server embeddings. It accepts either a server-level ID (e.g., `"github/github/github-mcp-server"`) or a tool-level ID; this eval uses a server-level ID since the user is asking about a server, not a specific tool. Since the prompt provides no pre-known ID, the agent must call `search_tools` first to resolve a real GitHub server ID.

**Expected output:** A list of servers similar to the GitHub MCP server, retrieved via `recommend_tools` with `type: "similar_to"` and a server-level ID. Results reflect functional similarity (code hosting, version control, CI/CD, developer workflow), not keyword matching.

**Assertions:**
- `search_tools` is first called to identify a real GitHub server ID (the ID is not invented)
- `recommend_tools` is called with `type: "similar_to"` and a `serverId` obtained from the prior search (server-level ID, not tool-level)
- At least 3 results are returned
- Results include servers in functionally adjacent domains (code hosting, version control, CI/CD, issue tracking, developer workflow)
- Response is labeled as similarity-based recommendations, not a keyword search result

---

### Eval 6 — `recommend_tools` (for_task)

**Tool:** `recommend_tools`
**Prompt:** "I'm building an agent that monitors cloud infrastructure and sends alerts. What MCP tools should I use?"

**Why for_task:** The user has a task description, not a known starting server. `recommend_tools` with `type: "for_task"` uses the task description as the search vector, returning tools most likely to help accomplish the task. No prior `search_tools` call is required — the task description itself is passed directly as `taskDescription`.

**Expected output:** A list of tools recommended for the infrastructure monitoring and alerting task, retrieved via `recommend_tools` with `type: "for_task"` and a `taskDescription` string. Results are task-relevant (cloud providers, monitoring tools, alerting/notification tools).

**Assertions:**
- `recommend_tools` is called with `type: "for_task"` and a `taskDescription` string derived from the user's prompt
- At least 3 results are returned
- Results include tools relevant to cloud infrastructure, monitoring, or alerting/notifications
- Response is labeled as task-based recommendations, not a search result
- Results reflect the full task scope (not just "cloud" or just "alerts" in isolation)
