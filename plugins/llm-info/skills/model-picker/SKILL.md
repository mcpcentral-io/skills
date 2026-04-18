---
name: model-picker
description: "Pick the right LLM for a use case and budget using real registry data. Use when the user asks 'which model should I use for X', 'cheapest model that supports vision', 'best coding model under $5/MTok', 'recommend a thinking model', or any model-selection question with capability or price constraints."
compatibility: "Requires the mcpcentral-llm-info MCP server (auto-wired by the llm-info plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# model-picker

Walk the user from a fuzzy goal ("I need a coding model under $5/MTok with vision") to a concrete `provider_id` / `model_id` plus a rationale grounded in the live registry.

## Workflow

1. **Parse the request** into (`use_case`, `budget`, `required_capabilities`).
2. **Call `recommend_model`** with those inputs. Returns ranked candidates with rationale.
3. **Filter** candidates that fail any required capability check (e.g. vision asked, model lacks vision).
4. **Show top 3** with model_id, price/MTok in/out, context window, capability flags, and the registry's rationale.
5. If the user wants the full spec for one of them, call **`get_model(provider_id, model_id)`** and surface pricing, rate limits, training cutoff, documentation URL.

## Inputs to recommend_model

| Field | Allowed values | Notes |
|---|---|---|
| `use_case` | `code_generation`, `chat`, `analysis`, `reasoning`, `vision`, `budget` | Map the user's goal to one of these. Default to `chat` if ambiguous. |
| `budget` | `low` (<$1/MTok), `medium` ($1–10/MTok), `high` (>$10/MTok) | Default `medium`. |
| `required_capabilities` | `vision`, `functions`, `streaming`, `prompt_caching`, `json_mode`, `thinking` | Pass only what the user explicitly needs. |
| `limit` | int (default 5) | Bump to 10 for "show me everything" requests. |

## Output Shape

For each top pick, render:

```
1. <provider> / <model>  — score N/100
   $<input>/MTok in,  $<output>/MTok out,  <context_window> tokens
   capabilities: vision ✓ functions ✓ thinking ✗
   rationale: <as returned by the registry>
```

End with a one-sentence recommendation pointing to one of the picks.

## Gotchas

- **`required_capabilities` is strict.** A model that doesn't list a flag will be excluded — don't pass capabilities the user didn't ask for "just to be safe", or you'll over-filter.
- **The `vision` use_case implies vision capability** but the recommender doesn't always set it as a hard requirement. Always also pass `required_capabilities: ["vision"]` when the user wants OCR / image input.
- **Prices in the registry are per million tokens.** Some models distinguish `cache_write_price_per_mtok` and `cache_read_price_per_mtok` — surface those when prompt caching is a stated requirement.
- **Ollama models report `is_local: 1`** and may have null prices — don't crash on null; render as "free (local)".
- **Coding-index rationales** like `Coding index: 37.8` come from the registry's internal benchmarks, not from your reasoning. Quote them verbatim, don't invent comparable scores.

## Examples

**User:** "Cheapest vision model for OCR."
→ `recommend_model(use_case="vision", budget="low", required_capabilities=["vision"])`
→ filter to those where `capabilities.vision === true`, return top 3.

**User:** "Best reasoning model regardless of cost."
→ `recommend_model(use_case="reasoning", budget="high", required_capabilities=["thinking"], limit=5)`.

**User:** "I want to use prompt caching to bring my Claude bill down."
→ `recommend_model(use_case="chat", budget="medium", required_capabilities=["prompt_caching"])` — then for each pick fetch `get_model` and show `cache_read_price_per_mtok` vs `input_price_per_mtok`.
