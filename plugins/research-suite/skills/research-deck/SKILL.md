---
name: research-deck
description: "End-to-end pipeline: search the user's knowledge graph for a topic, pick a cost-appropriate summarization model from the registry, render a real .pptx deck with citations, and return a download URL. Use when the user asks 'build me a deck on topic X using my own research', 'turn what I know about Y into slides', 'create a presentation from my library on Z'."
compatibility: "Requires three MCP servers, all auto-wired by the research-suite plugin: mcpcentral-totext-cloud, mcpcentral-llm-info, mcpcentral-office. Requires authenticated access to mcpcentral.io with documents already in the graph."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# research-deck

Three-server orchestration: knowledge graph → model picker → deck builder.

## Workflow

```
totext-cloud         llm-info          office
    │                    │                │
    ▼                    │                │
search_documents         │                │
find_related_documents   │                │
    │                    │                │
    ▼                    ▼                │
get_document_summary  recommend_model     │
    │ (1-3 docs)       (analysis, low)    │
    ▼                    ▼                │
   ─────── summary using picked model ────┤
                                          ▼
                                container_initialize
                                container_template_*
                                container_exec (python-pptx)
                                container_file_download_url
```

### Step-by-step

1. **Retrieve** — `search_documents(topic, limit=10)` + parallel `find_related_documents(top_doc_id)` for adjacents.
2. **Triage** — keep the 3-5 most relevant + highest-quality docs.
3. **Summarize** — fetch summaries via `get_document_summary` (one call per kept doc, parallel).
4. **Pick a model** — `mcp__mcpcentral-llm-info__recommend_model(use_case="analysis", budget="low", limit=3)`. Take the top pick that has `functions: true` (we'll need structured output for the slide outline).
5. **Generate the slide outline** using the picked model. Output: 5-8 slide structure with title + bullets + cited document_ids.
6. **Build the deck** — `office-sandbox.deck-builder` workflow: pick template, render, return download URL.
7. **Render with citations** — every slide that quotes the library shows the source filename in the footer.

## Output

```
Topic: <topic>

Sources consulted (5):
  • <filename>  (id, quality)
  • ...

Model used for outline: <provider>/<model>
Template: <template_name>
Slides: 6

Deck: <download_url>  (TTL: 1h)
```

## Gotchas

- **Don't include the model used in the deck itself.** Cite the documents (real sources), not the LLM that generated the bullets.
- **Outline length matters.** Fewer slides (5-6) > many slides (15+) for executive briefings. Default to 6 unless asked otherwise.
- **Citations should reference filenames, not document_ids.** Document IDs are noise on a slide. Map to filename + index footnote.
- **If the library is empty for the topic**, fall back to `research-graph` skill behavior (say so explicitly) — don't fabricate a deck from general knowledge.
- **Don't re-fetch the model pick per slide.** One `recommend_model` call at the start, reuse the pick for all summarization within the run.

## Examples

**User:** "Build me a 6-slide briefing on reinforcement learning from my library."
→ `search_documents("reinforcement learning", limit=10)` → triage → summaries → `recommend_model(use_case="analysis", budget="low")` → outline → deck → URL.
