---
name: knowledge-onboard
description: "Bulk-ingest URLs and files into the personal knowledge graph and verify entity/edge graph is built. Use when the user wants to add a list of URLs to their library, onboard a new project from scratch, or rebuild the graph after a large import. Pairs with totext-local for local files: extract first, then onboard the result."
compatibility: "Requires the mcpcentral-totext-cloud MCP server (auto-wired by the totext-graph plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# knowledge-onboard

Get content into the graph and confirm it's properly indexed.

## Workflow

### A) URL ingestion

1. **For each URL**, call `upload_url(url)` (parallel, batched 5 at a time to avoid rate limits).
2. **Wait briefly** then call `list_documents(filename_contains=<url-fragment>)` to confirm each one landed.
3. **Report** which URLs succeeded, which failed, and any duplicates the server collapsed.

### B) Local file ingestion (via totext-local)

1. Run `totext-local` to extract text + summary from local files.
2. For each result, call `upload_url` if the source had a URL, or use the totext-cloud upload-file flow (out of scope here — flag to the user).

### C) Post-ingest verification

1. **`list_projects`** → confirm doc count went up.
2. **`explore_entities(limit=20)`** → quick sanity check that entities are being extracted.
3. **If entities look sparse** (or after a bulk re-import), call **`rebuild_graph_edges`** to recompute similarity / cites / mentions edges. This is expensive — confirm with the user before invoking.
4. Optionally **`cleanup_orphaned_vectors`** if the user has been deleting documents — frees vector storage.

## Output

```
Ingest: 12 URLs submitted

Succeeded (10):
  • https://...   (id: <doc_id>)
  • ...

Failed (1):
  • https://...   reason: <error>

Duplicates (1, collapsed by server):
  • https://...   existing id: <doc_id>

Library now: <total_docs> documents (was N before).
Entities sampled: 20 (top: <name>, <name>, <name>...).

Recommendation: <run rebuild_graph_edges? cleanup_orphaned_vectors?>
```

## Gotchas

- **`upload_url` is async on the server side.** A successful response does NOT mean entities are extracted yet — wait or re-check via `list_documents` before claiming the doc is fully ingested.
- **`rebuild_graph_edges` is expensive.** Don't call it after every single upload; batch up imports first, then run it once at the end.
- **`cleanup_orphaned_vectors` is destructive in spirit.** It removes embeddings for documents that no longer exist. Safe to run, but tell the user what it does before invoking.
- **There's no native batch upload tool.** You parallelize `upload_url` yourself — batch 5 at a time, not 50, to avoid hitting rate limits.
- **Some URLs are JS-heavy and the server's fetcher will fail.** For those, the user should run `totext-local` (which has the Exa→Firecrawl→Jina fallback chain) to extract first, then upload the resulting text via a separate path.

## Examples

**User:** "Add these 5 URLs to my library: ..."
→ Parallel `upload_url` (×5) → `list_documents(filename_contains=...)` to verify → report.

**User:** "I just imported 200 papers, rebuild the graph."
→ `list_projects` for current state → `rebuild_graph_edges` → `explore_entities` to confirm new entities materialized.
