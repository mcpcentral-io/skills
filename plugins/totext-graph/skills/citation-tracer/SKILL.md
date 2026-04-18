---
name: citation-tracer
description: "Trace citation lineage forwards/backwards from a document — what cites it, what it cites, supersedes/precedes chains. Use when the user asks 'what cites this paper', 'what does this article reference', 'show the lineage of this document', or wants to understand how a source fits into a body of work."
compatibility: "Requires the mcpcentral-totext-cloud MCP server (auto-wired by the totext-graph plugin) with cite/reference edges already populated. Run knowledge-onboard with rebuild_graph_edges if edges look sparse."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# citation-tracer

Walk the citation / reference / supersedes graph forward and backward from a starting document.

## Workflow

1. **Resolve the starting document.** Either the user gives a `document_id`, or you call `search_documents(query)` and pick the top hit (confirm with the user before traversing).
2. **Trace lineage.** `trace_document_lineage(document_id)` returns the canonical chain.
3. **Find direct citations.** `find_related_documents(document_id, relationship_types=["cites","references"], max_hops=1)` for what this doc cites.
4. **Find inbound citations.** `graph_search(start_document_id, edge_types=["cites","references"], max_hops=2)` to discover what cites it.
5. **Render** the lineage tree (template below).

## Output Template

```
Document: <filename>  (id: <document_id>)

Lineage chain:
  ⤴ supersedes: <filename> → <filename>
  ● THIS DOCUMENT
  ⤵ superseded by: <filename>

Cites (outbound, N):
  → <filename>  (relationship: cites)
  → <filename>  (relationship: references)

Cited by (inbound, M, max_hops=2):
  ← <filename>  (1 hop)
  ← <filename>  (2 hops, via <intermediate>)
```

## Gotchas

- **Edges may be sparse.** Many documents have no `cites` / `references` edges at all if the extractor didn't pick up structured citations. Don't conclude "this is unique" — say "no citation edges found in the graph; the source may not have been processed for citations".
- **`supersedes` and `precedes` are temporal**, not citation. Use them to find newer/older versions of the same content (e.g. v1 → v2 of a paper), not influence relationships.
- **`max_hops` >2 explodes fast.** Stick to 2 unless the user explicitly asks for ancestral traversal.
- **`graph_search` requires `start_document_id`.** Don't try to call it with a query string — find the doc first via `search_documents`.
- **`min_similarity` filters semantic edges only**, not cite/reference edges. Don't pass it when restricting to `relationship_types=["cites","references"]`.

## Examples

**User:** "What cites the reinforcement learning Wikipedia article in my library?"
→ `search_documents("reinforcement learning")` → pick top → `graph_search(start_document_id, edge_types=["cites","references"], max_hops=2)`.

**User:** "Show the full lineage of document <id>."
→ `trace_document_lineage(<id>)` → render.
