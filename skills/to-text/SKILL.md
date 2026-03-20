---
name: to-text
description: "Universal content extraction and summarization skill. Extracts text from images (OCR), audio/video (transcription), PDFs, Office docs, JSON, Markdown, and URLs—then summarizes via local Ollama. Use when asked to: (1) Extract text from any file type, (2) Transcribe audio/video, (3) OCR images or screenshots, (4) Summarize documents or web content, (5) Process batches of files, (6) Convert content to text format."
compatibility: Requires Ollama running locally (qwen3:latest), local-vision MCP server, Python 3.x, and EXA_API_KEY. Optional: FIRECRAWL_API_KEY for JS-heavy URL extraction.
metadata:
  author: mcpcentral.io
  version: "1.1.0"
---

# To-Text

Extract text from any input type and generate AI summaries using local LLMs.

## Quick Start

1. **Detect input type** from extension or URL
2. **Extract text** using appropriate method (see routing below)
3. **Summarize** by calling Ollama MCP with type-specific prompt
4. **Save output** as JSON to `/Users/cam/Downloads/to-text-skills-output/output/`

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

## MCP Server Requirements

```bash
# Vision OCR
claude mcp add -s project local-vision local-vision serve .

# Summarization  
uvx mcp-ollama

# URL extraction
/plugin marketplace add exa-labs/exa-mcp-server
```

## Processing Workflow

### Step 1: Extract Text

**Images** → Call `local-vision` MCP tool for OCR. Preserve tables as markdown, maintain reading order.

**Audio/Video** → Use `faster-whisper` with model `large-v3` (path: `/Users/cam/.cache/whisper/large-v3.pt`). Include timestamps if available. For speaker diarization or word-level timestamps, use WhisperX instead. Alternatively, use `local-stt-mcp` if configured (removes Python scripting requirement).

**Documents (PDF, Office)** → Run `markitdown` to extract structured Markdown first, then pass to Claude for analysis. Fall back to Claude native reading when MarkItDown fails (scanned PDFs, complex visual content, charts/diagrams).

**URLs** → Tiered extraction: (1) Call `crawling_exa` with the URL. (2) If JS-heavy or Exa fails, use Firecrawl MCP `scrape`. (3) Final fallback: fetch `https://r.jina.ai/{url}` for clean Markdown via Jina Reader.

### Step 2: Select Prompt

Load from `prompts/` based on content type:

```
prompts/ocr.md          → Images
prompts/transcript.md   → Audio/Video  
prompts/document.md     → PDF, Office, Markdown
prompts/spreadsheet.md  → Excel, CSV
prompts/data.md         → JSON, JSONL
prompts/url.md          → Web pages
```

### Step 3: Summarize via Ollama

Call `mcp-ollama` generate tool:
```json
{
  "model": "qwen3:latest",
  "prompt": "[loaded prompt]\n\nContent:\n[extracted text]",
  "temperature": 0
}
```

Fallback: If Ollama unavailable, summarize with Claude.

### Step 4: Format Output

Return standardized JSON:
```json
{
  "text": "extracted raw text...",
  "summary": "AI-generated summary...",
  "metadata": {
    "source_type": "image|audio|pdf|...",
    "filename": "original.ext (or full URL for web sources)",
    "processed_date": "ISO timestamp"
  }
}
```

### Step 5: Save Output

Run `scripts/save_output.py` to save:
- Per-file JSON: `{timestamp}_{filename}.json`
- Batch report: `batch_{timestamp}.json`

Output directory: `/Users/cam/Downloads/to-text-skills-output/output/`

## Error Handling

- **Per-item isolation**: Errors don't stop batch processing
- **Graceful fallbacks**: Try alternative methods before failing
- **Clear error objects**: Return `{"error": "message", "metadata": {...}}` for failures
- **Unsupported extensions**: If the file extension is not in the Input Routing table, immediately return the error object — do not attempt extraction

## Gotchas

- **Ollama must be running before processing.** `mcp-ollama` will error if `ollama serve` isn't active. Start it first, or fall back to Claude summarization.
- **MarkItDown fails on scanned PDFs.** Scanned documents produce empty or garbled markdown. Detect this (near-empty `text_content`) and fall back to Claude native reading.
- **faster-whisper requires `ffmpeg`.** Without `ffmpeg` installed, audio/video transcription fails at format conversion. Install via `brew install ffmpeg` or `apt install ffmpeg`.
- **Jina Reader URL format is `https://r.jina.ai/{full_url}`.** The `{full_url}` must include the `https://` scheme — e.g., `https://r.jina.ai/https://example.com/article`.
- **Output directory is created automatically.** `scripts/save_output.py` uses `mkdir(parents=True, exist_ok=True)` — no need to pre-create the output path.
- **Unsupported extensions must error immediately.** Return `{"error": "...", "metadata": {...}}` for unknown extensions without attempting extraction.

## References

- **MCP Setup**: See `references/mcp-setup.md` for detailed server configuration
- **Supported Formats**: See `references/formats.md` for complete format list
