---
name: totext-local
description: "Universal local content extraction and summarization. Extracts text from images (OCR), audio/video (transcription), PDFs, Office docs, JSON, Markdown, and URLs, then summarizes with a model selected at runtime via mcpcentral-llm-info. Use when asked to: (1) extract text from any file type, (2) transcribe audio/video, (3) OCR images or screenshots, (4) summarize documents or web content, (5) process batches of files, (6) convert content to text. Pairs with totext-graph for cloud knowledge-graph storage."
compatibility: "Requires local-vision MCP (or Ollama with qwen2.5-vl), mcp-ollama or another summarizer backend, Python 3.x, and EXA_API_KEY for URL extraction. Summarization model is selected at runtime via mcpcentral-llm-info; falls back to qwen3:latest if the registry is unreachable. Optional: FIRECRAWL_API_KEY for JS-heavy URL extraction."
metadata:
  author: mcpcentral.io
  version: "1.2.0"
---

# totext-local

Extract text from any input type and generate AI summaries. The summarization model is **selected at runtime** by `mcpcentral-llm-info` based on input type and size — no more hardcoded `qwen3:latest`.

For cloud knowledge-graph storage, semantic search, entity extraction, and citation traversal, use the sibling `totext-graph` plugin.

## Quick Start

1. **Detect input type** from extension or URL (`scripts/detect_type.py`)
2. **Extract text** using the appropriate method (see routing below)
3. **Pick a summarization model** via `scripts/pick_summarizer.py` (calls `mcp__mcpcentral-llm-info__recommend_model`)
4. **Summarize** by calling the picked model's MCP backend with a type-specific prompt
5. **Save output** as JSON to `/Users/cam/Downloads/to-text-skills-output/output/`

## Input Routing

| Input Type | Extensions | Extraction Method |
|------------|------------|-------------------|
| Image | png, jpg, jpeg, gif, bmp, tiff, webp | `local-vision` MCP → OCR |
| Audio | mp3, wav, ogg, flac, m4a | faster-whisper transcription |
| Video | mp4, webm, mkv, avi, mov | Extract audio → faster-whisper |
| PDF | pdf | MarkItDown → Claude analysis |
| Office | docx, xlsx, pptx | MarkItDown → Claude analysis |
| Spreadsheet | csv, tsv | Direct read + parsing |
| Data | json, jsonl | Parse and format |
| Text | md, txt, html | Direct read |
| URL | http://, https:// | Exa → Firecrawl → Jina Reader (tiered) |

## Model Routing (new in 1.2.0)

`scripts/pick_summarizer.py` maps `(content_type, size_bytes, budget_tier)` → a `{provider_id, model_id}` pick:

| Content type | `use_case` passed to llm-info | Notes |
|---|---|---|
| image | `vision` | requires `vision: true` capability |
| audio / video | `chat` | transcripts are plain text after STT |
| pdf / office / text | `analysis` for >50 KB, else `chat` | long-context preferred for big docs |
| spreadsheet / data | `analysis` | structured input |
| url | `chat` | usually article-sized |

Default `budget_tier` is `low`. Override on the CLI: `pick_summarizer.py image --budget medium`.

If the `mcpcentral-llm-info` server is unreachable, the script falls back to a static map (`image → qwen2.5-vl:latest`, everything else → `qwen3:latest`) so the skill keeps working offline.

## MCP Server Requirements

```bash
# Vision OCR (local)
claude mcp add -s project local-vision local-vision serve .

# Summarization backends (local)
uvx mcp-ollama

# URL extraction
/plugin marketplace add exa-labs/exa-mcp-server

# Model routing (cloud — bundled with this plugin via mcpcentral-llm-info)
```

See `references/mcp-setup.md` for full setup including optional Firecrawl, local-stt-mcp, MarkItDown, and Docling.

## Processing Workflow

### Step 1: Extract Text

**Images** → Call `local-vision` MCP for OCR. Preserve tables as markdown, maintain reading order.

**Audio/Video** → Use `faster-whisper` with model `large-v3` (path: `/Users/cam/.cache/whisper/large-v3.pt`). Include timestamps if available. For speaker diarization or word-level timestamps, use WhisperX. Alternatively, use `local-stt-mcp` if configured.

**Documents (PDF, Office)** → Run `markitdown` to extract structured Markdown first, then pass to Claude for analysis. Fall back to Claude native reading when MarkItDown fails (scanned PDFs, complex visual content, charts/diagrams).

**URLs** → Tiered extraction: (1) `crawling_exa` with the URL. (2) If JS-heavy or Exa fails, Firecrawl MCP `scrape`. (3) Final fallback: fetch `https://r.jina.ai/{url}` for clean Markdown via Jina Reader.

### Step 2: Pick the Summarization Model

```bash
scripts/pick_summarizer.py <content_type> [--size-bytes N] [--budget low|medium|high]
```

Returns JSON like `{"provider_id": "ollama-cloud", "model_id": "qwen3:latest", "rationale": "...", "source": "llm-info"}` or `{... "source": "fallback"}` if the registry was unreachable.

### Step 3: Select Prompt

Load from `prompts/` based on content type:

```
prompts/ocr.md          → Images
prompts/transcript.md   → Audio/Video
prompts/document.md     → PDF, Office, Markdown
prompts/spreadsheet.md  → Excel, CSV
prompts/data.md         → JSON, JSONL
prompts/url.md          → Web pages
```

### Step 4: Summarize via the Picked Model

For Ollama models, call `mcp-ollama` `generate`:
```json
{
  "model": "<model_id from pick_summarizer>",
  "prompt": "[loaded prompt]\n\nContent:\n[extracted text]",
  "temperature": 0
}
```

For non-Ollama picks (Anthropic / OpenAI / Gemini), call the appropriate provider MCP server or fall back to Claude.

### Step 5: Format Output

Return standardized JSON:
```json
{
  "text": "extracted raw text...",
  "summary": "AI-generated summary...",
  "metadata": {
    "source_type": "image|audio|pdf|...",
    "filename": "original.ext (or full URL for web sources)",
    "processed_date": "ISO timestamp",
    "summarizer": {"provider_id": "...", "model_id": "...", "source": "llm-info|fallback"}
  }
}
```

### Step 6: Save Output

Run `scripts/save_output.py` to save:
- Per-file JSON: `{timestamp}_{filename}.json`
- Batch report: `batch_{timestamp}.json`

Output directory: `/Users/cam/Downloads/to-text-skills-output/output/` (legacy path, retained for continuity with existing data).

## Error Handling

- **Per-item isolation**: Errors don't stop batch processing
- **Graceful fallbacks**: Try alternative methods before failing
- **Clear error objects**: Return `{"error": "message", "metadata": {...}}` for failures
- **Unsupported extensions**: If the file extension is not in the Input Routing table, immediately return the error object
- **Model routing failure**: If both `mcpcentral-llm-info` and the static fallback yield nothing usable, default to `qwen3:latest` and log `metadata.summarizer.source = "hardcoded"`

## Gotchas

- **Ollama must be running before processing.** `mcp-ollama` errors if `ollama serve` isn't active.
- **MarkItDown fails on scanned PDFs.** Detect near-empty `text_content` and fall back to Claude native reading.
- **faster-whisper requires `ffmpeg`.** Install via `brew install ffmpeg` or `apt install ffmpeg`.
- **Jina Reader URL format is `https://r.jina.ai/{full_url}`.** Must include the `https://` scheme.
- **Output directory is created automatically.** `scripts/save_output.py` uses `mkdir(parents=True, exist_ok=True)`.
- **Model picks are cached per session.** `pick_summarizer.py` writes a small JSON cache so a batch of 100 files makes one llm-info call, not 100.
- **Vision picks require `vision: true`.** Don't accept a recommendation that lacks vision capability for image inputs — fall back to the static map.

## References

- **MCP Setup**: `references/mcp-setup.md`
- **Supported Formats**: `references/formats.md`
- **Sibling plugin**: `totext-graph` (cloud knowledge graph; install for entity extraction, semantic search, citation traversal)
