# MCP Server Evals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `skills/mcp-registry/evals/mcp-server-evals.json` with 6 evaluation test cases covering the unique capabilities of the `mcpcentral-tool-search` MCP server.

**Architecture:** A single JSON file mirroring the existing `evals.json` format, with an added `tool` field per eval. Each eval targets a capability the skill cannot replicate via WebFetch: semantic search, BM25 keyword search, hybrid search, tool schema retrieval, similarity-based recommendations, and task-based recommendations.

**Tech Stack:** JSON (no runtime dependencies)

**Key files:**
- `skills/mcp-registry/evals/evals.json` — existing skill evals, for format reference
- `docs/superpowers/specs/2026-03-20-mcp-server-evals-design.md` — spec with full eval definitions

---

### Task 1: Create mcp-server-evals.json

**Files:**
- Create: `skills/mcp-registry/evals/mcp-server-evals.json`

- [ ] **Step 1: Validate the existing evals.json structure**

  Confirm the format to match before writing:

  ```bash
  cat skills/mcp-registry/evals/evals.json
  ```

  Expected: JSON with `skill_name` and `evals[]` at the top level, each eval having `id`, `prompt`, `expected_output`, and `assertions[]`.

- [ ] **Step 2: Create the file with all 6 evals**

  Create `skills/mcp-registry/evals/mcp-server-evals.json` with this exact content:

  ```json
  {
    "skill_name": "mcpcentral-tool-search",
    "evals": [
      {
        "id": 1,
        "tool": "search_tools",
        "prompt": "Find MCP tools that help AI agents persist memory and context between sessions.",
        "expected_output": "A list of tools related to agent memory and context persistence (e.g., vector stores, embedding tools, session managers, knowledge bases), surfaced via search_tools with mode: semantic. Results reflect conceptual relevance, not just literal keyword overlap.",
        "assertions": [
          "search_tools is called with mode: \"semantic\"",
          "At least 3 results are returned",
          "Results are conceptually relevant to memory or context persistence (e.g., vector stores, embedding tools, session managers, knowledge bases)"
        ]
      },
      {
        "id": 2,
        "tool": "search_tools",
        "prompt": "Search for MCP servers with 'postgres' in the name or description.",
        "expected_output": "A list of tools whose names or descriptions contain the exact term 'postgres', retrieved via search_tools with mode: bm25.",
        "assertions": [
          "search_tools is called with mode: \"bm25\"",
          "At least 1 result is returned",
          "All results contain 'postgres' in the tool name or description (no semantically-adjacent-but-unrelated tools like generic 'database' or 'SQL' servers that don't mention postgres)"
        ]
      },
      {
        "id": 3,
        "tool": "search_tools",
        "prompt": "Find tools for working with GitHub — include both well-known tools and ones I might not know about.",
        "expected_output": "A list of GitHub-related and adjacent tools from search_tools with mode: hybrid. Results include directly-named GitHub tools plus semantically adjacent tools (code review, CI/CD, issue tracking, repository management).",
        "assertions": [
          "search_tools is called with mode: \"hybrid\"",
          "At least 3 results are returned",
          "Results include tools directly named or described as GitHub tools",
          "Results include at least one tool in an adjacent domain (code review, CI/CD, issue tracking, or repository management)"
        ]
      },
      {
        "id": 4,
        "tool": "get_tool_schema",
        "prompt": "What exact parameters do I need to call the postgres query tool?",
        "expected_output": "A full JSON schema for a postgres query tool, including parameter names, types, and required/optional status. The serverId is resolved via a prior search_tools call; the toolName ('query') is inferred from the prompt.",
        "assertions": [
          "search_tools is first called to identify a valid postgres-related server ID (the ID is not invented)",
          "get_tool_schema is called with both a serverId and a toolName (not a single combined ID string)",
          "The serverId is obtained from the prior search_tools result, not fabricated",
          "The response includes a JSON schema with a properties block",
          "Each property in the schema includes a type and description",
          "Required vs. optional parameters are distinguished in the response"
        ]
      },
      {
        "id": 5,
        "tool": "recommend_tools",
        "prompt": "What MCP servers are similar to the GitHub MCP server?",
        "expected_output": "A list of servers similar to the GitHub MCP server, retrieved via recommend_tools with type: similar_to and a server-level ID resolved from a prior search_tools call. Results reflect functional similarity (code hosting, version control, CI/CD, developer workflow).",
        "assertions": [
          "search_tools is first called to identify a real GitHub server ID (the ID is not invented)",
          "recommend_tools is called with type: \"similar_to\" and a serverId obtained from the prior search (server-level ID, not tool-level)",
          "At least 3 results are returned",
          "Results include servers in functionally adjacent domains (code hosting, version control, CI/CD, issue tracking, developer workflow)",
          "Response is labeled as similarity-based recommendations, not a keyword search result"
        ]
      },
      {
        "id": 6,
        "tool": "recommend_tools",
        "prompt": "I'm building an agent that monitors cloud infrastructure and sends alerts. What MCP tools should I use?",
        "expected_output": "A list of tools recommended for the infrastructure monitoring and alerting task, retrieved via recommend_tools with type: for_task and a taskDescription string. Results are task-relevant (cloud providers, monitoring tools, alerting/notification tools).",
        "assertions": [
          "recommend_tools is called with type: \"for_task\" and a taskDescription string derived from the user's prompt",
          "At least 3 results are returned",
          "Results include tools relevant to cloud infrastructure, monitoring, or alerting/notifications",
          "Response is labeled as task-based recommendations, not a search result",
          "Results reflect the full task scope (not just 'cloud' or just 'alerts' in isolation)"
        ]
      }
    ]
  }
  ```

- [ ] **Step 3: Validate the JSON is well-formed**

  Run from the repository root (`/Users/cam/GITHUB/skills`):

  ```bash
  python3 -m json.tool skills/mcp-registry/evals/mcp-server-evals.json > /dev/null && echo "Valid JSON"
  ```

  Expected output: `Valid JSON`

- [ ] **Step 4: Verify structure matches evals.json conventions**

  Run from the repository root (`/Users/cam/GITHUB/skills`). Checks top-level keys and per-eval required fields:

  ```bash
  python3 -c "
  import json
  with open('skills/mcp-registry/evals/mcp-server-evals.json') as f:
      data = json.load(f)
  assert 'skill_name' in data, 'missing skill_name'
  assert 'evals' in data, 'missing evals'
  assert len(data['evals']) == 6, f'expected 6 evals, got {len(data[\"evals\"])}'
  for e in data['evals']:
      for field in ('id', 'tool', 'prompt', 'expected_output', 'assertions'):
          assert field in e, f'eval {e.get(\"id\")} missing field: {field}'
      assert isinstance(e['assertions'], list) and len(e['assertions']) > 0, f'eval {e[\"id\"]} has empty assertions'
  tools = [e['tool'] for e in data['evals']]
  assert tools.count('search_tools') == 3, f'expected 3 search_tools evals, got {tools.count(\"search_tools\")}'
  assert tools.count('get_tool_schema') == 1, 'expected 1 get_tool_schema eval'
  assert tools.count('recommend_tools') == 2, 'expected 2 recommend_tools evals'
  modes = [e['assertions'][0] for e in data['evals'] if e['tool'] == 'search_tools']
  assert any('semantic' in m for m in modes), 'missing semantic mode eval'
  assert any('bm25' in m for m in modes), 'missing bm25 mode eval'
  assert any('hybrid' in m for m in modes), 'missing hybrid mode eval'
  print('All checks passed')
  "
  ```

  Expected output: `All checks passed`

- [ ] **Step 5: Commit**

  ```bash
  git add skills/mcp-registry/evals/mcp-server-evals.json
  git commit -m "feat: add MCP server evals for mcpcentral-tool-search"
  ```

---

### Task 2: Update README to reference mcp-server-evals.json

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current Evals section**

  ```bash
  grep -n "Evals" README.md
  ```

- [ ] **Step 2: Update the Evals section**

  Find the Evals section (currently lists 5 skill eval descriptions) and add a subsection for the MCP server evals. Replace the existing Evals section with:

  ```markdown
  ## Evals

  ### Skill Evals (`evals/evals.json`)

  5 evaluation test cases covering direct REST API usage:

  1. Registry search (PostgreSQL servers)
  2. Server detail fetching (filesystem server)
  3. Config generation (GitHub server for Claude Desktop)
  4. Popularity browsing (top 10 by GitHub stars)
  5. Multi-keyword recommendation synthesis (email servers)

  ### MCP Server Evals (`evals/mcp-server-evals.json`)

  6 evaluation test cases covering the unique capabilities of the `mcpcentral-tool-search` MCP server:

  1. Semantic search (`search_tools`, mode: semantic)
  2. BM25 keyword search (`search_tools`, mode: bm25)
  3. Hybrid search with RRF fusion (`search_tools`, mode: hybrid)
  4. Tool schema retrieval (`get_tool_schema`)
  5. Similarity-based recommendations (`recommend_tools`, type: similar_to)
  6. Task-based recommendations (`recommend_tools`, type: for_task)
  ```

- [ ] **Step 3: Update the Repository Structure block**

  In `README.md`, find the Repository Structure block (the `evals/` subsection currently shows only `evals.json`). Replace it so both files appear:

  ```
  │       └── evals/
  │           ├── evals.json            # 5 skill evaluation test cases
  │           └── mcp-server-evals.json # 6 MCP server evaluation test cases
  ```

- [ ] **Step 4: Verify README renders correctly**

  ```bash
  grep -A 25 "## Evals" README.md
  ```

  Expected: both subsections visible with correct counts (5 skill evals, 6 MCP server evals).

  ```bash
  grep "mcp-server-evals" README.md
  ```

  Expected: appears in both the Repository Structure block and the MCP Server Evals subsection.

- [ ] **Step 5: Commit**

  ```bash
  git add README.md
  git commit -m "docs: add MCP server evals section to README"
  ```
