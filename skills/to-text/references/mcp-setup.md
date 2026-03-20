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

**Fallback:** DeepSeek-OCR via Ollama
```bash
ollama pull deepseek-vl2:latest
```

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

## Optional: Whisper MCP

If available, use Whisper MCP for transcription. Otherwise, use Python directly:

```python
import whisper
model = whisper.load_model("large-v3")
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
| Technical | codellama:latest | Code-aware |
| Fast | phi3:mini | Fastest option |
