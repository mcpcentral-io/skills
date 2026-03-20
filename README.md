# MCPCentral Plugin for Claude Code

Discover, search, and configure MCP servers — combining a knowledge skill with a semantic search MCP server in a single installable plugin.

## What's Included

| Component | Type | Description |
|-----------|------|-------------|
| **mcp-registry** | Skill | Teaches Claude how to query the [MCP Registry](https://registry.modelcontextprotocol.io) and [mcpcentral.io](https://mcpcentral.io) REST APIs to find, compare, and generate setup configs for MCP servers |
| **mcpcentral-tool-search** | MCP Server | Semantic + hybrid search over 1000+ MCP tools and servers via [tools.mcpcentral.io](https://tools.mcpcentral.io), with tool schema lookup, recommendations, and sandboxed code execution |
| **to-text** | Skill | Universal content extraction and summarization — OCR, audio/video transcription, document conversion, and URL extraction with local LLM summarization via Ollama |

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
│   ├── mcp-registry/         # MCP server discovery skill
│   └── to-text/              # Universal content extraction skill
├── README.md
├── .gitattributes
└── .gitignore
```

## Evals

Each skill and MCP server includes an `evals/` directory with evaluation test cases for validating behavior.

## Links

- [MCPCentral](https://mcpcentral.io) — MCP server directory with community metrics
- [MCP Registry](https://registry.modelcontextprotocol.io) — Official MCP server registry
- [Agent Skills Standard](https://agentskills.io) — Cross-platform skill specification
- [ClawCentral](https://clawcentral.io) — Our platform

