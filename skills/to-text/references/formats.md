# Supported Formats

## Images (OCR via local-vision)

| Extension | MIME Type | Notes |
|-----------|-----------|-------|
| .png | image/png | Best for screenshots |
| .jpg, .jpeg | image/jpeg | Good for photos |
| .gif | image/gif | First frame only |
| .bmp | image/bmp | Uncompressed |
| .tiff, .tif | image/tiff | High quality scans |
| .webp | image/webp | Modern format |

## Audio (Whisper transcription)

| Extension | MIME Type | Notes |
|-----------|-----------|-------|
| .mp3 | audio/mpeg | Most common |
| .wav | audio/wav | Uncompressed |
| .ogg | audio/ogg | Open format |
| .flac | audio/flac | Lossless |
| .m4a | audio/mp4 | Apple format |
| .aac | audio/aac | Compressed |
| .wma | audio/x-ms-wma | Windows Media |

## Video (Extract audio → Whisper)

| Extension | MIME Type | Notes |
|-----------|-----------|-------|
| .mp4 | video/mp4 | Most common |
| .webm | video/webm | Web format |
| .mkv | video/x-matroska | Container |
| .avi | video/x-msvideo | Legacy |
| .mov | video/quicktime | Apple format |
| .wmv | video/x-ms-wmv | Windows Media |

## Documents

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .pdf | application/pdf | MarkItDown → Claude analysis (fallback: Claude native) |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | MarkItDown → Claude analysis |
| .doc | application/msword | MarkItDown → Claude analysis (legacy Word) |
| .pptx | application/vnd.openxmlformats-officedocument.presentationml.presentation | MarkItDown → Claude analysis |
| .ppt | application/vnd.ms-powerpoint | MarkItDown → Claude analysis (legacy PowerPoint) |

## Spreadsheets

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | MarkItDown → Claude analysis |
| .xls | application/vnd.ms-excel | MarkItDown → Claude analysis (legacy Excel) |
| .csv | text/csv | Direct read / pandas |
| .tsv | text/tab-separated-values | Direct read / pandas |

## Structured Data

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .json | application/json | json.load |
| .jsonl | application/x-jsonlines | Line-by-line |

## Text/Markup

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .md | text/markdown | Direct read |
| .txt | text/plain | Direct read |
| .html, .htm | text/html | Direct read |
| .xml | application/xml | Direct read |
| .yaml, .yml | application/yaml | Direct read |

## URLs

Any valid `http://` or `https://` URL is processed via a tiered fallback chain:

1. **Exa MCP** (`exa_get_contents`) — primary; fast, good metadata
2. **Firecrawl MCP** (`scrape`) — for JS-heavy SPAs or when Exa fails
3. **Jina Reader** (`https://r.jina.ai/{url}`) — free fallback via HTTP fetch, returns clean Markdown

**Limitations:**
- Paywalled content may be blocked at all tiers
- Social media pages have limited support
- Rate limits apply per Exa/Firecrawl plan
