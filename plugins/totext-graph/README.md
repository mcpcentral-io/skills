# totext-graph Plugin

Personal document **knowledge graph** skills, powered by [`mcpcentral-totext-cloud`](https://totext.mcpcentral.io/mcp).

Hybrid (BM25 + semantic) search across your uploaded documents, automatic entity extraction (people / companies / topics / dates / locations), citation and reference traversal up to 3 hops, and topic clustering.

The local-extraction sibling is the `mcpcentral` plugin's `totext-local` skill — use that for one-shot file extraction, then `knowledge-onboard` here to get the result into the graph.

## Install

```bash
/plugin marketplace add mcpcentral-io/skills
/plugin install totext-graph@mcpcentral-skills
```

The plugin's `.mcp.json` auto-wires `mcpcentral-totext-cloud`. Sign in via the OAuth flow on first use.

## Skills

| Skill | When to invoke |
|---|---|
| `research-graph` | "What do I have on topic X?" — answer a research question from your library |
| `entity-dossier` | "Build a dossier on person/company/topic Y" — co-occurrence + key documents |
| `citation-tracer` | "What cites this paper?" / "What does this article reference?" — lineage traversal |
| `knowledge-onboard` | Bulk-ingest URLs / documents into the graph and verify edges are built |

## Backing MCP Tools

Discovery:
- `list_projects`, `list_documents`, `search`, `search_documents`

Documents:
- `get_document_text`, `get_document_summary`, `find_similar`, `find_related_documents`

Entities:
- `explore_entities`, `get_entity_documents`, `find_entity_connections`

Graph:
- `graph_search`, `get_topic_cluster`, `trace_document_lineage`

Maintenance:
- `fetch`, `upload_url`, `rebuild_graph_edges`, `cleanup_orphaned_vectors`

## Evals

Each skill ships with `evals/evals.json` and `evals/mcp-server-evals.json`.
