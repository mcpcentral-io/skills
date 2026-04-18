#!/usr/bin/env python3
"""
Pick a summarization model for a given content type.

Strategy:
  1. Map content_type -> use_case (vision, chat, analysis).
  2. Call mcp__mcpcentral-llm-info__recommend_model via the MCP host.
  3. If unreachable, fall back to a static map so the skill still works offline.

This script does NOT call MCP itself (MCP is the host's job). Instead, when run
from inside Claude Code the host is expected to invoke
`mcp__mcpcentral-llm-info__recommend_model` and pipe its JSON result back via
`--llm-info-json -`. When run standalone (no MCP host), the static fallback is
used. This keeps the script unit-testable and avoids a hard MCP runtime
dependency.

Usage:
    pick_summarizer.py <content_type> [--size-bytes N]
                                       [--budget low|medium|high]
                                       [--llm-info-json FILE_OR_DASH]

Output (stdout): JSON object with provider_id, model_id, rationale, source.

Examples:
    # Pick for an image with default low budget
    pick_summarizer.py image

    # Pick for a 200KB PDF with medium budget
    pick_summarizer.py pdf --size-bytes 204800 --budget medium

    # Use a pre-fetched llm-info recommend_model response
    pick_summarizer.py image --llm-info-json /tmp/llm_recs.json
"""

import argparse
import json
import sys
from pathlib import Path


# Static fallback used when the registry is unreachable.
# Conservative picks that work offline via local Ollama.
STATIC_FALLBACK = {
    "image":       {"provider_id": "ollama", "model_id": "qwen2.5-vl:latest"},
    "audio":       {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "video":       {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "pdf":         {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "office":      {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "spreadsheet": {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "data":        {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "text":        {"provider_id": "ollama", "model_id": "qwen3:latest"},
    "url":         {"provider_id": "ollama", "model_id": "qwen3:latest"},
}

LARGE_DOC_BYTES = 50 * 1024  # >50KB → prefer analysis use_case

CACHE_PATH = Path("/tmp/totext-local-summarizer-cache.json")


def use_case_for(content_type: str, size_bytes: int) -> str:
    """Map content type + size to llm-info use_case."""
    if content_type == "image":
        return "vision"
    if content_type in ("pdf", "office", "text"):
        return "analysis" if size_bytes > LARGE_DOC_BYTES else "chat"
    if content_type in ("spreadsheet", "data"):
        return "analysis"
    return "chat"  # audio, video, url


def required_capabilities_for(content_type: str) -> list[str]:
    """Capabilities the picked model MUST support."""
    if content_type == "image":
        return ["vision"]
    return []


def pick_from_recommendations(recs: dict, required_caps: list[str]) -> dict | None:
    """
    Walk a recommend_model response and return the first model that meets the
    required capabilities. Returns None if no candidate qualifies.
    """
    items = recs.get("recommendations") or []
    for item in items:
        model = item.get("model") or {}
        caps = model.get("capabilities") or {}
        if all(caps.get(c) for c in required_caps):
            return {
                "provider_id": model.get("provider"),
                "model_id":    model.get("model"),
                "rationale":   item.get("rationale"),
                "source":      "llm-info",
            }
    return None


def load_cached(content_type: str, budget: str) -> dict | None:
    if not CACHE_PATH.exists():
        return None
    try:
        cache = json.loads(CACHE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return cache.get(f"{content_type}:{budget}")


def save_cached(content_type: str, budget: str, pick: dict) -> None:
    cache = {}
    if CACHE_PATH.exists():
        try:
            cache = json.loads(CACHE_PATH.read_text())
        except (OSError, json.JSONDecodeError):
            cache = {}
    cache[f"{content_type}:{budget}"] = pick
    try:
        CACHE_PATH.write_text(json.dumps(cache))
    except OSError:
        pass  # Cache is best-effort


def fallback(content_type: str) -> dict:
    pick = dict(STATIC_FALLBACK.get(content_type, STATIC_FALLBACK["text"]))
    pick["rationale"] = "static fallback (mcpcentral-llm-info unreachable)"
    pick["source"] = "fallback"
    return pick


def main() -> int:
    ap = argparse.ArgumentParser(description="Pick a summarization model.")
    ap.add_argument("content_type",
                    choices=list(STATIC_FALLBACK.keys()),
                    help="Output of detect_type.py 'type' field")
    ap.add_argument("--size-bytes", type=int, default=0,
                    help="Extracted-text size in bytes (drives long-context preference)")
    ap.add_argument("--budget", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--llm-info-json", default=None,
                    help="Path to a recommend_model response (or '-' for stdin). "
                         "If omitted or load fails, the static fallback is used.")
    ap.add_argument("--no-cache", action="store_true",
                    help="Skip the per-session cache.")
    args = ap.parse_args()

    if not args.no_cache:
        cached = load_cached(args.content_type, args.budget)
        if cached is not None:
            cached["source"] = cached.get("source", "cache") + "+cache"
            print(json.dumps(cached, indent=2))
            return 0

    required_caps = required_capabilities_for(args.content_type)
    pick: dict | None = None

    if args.llm_info_json:
        try:
            raw = sys.stdin.read() if args.llm_info_json == "-" \
                  else Path(args.llm_info_json).read_text()
            recs = json.loads(raw)
            pick = pick_from_recommendations(recs, required_caps)
        except (OSError, json.JSONDecodeError):
            pick = None

    if pick is None:
        pick = fallback(args.content_type)

    if not args.no_cache and pick.get("source") in ("llm-info", "fallback"):
        save_cached(args.content_type, args.budget, pick)

    print(json.dumps(pick, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
