#!/usr/bin/env python3
"""
Run Translations with Claude Code (No API Key Required)

This script runs translations using Claude Code by asking Claude to execute
the SKILL agent logic. It works without an API key.

Usage:
    python src/run_with_claude_code.py data/input/sanity_check.json
    python src/run_with_claude_code.py data/input/same_sentence_progressive.json
    python src/run_with_claude_code.py data/input/different_sentences_progressive.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_input_file(input_path: str) -> dict:
    """Load input JSON file."""
    path = Path(input_path)

    if not path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_claude_code_request(data: dict, input_filename: str) -> str:
    """
    Generate a request for Claude Code to execute translations.

    This creates a message that asks Claude to run all translations
    using the SKILL agent logic.
    """
    sentences = data.get('sentences', [])
    metadata = data.get('metadata', {})

    request = f"""
I need you to run real translations using the SKILL agent logic for this input file: {input_filename}

This file contains {len(sentences)} test case(s).

Here are the test cases:

"""

    for i, item in enumerate(sentences, 1):
        request += f"""
{'='*70}
Test Case {i}/{len(sentences)}
{'='*70}

ID: {item.get('id', f'test_{i}')}
Error Rate: {item.get('error_rate', 0.0) * 100:.0f}%
Word Count: {item.get('word_count', len(item.get('original', '').split()))}

Original:
{item.get('original', '')}

Misspelled (with errors):
{item.get('misspelled', '')}

"""

    request += f"""
{'='*70}
TASK
{'='*70}

Please translate ALL {len(sentences)} test cases using your SKILL agent logic:

For EACH test case:
1. Agent 1 (EN→FR): Translate the misspelled English to French
   - Use context to infer correct words from misspellings
   - Produce natural, grammatically correct French

2. Agent 2 (FR→HE): Translate the French to Hebrew
   - Semantic translation (not word-by-word)
   - Proper Hebrew grammar and syntax

3. Agent 3 (HE→EN): Translate the Hebrew back to English
   - This is the final output to compare with original

After completing all translations, provide the results in this JSON format:

```json
{{
  "experiment_id": "claude_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
  "timestamp": "{datetime.now().isoformat()}",
  "mode": "claude_code_execution",
  "input_file": "{input_filename}",
  "results": [
    {{
      "id": "test_case_id",
      "original": "original text",
      "misspelled": "text with errors",
      "error_rate": 0.15,
      "french": "French translation from Agent 1",
      "hebrew": "Hebrew translation from Agent 2",
      "final": "Final English from Agent 3",
      "word_count": 19
    }}
    // ... repeat for all test cases
  ]
}}
```

Please execute all {len(sentences)} translations now and provide the complete JSON result.
"""

    return request


def save_request_file(request: str, input_filename: str):
    """Save the request to a file for reference with new directory structure."""
    date_str = datetime.now().strftime('%Y-%m-%d')
    input_name = Path(input_filename).stem  # e.g., "sanity_check", "same_sentence_progressive"

    output_dir = Path("results") / date_str / input_name
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    request_file = output_dir / f"request_{timestamp}.txt"

    with open(request_file, 'w', encoding='utf-8') as f:
        f.write(request)

    return request_file


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python src/run_with_claude_code.py <input_file.json>")
        print("\nExamples:")
        print("  python src/run_with_claude_code.py data/input/sanity_check.json")
        print("  python src/run_with_claude_code.py data/input/same_sentence_progressive.json")
        print("  python src/run_with_claude_code.py data/input/different_sentences_progressive.json")
        sys.exit(1)

    input_file = sys.argv[1]

    print("\n" + "="*70)
    print("Claude Code Translation Runner")
    print("="*70)
    print(f"\nInput: {input_file}")

    # Load input
    data = load_input_file(input_file)
    sentences = data.get('sentences', [])

    print(f"Loaded: {len(sentences)} test case(s)")

    # Generate request for Claude Code
    request = generate_claude_code_request(data, Path(input_file).name)

    # Save request to file
    request_file = save_request_file(request, input_file)
    print(f"\n✓ Request saved to: {request_file}")

    # Display the request
    print("\n" + "="*70)
    print("REQUEST FOR CLAUDE CODE")
    print("="*70)
    print("\nCopy the request below and send it to Claude Code:\n")
    print("-"*70)
    print(request)
    print("-"*70)

    # Show the expected output location
    date_str = datetime.now().strftime('%Y-%m-%d')
    input_name = Path(input_file).stem
    expected_results_dir = f"results/{date_str}/{input_name}"

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"""
1. Copy the request above
2. Paste it in your Claude Code conversation
3. Claude will execute all translations and provide JSON results
4. Results will be saved to:
   {expected_results_dir}/results_TIMESTAMP.json
5. Analyze the results:
   python src/main.py analyze {expected_results_dir}/results_TIMESTAMP.json

Alternatively, Claude can save the results directly for you.
""")


if __name__ == '__main__':
    main()
