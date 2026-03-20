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
| .pdf | application/pdf | Claude native / pypdf |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Claude native / python-docx |
| .doc | application/msword | Legacy Word |
| .pptx | application/vnd.openxmlformats-officedocument.presentationml.presentation | Claude native / python-pptx |
| .ppt | application/vnd.ms-powerpoint | Legacy PowerPoint |

## Spreadsheets

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | Claude native / openpyxl |
| .xls | application/vnd.ms-excel | Legacy Excel |
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

Any valid `http://` or `https://` URL is processed via Exa MCP.

**Limitations:**
- Paywalled content may be blocked
- JavaScript-rendered content may be incomplete
- Rate limits apply per Exa plan
