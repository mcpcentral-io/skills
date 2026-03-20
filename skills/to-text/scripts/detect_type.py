#!/usr/bin/env python3
"""
Detect input type for To-Text processing.

Usage:
    detect_type.py <filepath_or_url>
    
Returns JSON with detected type and recommended processor.
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse


# Extension to type mapping
EXTENSION_MAP = {
    # Images
    '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
    '.gif': 'image', '.bmp': 'image', '.tiff': 'image',
    '.tif': 'image', '.webp': 'image',
    
    # Audio
    '.mp3': 'audio', '.wav': 'audio', '.ogg': 'audio',
    '.flac': 'audio', '.m4a': 'audio', '.aac': 'audio',
    '.wma': 'audio',
    
    # Video
    '.mp4': 'video', '.webm': 'video', '.mkv': 'video',
    '.avi': 'video', '.mov': 'video', '.wmv': 'video',
    
    # Documents
    '.pdf': 'pdf',
    '.docx': 'office', '.doc': 'office',
    '.pptx': 'office', '.ppt': 'office',
    
    # Spreadsheets
    '.xlsx': 'spreadsheet', '.xls': 'spreadsheet',
    '.csv': 'spreadsheet', '.tsv': 'spreadsheet',
    
    # Data
    '.json': 'data', '.jsonl': 'data',
    
    # Text
    '.md': 'text', '.txt': 'text', '.html': 'text',
    '.htm': 'text', '.xml': 'text', '.yaml': 'text',
    '.yml': 'text',
}

# Type to prompt mapping
PROMPT_MAP = {
    'image': 'ocr.md',
    'audio': 'transcript.md',
    'video': 'transcript.md',
    'pdf': 'document.md',
    'office': 'document.md',
    'spreadsheet': 'spreadsheet.md',
    'data': 'data.md',
    'text': 'document.md',
    'url': 'url.md',
}

# Type to processor mapping
PROCESSOR_MAP = {
    'image': 'local-vision MCP',
    'audio': 'whisper',
    'video': 'whisper (extract audio first)',
    'pdf': 'claude native or pypdf',
    'office': 'claude native or python-docx/openpyxl',
    'spreadsheet': 'direct read + pandas',
    'data': 'json.load',
    'text': 'direct read',
    'url': 'exa MCP',
}


def detect_type(input_path: str) -> dict:
    """
    Detect the type of input.
    
    Args:
        input_path: File path or URL
        
    Returns:
        Dict with type, prompt, processor, and metadata
    """
    # Check if URL
    parsed = urlparse(input_path)
    if parsed.scheme in ('http', 'https'):
        return {
            'input': input_path,
            'type': 'url',
            'prompt': PROMPT_MAP['url'],
            'processor': PROCESSOR_MAP['url'],
            'is_url': True,
            'domain': parsed.netloc
        }
    
    # File path
    path = Path(input_path)
    ext = path.suffix.lower()
    
    file_type = EXTENSION_MAP.get(ext, 'unknown')
    
    result = {
        'input': input_path,
        'filename': path.name,
        'extension': ext,
        'type': file_type,
        'prompt': PROMPT_MAP.get(file_type, 'document.md'),
        'processor': PROCESSOR_MAP.get(file_type, 'unknown'),
        'is_url': False,
        'exists': path.exists()
    }
    
    if path.exists():
        result['size_bytes'] = path.stat().st_size
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: detect_type.py <filepath_or_url>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    result = detect_type(input_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
