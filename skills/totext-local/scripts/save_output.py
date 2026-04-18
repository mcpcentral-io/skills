#!/usr/bin/env python3
"""
Save To-Text output to filesystem.

Usage:
    save_output.py --result <json_string> [--output-dir <dir>]
    
Or use as module:
    from save_output import save_result
    save_result(result_dict, output_dir="/path/to/output")
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_OUTPUT_DIR = "/Users/cam/Downloads/to-text-skills-output/output"


def sanitize_filename(name: str) -> str:
    """Convert string to safe filename."""
    # Remove/replace unsafe characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe = re.sub(r'\s+', '_', safe)
    safe = re.sub(r'_+', '_', safe)
    safe = safe.strip('_.')
    return safe[:100] if safe else 'unnamed'


def generate_timestamp() -> str:
    """Generate ISO-format timestamp for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_result(
    result: dict,
    output_dir: Optional[str] = None,
    filename_prefix: Optional[str] = None
) -> dict:
    """
    Save processing result to JSON file.
    
    Args:
        result: Dict with text, summary, metadata keys
        output_dir: Directory for output (default: DEFAULT_OUTPUT_DIR)
        filename_prefix: Optional prefix for filename
        
    Returns:
        Dict with saved file path and status
    """
    output_path = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Determine filename
    timestamp = generate_timestamp()
    
    if filename_prefix:
        base_name = sanitize_filename(filename_prefix)
    elif result.get('metadata', {}).get('filename'):
        base_name = sanitize_filename(
            Path(result['metadata']['filename']).stem
        )
    else:
        base_name = 'output'
    
    filename = f"{timestamp}_{base_name}.json"
    filepath = output_path / filename
    
    # Add save metadata
    result_with_meta = {
        **result,
        'saved_at': datetime.now().isoformat(),
        'saved_to': str(filepath)
    }
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result_with_meta, f, indent=2, ensure_ascii=False)
    
    return {
        'status': 'success',
        'filepath': str(filepath),
        'filename': filename
    }


def save_batch_report(
    results: list,
    errors: Optional[list] = None,
    output_dir: Optional[str] = None
) -> dict:
    """
    Save batch processing report.
    
    Args:
        results: List of individual results
        errors: Optional list of error messages
        output_dir: Directory for output
        
    Returns:
        Dict with saved report path and summary
    """
    output_path = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = generate_timestamp()
    filename = f"batch_{timestamp}.json"
    filepath = output_path / filename
    
    report = {
        'batch_id': f"batch_{timestamp}",
        'processed_date': datetime.now().isoformat(),
        'total_items': len(results),
        'successful': sum(1 for r in results if 'error' not in r),
        'failed': sum(1 for r in results if 'error' in r),
        'items': results,
        'errors': errors or []
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return {
        'status': 'success',
        'filepath': str(filepath),
        'summary': {
            'total': report['total_items'],
            'successful': report['successful'],
            'failed': report['failed']
        }
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: save_output.py --result '<json_string>' [--output-dir <dir>]")
        sys.exit(1)
    
    # Parse arguments
    result_json = None
    output_dir = DEFAULT_OUTPUT_DIR
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--result' and i + 1 < len(args):
            result_json = args[i + 1]
            i += 2
        elif args[i] == '--output-dir' and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            i += 1
    
    if not result_json:
        print("Error: --result argument required")
        sys.exit(1)
    
    try:
        result = json.loads(result_json)
        saved = save_result(result, output_dir)
        print(f"✅ Saved to: {saved['filepath']}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
