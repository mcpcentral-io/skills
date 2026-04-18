---
name: model-changelog
description: "Digest of recently released LLMs with capability highlights, organized by provider. Use when the user asks 'what's new in LLMs', 'what models came out this week', 'latest releases from Anthropic / Gemini / OpenAI', or wants a regular changelog brief."
compatibility: "Requires the mcpcentral-llm-info MCP server (auto-wired by the llm-info plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# model-changelog

Build a concise "what's new" digest from `list_latest`, optionally enriched with full specs.

## Workflow

1. **Call `list_latest(limit=20)`** (or filter by `provider` if the user named one).
2. **Group by provider** and sort within each group by `created_at` descending.
3. **For each model, render** a one-line entry: name, release date, headline capability (vision / thinking / huge context / new family).
4. **Optionally** for the top 3 most-interesting picks, call `get_model` to surface pricing and full capability flags.
5. **End with** a 2-3 sentence "what changed this period" narrative — flag obvious patterns (e.g. "Gemini shipped 4 vision/audio variants this week").

## Output Template

```
LLM releases — last <N> models

Anthropic
  • claude-opus-4-7 (2026-04-14)  — flagship, 1M context
  • ...

Gemini
  • gemini-3.1-flash-tts-preview (2026-04-16)  — TTS variant
  • gemini-robotics-er-1.6-preview (2026-04-15)  — robotics ER
  • ...

Ollama (local + cloud)
  • glm-5.1 (2026-04-07)
  • gemma4:31b (2026-04-02)
  • ...

What changed: <2-3 sentence narrative>
```

## Gotchas

- **`list_latest` is sorted by release_date, not by importance.** A TTS preview can outrank a frontier model. Curate when summarizing — don't just paste the raw list.
- **Capability flags are often null on previews.** A new model with `supports_vision: 0` may simply not have its capabilities filled in yet. Don't claim "no vision" without checking the model's documentation_url.
- **Some providers ship many variants per week** (Gemini in particular). Group variants of the same family on a single line with parenthesised dates rather than enumerating each.
- **`provider_id` and `model_id` together identify the model**, not `model_id` alone. There can be e.g. an `ollama-cloud` and a `gemini` entry for the same `model_id`.

## Examples

**User:** "What did Anthropic ship recently?"
→ `list_latest(provider="anthropic", limit=10)` → group, render.

**User:** "Weekly LLM brief."
→ `list_latest(limit=20)` → group by provider → narrative summary.
