---
name: to-text
description: "Universal content extraction and summarization skill. Extracts text from images (OCR), audio/video (Whisper), PDFs, Office docs, JSON, Markdown, and URLs—then summarizes via local Ollama. Use when asked to: (1) Extract text from any file type, (2) Transcribe audio/video, (3) OCR images or screenshots, (4) Summarize documents or web content, (5) Process batches of files, (6) Convert content to text format."
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
| Audio | mp3, wav, ogg, flac, m4a | Whisper transcription |
| Video | mp4, webm, mkv, avi, mov | Extract audio → Whisper |
| PDF | pdf | Claude native or pypdf |
| Office | docx, xlsx, pptx | Claude native or python-docx/openpyxl |
| Spreadsheet | csv, tsv | Direct read + parsing |
| Data | json, jsonl | Parse and format |
| Text | md, txt, html | Direct read |
| URL | http://, https:// | Exa MCP extraction |

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

**Audio/Video** → Use Whisper (model at `/Users/cam/.cache/whisper/large-v3.pt`). Include timestamps if available.

**Documents** → Use Claude's native reading capabilities or appropriate Python library.

**URLs** → Call `exa_get_contents` tool with the URL.

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
    "filename": "original.ext",
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

## References

- **MCP Setup**: See `references/mcp-setup.md` for detailed server configuration
- **Supported Formats**: See `references/formats.md` for complete format list
