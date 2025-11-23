#!/usr/bin/env python3
"""
Save Claude Code Results Helper

This script helps save results from Claude Code executions to the proper
directory structure: results/YYYY-MM-DD/input_name/

Usage:
    python src/save_claude_results.py <input_file> <results_json>

Example:
    python src/save_claude_results.py data/input/same_sentence_progressive.json results.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def save_claude_results(input_file: str, results_data: dict) -> Path:
    """
    Save Claude Code results to proper directory structure.

    Args:
        input_file: Path to input JSON file (e.g., data/input/sanity_check.json)
        results_data: Dictionary with translation results

    Returns:
        Path to saved results file
    """
    # Extract input name
    input_path = Path(input_file)
    input_name = input_path.stem  # e.g., "sanity_check"

    # Create directory structure: results/YYYY-MM-DD/input_name/
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = Path("results") / date_str / input_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save results file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f"results_{timestamp}.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    return results_file


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python src/save_claude_results.py <input_file> <results_json>")
        print("\nExample:")
        print("  python src/save_claude_results.py data/input/sanity_check.json results.json")
        sys.exit(1)

    input_file = sys.argv[1]
    results_file = sys.argv[2]

    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results_data = json.load(f)

    # Save to proper location
    saved_path = save_claude_results(input_file, results_data)

    print(f"\n✅ Results saved to: {saved_path}")
    print(f"\nYou can now analyze with:")
    print(f"python src/main.py analyze {saved_path}")
    print()


if __name__ == '__main__':
    main()
