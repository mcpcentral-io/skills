---
name: model-cost-estimate
description: "Estimate monthly LLM cost for a workload across N candidate models and recommend the cheapest viable. Use when the user describes a usage pattern ('1M input tokens/day, 200K output, 70% cache hit') and asks 'how much will this cost' or 'which model is cheapest for this load'."
compatibility: "Requires the mcpcentral-llm-info MCP server (auto-wired by the llm-info plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# model-cost-estimate

Translate a workload description into a per-model monthly cost table, then recommend the cheapest model that meets stated capability requirements.

## Workflow

1. **Extract the workload** from the user's prompt:
   - `input_tokens_per_call`
   - `output_tokens_per_call`
   - `calls_per_day`
   - `cache_hit_rate` (default 0 if prompt caching not mentioned)
   - `required_capabilities` (default `[]`)
2. **Build the candidate list.** Either the user names models, or call `compare_pricing` with their hinted family / providers. If they didn't hint, use `recommend_model(use_case=..., budget="low", limit=5)` to seed.
3. **For each candidate, call `get_model`** to fetch the latest pricing (parallel calls).
4. **Compute monthly cost** per the formula below.
5. **Filter** out candidates that fail any required capability.
6. **Render the table** sorted by monthly cost ascending and recommend the top row.

## Cost Formula (per model, per month, 30 days)

```
calls_per_month     = calls_per_day * 30
input_total         = calls_per_month * input_tokens_per_call
output_total        = calls_per_month * output_tokens_per_call

cache_read_tokens   = input_total * cache_hit_rate
fresh_input_tokens  = input_total * (1 - cache_hit_rate)

cost = (fresh_input_tokens * input_price_per_mtok / 1e6)
     + (cache_read_tokens  * cache_read_price_per_mtok / 1e6)
     + (output_total       * output_price_per_mtok / 1e6)
```

If a model lacks `cache_read_price_per_mtok`, set it equal to `input_price_per_mtok` (no cache benefit) and note that in the row.

## Output

```
Workload: 1.0M input/call × 200K output/call × 100 calls/day × 70% cache hit

Model                            input    cache-read   output   monthly cost
anthropic/claude-haiku-4-5       $0.80    $0.08        $4.00    $XX
anthropic/claude-sonnet-4-6      $3.00    $0.30        $15.00   $XX
openai/gpt-4o-mini               $0.15    n/a          $0.60    $XX  (no cache benefit)
...

Cheapest viable: <model>  ($XX/month)
Cheapest with prompt_caching: <model>  ($XX/month)
```

## Gotchas

- **Cache hit rate >0 only helps if `supports_prompt_caching: 1`.** Don't apply the cache discount to models without the flag.
- **Local models report null prices.** Render as "free (local)" and skip them in the cheapest-viable line unless the user asked for local options.
- **Per-MTok prices are exact, not "approximately".** Don't round in the formula; round only at display time (typically to 2 decimal places).
- **Rate limits matter at high volumes.** If `calls_per_day` × tokens-per-call exceeds a model's `tpm_limit * 60 * 24`, flag it as throughput-infeasible — cheap on paper, throttled in practice.
- **Cache write cost is real.** First-call pricing uses `cache_write_price_per_mtok` (often higher than input). For low-volume / one-shot workloads, factor it in or disable the cache assumption.
