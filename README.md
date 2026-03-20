# MCPCentral Plugin for Claude Code

Discover, search, and configure MCP servers — combining a knowledge skill with a semantic search MCP server in a single installable plugin.

## What's Included

| Component | Type | Description |
|-----------|------|-------------|
| **mcp-registry** | Skill | Teaches Claude how to query the [MCP Registry](https://registry.modelcontextprotocol.io) and [mcpcentral.io](https://mcpcentral.io) REST APIs to find, compare, and generate setup configs for MCP servers |
| **mcpcentral-tool-search** | MCP Server | Semantic + hybrid search over 1000+ MCP tools and servers via [tools.mcpcentral.io](https://tools.mcpcentral.io), with tool schema lookup, recommendations, and sandboxed code execution |

**The skill** handles direct registry API calls — searching by keyword, fetching server details, listing versions, and generating `claude_desktop_config.json` / `.mcp.json` snippets from real package metadata.

**The MCP server** adds semantic search (vector embeddings + BM25 hybrid), tool schema retrieval, similarity-based recommendations, and a sandboxed `execute` tool for orchestrating discovered servers.

Together, they give Claude comprehensive MCP server discovery whether you need quick registry lookups or deep semantic search.

## Installation

### Claude Code (Plugin Marketplace)

```bash
# Add the marketplace
/plugin marketplace add mcpcentral-io/skills

# Install the plugin
/plugin install mcpcentral@mcpcentral-skills
```

This installs both the skill and auto-connects the MCP server — no separate configuration needed.

### Manual Skill Installation

If you only want the skill (no MCP server), copy the skill folder into your project:

```bash
git clone https://github.com/mcpcentral-io/skills.git
cp -r skills/skills/mcp-registry your-project/.claude/skills/
```

## Authentication

The MCP server at `tools.mcpcentral.io` requires authentication. When connected via the plugin, Claude Code will handle the OAuth flow automatically — you'll be prompted to authenticate in your browser on first use.

For API key access, visit [mcpcentral.io](https://mcpcentral.io) to generate a key.

## MCP Server Tools

| Tool | Description |
|------|-------------|
| `search_tools` | Semantic + hybrid search for MCP tools and servers |
| `get_tool_schema` | Full JSON Schema and TypeScript interface for a specific tool |
| `recommend_tools` | Similarity-based or task-based tool recommendations |
| `execute` | Run code in a sandbox with bindings to discovered MCP servers (Deprecated) |
| `list_my_servers` | List your customized collections of MCP servers, managed on [mcpcentral.io](https://mcpcentral.io) |

## Skill Capabilities

The `mcp-registry` skill teaches Claude to:

- **Search** the official MCP Registry by keyword
- **Fetch** server details including packages, environment variables, and remote endpoints
- **Browse** popular servers via MCPCentral (sorted by GitHub stars)
- **Generate** setup configs for Claude Desktop, VS Code, and generic `.mcp.json`
- **Recommend** servers by synthesizing multi-keyword searches
- **Read** server documentation via repository README fetching

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json     # Plugin marketplace configuration
├── .mcp.json                # Bundled MCP server connection
├── skills/
│   └── mcp-registry/
│       ├── SKILL.md          # Skill instructions and API reference
│       └── evals/
│           ├── evals.json            # 5 skill evaluation test cases
│           └── mcp-server-evals.json # 6 MCP server evaluation test cases
├── README.md
├── .gitattributes
└── .gitignore
```

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

## Links

- [MCPCentral](https://mcpcentral.io) — MCP server directory with community metrics
- [MCP Registry](https://registry.modelcontextprotocol.io) — Official MCP server registry
- [Agent Skills Standard](https://agentskills.io) — Cross-platform skill specification
- [ClawCentral](https://clawcentral.io) — Our platform

