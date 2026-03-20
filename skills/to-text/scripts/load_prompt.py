#!/usr/bin/env python3
"""
Load and populate prompt template for To-Text summarization.

Usage:
    load_prompt.py <prompt_name> --content <text>
    load_prompt.py ocr --content "Extracted text here..."
    
Returns the full prompt ready for Ollama.
"""

import sys
from pathlib import Path


# Skill root (relative to this script)
SKILL_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = SKILL_ROOT / 'prompts'


def load_prompt(prompt_name: str, content: str) -> str:
    """
    Load prompt template and populate with content.
    
    Args:
        prompt_name: Name of prompt file (with or without .md)
        content: Text content to inject
        
    Returns:
        Complete prompt string
    """
    # Normalize prompt name
    if not prompt_name.endswith('.md'):
        prompt_name = f"{prompt_name}.md"
    
    prompt_path = PROMPTS_DIR / prompt_name
    
    if not prompt_path.exists():
        # Fallback to document prompt
        prompt_path = PROMPTS_DIR / 'document.md'
    
    template = prompt_path.read_text(encoding='utf-8')
    
    # Replace placeholder
    return template.replace('{content}', content)


def get_prompt_for_type(content_type: str, content: str) -> str:
    """
    Get populated prompt based on content type.
    
    Args:
        content_type: Type from detect_type.py (image, audio, pdf, etc.)
        content: Extracted text content
        
    Returns:
        Complete prompt string
    """
    type_to_prompt = {
        'image': 'ocr',
        'audio': 'transcript',
        'video': 'transcript',
        'pdf': 'document',
        'office': 'document',
        'spreadsheet': 'spreadsheet',
        'data': 'data',
        'text': 'document',
        'url': 'url',
    }
    
    prompt_name = type_to_prompt.get(content_type, 'document')
    return load_prompt(prompt_name, content)


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--content':
        print("Usage: load_prompt.py <prompt_name> --content <text>")
        print("\nAvailable prompts:")
        if PROMPTS_DIR.exists():
            for p in PROMPTS_DIR.glob('*.md'):
                print(f"  - {p.stem}")
        sys.exit(1)
    
    prompt_name = sys.argv[1]
    content = sys.argv[3]
    
    result = load_prompt(prompt_name, content)
    print(result)


if __name__ == "__main__":
    main()
