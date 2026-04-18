---
name: research-graph
description: "Answer a research question against the user's personal document graph. Hybrid (BM25 + semantic) search, expand via related documents, return ranked citations with quotes. Use when the user asks 'what do I have on X', 'what did I read about Y', 'find documents in my library about Z', or any question that should consult their own knowledge base before falling back to general web search."
compatibility: "Requires the mcpcentral-totext-cloud MCP server (auto-wired by the totext-graph plugin) and an authenticated mcpcentral.io account with documents already ingested."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# research-graph

Answer research questions from documents the user has already ingested into mcpcentral's totext-cloud.

## Workflow

1. **Search** — call `search_documents(query, limit=10)`. Hybrid (BM25 + semantic) by default — richer than `search`.
2. **Triage** — read the previews and summaries. Drop irrelevant hits before spending tokens on full text.
3. **Expand** — for each kept document, call `find_related_documents(document_id, limit=5)` to surface adjacent docs the search missed (parallel calls).
4. **Read selectively** — `get_document_text(document_id)` only on the 1-3 highest-quality docs needed to answer. Don't read everything.
5. **Cite** — return the answer with explicit citations: filename + document_id, plus a verbatim quote.
6. **Suggest follow-ups** — surface 2-3 related documents the user might want to read next.

## Output Template

```
Question: <original prompt>

Answer: <2-4 paragraph synthesis>

Sources:
  [1] <filename>  (id: <document_id>)
      "<verbatim quote>"
  [2] <filename>  (id: <document_id>)
      "<verbatim quote>"

Related (not consulted): <filename>, <filename>
```

## Gotchas

- **Empty library is normal for new users.** If `list_projects` returns `total: 0` and `search_documents` returns no hits, say so explicitly and offer the `knowledge-onboard` skill — don't fabricate answers.
- **`search` vs `search_documents`.** `search_documents` returns previews and summaries (richer); `search` is leaner. Default to `search_documents`.
- **Quality scores are 0-100.** Below ~60 the document was probably extracted poorly (scanned PDF, JS-heavy page) — quote with caution.
- **`find_related_documents` traversal can explode.** `max_hops` defaults to 1 — don't bump above 2 unless explicitly answering "what's downstream of this".
- **Don't read full text speculatively.** `get_document_text` returns the entire document; for a 50-page PDF that's a lot of tokens. Use the summary first.
- **Quote verbatim from `get_document_text`, not from your synthesis.** If you can't find the supporting quote in the actual document, your answer is overreaching.

## Examples

**User:** "What do I have on reinforcement learning?"
→ `search_documents("reinforcement learning", limit=10)` → triage → fetch the top 1-2 → answer with citations.

**User:** "Summarize my podcast appearances."
→ `search_documents("podcast", limit=20)` + `explore_entities(entity_type="topic", search="podcast")` → synthesize.
