---
name: ai-news-brief
description: "Weekly AI/LLM briefing: pull the latest model releases from llm-info, enrich with capability deltas, render as a one-page deck (or markdown), optionally store the brief back into the user's knowledge graph for future search. Use when the user wants a periodic 'what's new in AI' summary, 'weekly AI brief', 'monthly LLM digest'."
compatibility: "Requires the mcpcentral-llm-info and mcpcentral-office MCP servers (auto-wired). The optional 'store back to library' step also requires mcpcentral-totext-cloud."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# ai-news-brief

Two-server (or three-server) pipeline: model registry → deck/markdown renderer → optional graph storage.

## Workflow

1. **Pull releases.** `mcp__mcpcentral-llm-info__list_latest(limit=20)` — newest models across all providers.
2. **Curate.** Drop trivial variants (e.g. duplicate format previews). Keep 5-8 with real capability gains: new modality, new family, big context jump, frontier release.
3. **Enrich the picks.** `get_model(provider_id, model_id)` for each curated pick (parallel) — pricing, context window, capability flags, documentation URL.
4. **Decide format.** If user wants slides → use `office-sandbox.deck-builder` template. If user wants markdown → render inline.
5. **Render.** One slide (or one section) per pick: name, date, provider, headline capability, price tier, link.
6. **Optional: store back.** If the user wants the brief searchable later, write the markdown to a temp file, generate a download URL, then `mcp__mcpcentral-totext-cloud__upload_url` with the URL of the brief.

## Output (deck mode)

```
AI brief — week of YYYY-MM-DD

Slides:
  1. Cover: "AI brief — week of YYYY-MM-DD"
  2. <provider>/<model> — <headline capability>
  3. ...
  N. Closing: "Next brief: YYYY-MM-DD"

Template: <template_name>
Deck: <download_url>  (TTL: 1h)

Stored to library: <document_id>  (optional, only if --store)
```

## Output (markdown mode)

A single markdown file with the same structure as the deck, ready to paste into Slack / email / a notes app.

## Gotchas

- **`list_latest` is sorted by date, not importance.** Curate; don't paste raw.
- **Per-week vs per-month framing matters.** A 1-week window may have only 2-3 interesting releases — don't pad to fill 8 slides.
- **`get_model` for null-pricing models is fine** but rendering should say "free (local)" not "$null".
- **The "store back" step is async on the totext-cloud side.** Tell the user the brief is queued for ingestion; entities/edges may take a minute.
- **Don't pick a deck template for what's really a one-pager.** A 5-slide deck is fine; a 25-slide deck for a weekly brief is bloat. Default to ≤8 slides, ≤1 page markdown.

## Examples

**User:** "Weekly AI brief, slides format."
→ `list_latest(limit=20)` → curate to 6 → parallel `get_model` ×6 → `deck-builder` workflow → return URL.

**User:** "Monthly brief, markdown, and save it to my library."
→ `list_latest(limit=40)` → curate to 10 → parallel `get_model` ×10 → render markdown → write to file → `container_file_download_url` → `upload_url` to totext-cloud.
