# MCP Server Setup

## Required Servers

### 1. local-vision (Image OCR)

```bash
# Add as project-scoped MCP server
claude mcp add -s project local-vision local-vision serve .
```

**Tool Interface:**
- Tool: `local-vision` (or check with `claude mcp tools`)
- Input: Image file path or base64 data
- Output: Extracted text with confidence scores

**Fallback:** `qwen2.5-vl` via Ollama (capable vision-language model)
```bash
ollama pull qwen2.5-vl:latest
```

**Cloud alternative:** Mistral OCR MCP offers high-accuracy cloud OCR when local options are insufficient.

### 2. mcp-ollama (Summarization)

```bash
# Run via uvx
uvx mcp-ollama

# Or install globally
pip install mcp-ollama
```

**Ensure Ollama is running:**
```bash
ollama serve
ollama pull qwen3:latest  # Recommended model
```

**Tool Interface:**
- Tool: `generate` or `chat`
- Parameters:
  - `model`: "qwen3:latest" (or preferred)
  - `prompt`: Full prompt with content
  - `temperature`: 0 (for consistency)

### 3. exa-mcp-server (URL Extraction)

```bash
# Via Claude CLI
/plugin marketplace add exa-labs/exa-mcp-server
/plugin install exa-mcp-server
```

**Tool Interface:**
- Tool: `exa_get_contents`
- Input: `{ "ids": ["url"], "text": true }`
- Output: Extracted page content

**API Key:**
```bash
export EXA_API_KEY="your-key-here"
```

### 4. Firecrawl MCP (URL Extraction — JS-heavy sites)

```bash
/plugin marketplace add mendableai/firecrawl-mcp-server
```

**Tool Interface:**
- Tool: `scrape`
- Input: `{ "url": "https://..." }`
- Output: Rendered page content as Markdown

**API Key:**
```bash
export FIRECRAWL_API_KEY="your-key-here"
```

Used as fallback when Exa fails or site requires JavaScript rendering.

## Optional Servers

### local-stt-mcp (Audio Transcription)

MCP server using whisper.cpp, optimized for Apple Silicon. Removes the need for direct Python scripting.

```bash
# Install SmartLittleApps/local-stt-mcp
claude mcp add -s project local-stt-mcp local-stt-mcp serve .
```

Supports diarization and runs faster-whisper/whisper.cpp under the hood.

### MarkItDown (Document Extraction)

Converts PDF, DOCX, PPTX, XLSX, HTML, CSV → clean Markdown for LLM ingestion.

```bash
pip install markitdown
```

**Usage:**
```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

**Premium alternative:** Docling (IBM) for complex layouts, merged table cells, multi-column documents, and formulas:
```bash
pip install docling
```

## Audio Transcription (Python fallback)

If `local-stt-mcp` is not available, use `faster-whisper` directly (4-6x faster than original `whisper` library, identical accuracy, same model weights):

```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="auto")
segments, info = model.transcribe(audio_path)
text = " ".join(seg.text for seg in segments)
```

For speaker diarization or word-level timestamps, use WhisperX:
```python
import whisperx
model = whisperx.load_model("large-v3", device="cpu")
result = model.transcribe(audio_path)
```

Model location: `/Users/cam/.cache/whisper/large-v3.pt`

## Verifying Setup

```bash
# List available MCP tools
claude mcp tools

# Check Ollama models
ollama list

# Test Ollama
curl http://localhost:11434/api/generate -d '{"model":"qwen3:latest","prompt":"test"}'
```

## Model Recommendations

| Task | Model | Notes |
|------|-------|-------|
| General summary | qwen3:latest | Good balance |
| Long documents | qwen3:32b | Better context |
| Lightweight/fast | llama3.3:8b | Good for 8GB RAM |
| Technical | codellama:latest | Code-aware |
| Fast | phi3:mini | Fastest option |

**Note:** Qwen3.5 does not yet have Ollama GGUF support (llama.cpp only) — use `qwen3:latest` for now.
