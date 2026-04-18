---
name: model-migrate
description: "Generate a migration guide between two LLMs (e.g. gpt-4o → claude-sonnet-4-6, or claude-3-5-sonnet → claude-opus-4-7). Reports pricing delta, capability gains/losses, prompt-caching parity, context-window changes, and SDK-level concerns. Use when the user asks 'how do I migrate from X to Y', 'what changes if I switch from A to B', 'compare these two models for me'."
compatibility: "Requires the mcpcentral-llm-info MCP server (auto-wired by the llm-info plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# model-migrate

Side-by-side migration report for two specific models, grounded in registry data.

## Workflow

1. **Parse the from / to models** from the user's prompt. Disambiguate provider if ambiguous (e.g. "claude-sonnet" → ask which version).
2. **Call `get_model`** on each side. Two parallel calls.
3. **Optionally call `compare_pricing`** with the model_family (e.g. `claude-4`) to surface adjacent options the user didn't explicitly ask about.
4. **Render the diff** (see template below).
5. **Flag SDK-level migration concerns** based on `message_format` and `extra_headers` deltas.

## Diff Template

```
Migration: <from-provider>/<from-model>  →  <to-provider>/<to-model>

Pricing per MTok
  input:  $A → $B  (Δ ±X%)
  output: $A → $B  (Δ ±X%)
  cache read:   $A → $B
  cache write:  $A → $B

Context window: A → B tokens (Δ ±X%)
Max output:     A → B tokens

Capabilities
  vision:           ✓ → ✓
  functions:        ✓ → ✓
  thinking:         ✗ → ✓   ← gained
  prompt_caching:   ✓ → ✓
  json_mode:        ✓ → ✗   ← LOST  (verify your code path doesn't depend on this)

SDK / API
  message_format:   anthropic → anthropic   (no SDK change)
  extra_headers:    "anthropic-beta: prompt-caching-2024-07-31" → null   (drop the header)
  api_version:      2023-06-01 → null

Rate limits
  RPM:  A → B
  TPM:  A → B
```

End with a 2-3 sentence summary: net win, net loss, or trade-off, and the one thing the user should test first.

## Gotchas

- **Same `message_format` does not mean drop-in.** Anthropic ↔ Anthropic still differs in `extra_headers` (e.g. prompt-caching beta header dropped on newer models). Surface the header diff explicitly.
- **`supports_*: 0` means "not declared", not necessarily "definitely unsupported".** For brand-new preview models, capability flags may still be filled in. If both sides show 0 for the same capability, treat as unknown rather than as a loss.
- **Pricing deltas can be misleading without cache hit rate.** A 2× input price hike can still net a saving if cache_read drops 5×. Mention this when both models support prompt_caching.
- **Use the `created_at` / `release_date` to flag stale picks.** If the "to" model is older than the "from" model, ask whether the user actually meant the newer direction.

## Examples

**User:** "Migrate from gpt-4o to claude-sonnet-4-6."
→ `get_model("openai", "gpt-4o")` + `get_model("anthropic", "claude-sonnet-4-6")` in parallel → render diff.

**User:** "I'm on claude-3-5-sonnet, should I move to claude-opus-4-7?"
→ Both `get_model` calls + `compare_pricing(model_family="claude-4")` to surface Sonnet 4.6 as a middle option.
