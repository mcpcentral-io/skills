---
name: entity-dossier
description: "Build a dossier on a person, company, topic, date, or location from documents in the user's graph: who/what they are, where they appear, who they co-occur with, key documents. Use when the user asks 'tell me what I know about X', 'build a profile for company Y', 'who else have I read about alongside Z'."
compatibility: "Requires the mcpcentral-totext-cloud MCP server (auto-wired by the totext-graph plugin) with documents and entities already extracted."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# entity-dossier

Compile a structured profile of an entity by walking the document graph's entity index.

## Workflow

1. **Resolve the entity.** Call `explore_entities(search=<name>, entity_type=<type>)` to find the entity's `entity_id`. Disambiguate if multiple matches.
2. **Fetch documents.** `get_entity_documents(entity_id)` returns every document the entity appears in.
3. **Find co-occurring entities.** `find_entity_connections(entity_ids=[entity_id], connection_type="and", limit=20)` is not the right tool here — that needs ≥2 entities. Instead, fetch each document's entity list (via `get_document_text` or `get_document_summary`) or call `explore_entities` repeatedly. A faster path: enumerate the top documents and report the most-common other entities found.
4. **Summarize each key document.** `get_document_summary(document_id)` is cheaper than `get_document_text`.
5. **Assemble the dossier** (template below).

## Dossier Template

```
Entity: <name>  (type: <person|company|topic|date|location>, id: <entity_id>)

Document appearances: N

Top documents:
  • <filename>  (quality: NN)  — <one-line summary>
  • ...

Most-common co-occurrences:
  • <other-entity> (in M of N docs)
  • ...

Recent mention: <filename> (created_at)

Open questions to research: <2-3 followups based on co-occurrence patterns>
```

## Gotchas

- **`explore_entities` is fuzzy.** Searching "Cameron" may return multiple Camerons; always show the `entity_id` and disambiguate before proceeding.
- **`entity_type` enum is fixed:** `person | company | topic | date | location`. Don't pass other strings.
- **Co-occurrence math is per-document, not per-mention.** "Anthropic appears with OpenAI in 8 of 12 docs" means 8 documents mention both — not 8 sentences.
- **`find_entity_connections` requires ≥2 entities.** It's the wrong shape for "what does X co-occur with"; use it when the user already named two or more entities ("docs that mention both Anthropic and Google").
- **No date-range filter on entities.** If the user asks for "what I've read about X this year", you have to filter the document list yourself by `created_at`.
- **Topic entities can be very fuzzy.** "AI safety" and "ai safety" may be two entries — explore both before claiming completeness.

## Examples

**User:** "Build me a dossier on Anthropic."
→ `explore_entities(search="Anthropic", entity_type="company")` → `get_entity_documents(entity_id)` → summarize top 5.

**User:** "What do I have on documents that mention both OpenAI and Anthropic?"
→ `find_entity_connections(entity_names=["OpenAI", "Anthropic"], connection_type="and")` → render co-occurrence table.
