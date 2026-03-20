# MCP Server Evals Design

**Date:** 2026-03-20
**Scope:** Evaluation test cases for the `mcpcentral-tool-search` MCP server

## Background

The `mcp-registry` skill already has 5 evals (`skills/mcp-registry/evals/evals.json`) covering direct REST API calls via WebFetch. Those evals do not cover the `mcpcentral-tool-search` MCP server, which exposes distinct capabilities: semantic search, BM25 keyword search, hybrid search, tool schema retrieval, and similarity/task-based recommendations.

This spec defines 6 new evals targeting those unique capabilities.

## Out of Scope

- `list_my_servers` — requires authentication, excluded
- `execute` — deprecated per README
- Re-testing capabilities already covered by skill evals (keyword registry search, star-sorted browsing, config generation)

## File

`skills/mcp-registry/evals/mcp-server-evals.json`

Separate from `evals.json` so skill evals and MCP server evals are independently runnable. Top-level structure:

```json
{
  "mcp_server": "mcpcentral-tool-search",
  "evals": [...]
}
```

## Format

Each eval mirrors the existing `evals.json` structure:

```json
{
  "id": 1,
  "tool": "search_tools",
  "prompt": "...",
  "expected_output": "...",
  "assertions": ["...", "..."]
}
```

A `tool` field is added to identify which MCP tool the eval targets, for grouping and filtering. All other fields match the existing format.

## Evals

### Eval 1 — `search_tools` (semantic mode)

**Tool:** `search_tools`
**Prompt:** "Find MCP tools that help AI agents persist memory and context between sessions."

**Why semantic:** The query is conceptual — no exact keyword like "memory" or "context" is guaranteed to appear verbatim in matching tool names or descriptions. Semantic vector embeddings should surface relevant tools (vector stores, memory managers, context backends) that BM25 would miss.

**Expected output:** A list of tools related to agent memory and context persistence, surfaced via `search_tools` with `mode: "semantic"`. Results should reflect conceptual relevance, not just literal keyword overlap.

**Assertions:**
- `search_tools` is called with `mode: "semantic"`
- At least 3 results are returned
- Results are conceptually relevant to memory/context persistence (e.g., vector stores, embedding tools, session managers)
- Results would likely differ from a BM25 search on the same query (semantic mode surfaces conceptual matches, not just literal keyword hits)

---

### Eval 2 — `search_tools` (bm25 mode)

**Tool:** `search_tools`
**Prompt:** "Search for MCP servers with 'postgres' in the name or description."

**Why bm25:** The user explicitly wants literal keyword matching — tools whose names or descriptions contain the exact term "postgres". BM25 is the right mode for this; semantic search might surface generic database tools that dilute the results.

**Expected output:** A list of tools whose names or descriptions contain the exact term "postgres", retrieved via `search_tools` with `mode: "bm25"`.

**Assertions:**
- `search_tools` is called with `mode: "bm25"`
- At least 1 result is returned
- All results contain "postgres" in the tool name or description (no semantically-adjacent-but-unrelated tools like generic "database" or "SQL" servers)
- Results would likely differ from a semantic search on the same query

---

### Eval 3 — `search_tools` (hybrid mode)

**Tool:** `search_tools`
**Prompt:** "Find tools for working with GitHub — include both well-known tools and ones I might not know about."

**Why hybrid:** The phrase "well-known tools" calls for BM25 (exact "GitHub" keyword matches), while "ones I might not know about" calls for semantic search (adjacent tools: code review, CI/CD, issue tracking, repository management). Hybrid mode combines both via RRF fusion.

**Expected output:** A list of GitHub-related tools from `search_tools` with `mode: "hybrid"`. Results include directly-named GitHub tools plus semantically adjacent tools the user may not have thought to search for.

**Assertions:**
- `search_tools` is called with `mode: "hybrid"`
- At least 3 results are returned
- Results include tools directly named or described as GitHub tools
- Results include at least one tool in an adjacent domain (code review, CI/CD, issue tracking, or repository management) that a pure keyword search might not surface
- Results are not identical to what either semantic or BM25 mode alone would return

---

### Eval 4 — `get_tool_schema`

**Tool:** `get_tool_schema`
**Prompt:** "What exact parameters do I need to call the postgres query tool?"

**Why get_tool_schema:** This is the only way to retrieve a full JSON Schema and TypeScript interface for a specific tool. The skill (WebFetch path) has no equivalent — it can only retrieve package-level metadata, not tool-level call signatures.

**Expected output:** A full JSON schema for a postgres-related tool, including parameter names, types, and required/optional status — retrieved via `get_tool_schema` with a valid tool ID.

**Assertions:**
- `get_tool_schema` is called with a valid postgres-related tool ID (obtained via a prior `search_tools` call if needed)
- The response includes a JSON schema with a `properties` block
- Each property includes a type and description
- Required vs. optional parameters are distinguished
- The response is more detailed than what a registry metadata fetch would return (tool-level call signature, not just package identifier)

---

### Eval 5 — `recommend_tools` (similar_to)

**Tool:** `recommend_tools`
**Prompt:** "What MCP servers are similar to the GitHub MCP server?"

**Why similar_to:** The user is starting from a known server and wants to discover adjacent options. `similar_to` uses vector similarity over tool embeddings — it returns structurally or functionally similar tools, not keyword matches.

**Expected output:** A list of tools similar to the GitHub MCP server, retrieved via `recommend_tools` with `type: "similar_to"` and a valid GitHub server ID. Results should reflect functional similarity (code hosting, version control, CI/CD, developer workflow) not just name similarity.

**Assertions:**
- `recommend_tools` is called with `type: "similar_to"` and a valid GitHub server ID
- At least 3 results are returned
- Results include tools in functionally adjacent domains (code hosting, version control, CI/CD, issue tracking, developer workflow)
- Response is labeled as similarity-based, not a keyword search result
- The server ID used is resolved from real tool data, not invented

---

### Eval 6 — `recommend_tools` (for_task)

**Tool:** `recommend_tools`
**Prompt:** "I'm building an agent that monitors cloud infrastructure and sends alerts. What MCP tools should I use?"

**Why for_task:** The user has a task description, not a known starting server. `for_task` uses the task description as the search vector, returning tools most likely to help accomplish the task. This is distinct from both keyword search and similarity search.

**Expected output:** A list of tools recommended for the infrastructure monitoring and alerting task, retrieved via `recommend_tools` with `type: "for_task"` and a task description string. Results should be task-relevant (cloud providers, monitoring tools, alerting/notification tools).

**Assertions:**
- `recommend_tools` is called with `type: "for_task"` and a task description string
- At least 3 results are returned
- Results include tools relevant to cloud infrastructure, monitoring, or alerting/notifications
- Response is labeled as task-based recommendations, not a search result
- Results reflect the full task scope (not just "cloud" or just "alerts" in isolation)
