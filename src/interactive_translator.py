#!/usr/bin/env python3
"""
Interactive Translation with Claude Code

This script generates prompts for you to run in Claude Code interactively.
No API key required - you just copy/paste the prompts to Claude.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_sentences():
    """Load sentences from JSON file."""
    sentences_file = Path("data/input/sentences.json")

    if not sentences_file.exists():
        print(f"❌ Error: {sentences_file} not found")
        sys.exit(1)

    with open(sentences_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('sentences', [])


def generate_interactive_session():
    """Generate an interactive translation session guide."""

    print("\n" + "="*70)
    print("INTERACTIVE TRANSLATION SESSION - NO API KEY REQUIRED")
    print("="*70)

    sentences = load_sentences()

    print(f"\n📂 Loaded {len(sentences)} test cases")
    print("\n" + "="*70)
    print("INSTRUCTIONS")
    print("="*70)
    print("""
This script will guide you through running translations interactively.

For each test case:
1. I'll show you the prompt for Agent 1 (EN→FR)
2. You copy it and ask Claude Code (in this same conversation!)
3. Claude responds with French translation
4. I'll show you the prompt for Agent 2 (FR→HE) with placeholder
5. You copy it, replace [FRENCH] with Claude's response, and ask again
6. Repeat for Agent 3 (HE→EN)

At the end, I'll generate a results.json file for you to save.

Ready? Press Enter to start...""")

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping prompt...")

    all_results = []

    for i, item in enumerate(sentences, 1):
        print(f"\n{'#'*70}")
        print(f"# TEST CASE {i}/{len(sentences)}")
        print(f"# Error Rate: {int(item['error_rate']*100)}%")
        print(f"{'#'*70}\n")

        original = item['original']
        misspelled = item['misspelled']
        error_rate = item['error_rate']

        print(f"Original:   {original}")
        print(f"Misspelled: {misspelled}")
        print()

        # Agent 1: EN → FR
        print("="*70)
        print("STEP 1: ENGLISH → FRENCH")
        print("="*70)
        print("\nCopy this prompt and send it to Claude Code:\n")
        print("-"*70)
        print(f"""Translate this English text to French:

"{misspelled}"

Please provide ONLY the French translation, nothing else.""")
        print("-"*70)

        print("\nWaiting for you to get the French translation from Claude...")
        print("Then paste it here and press Enter:")

        try:
            french = input("French translation: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Skipping interactive input - using placeholder")
            french = "[PASTE_FRENCH_HERE]"

        # Agent 2: FR → HE
        print("\n" + "="*70)
        print("STEP 2: FRENCH → HEBREW")
        print("="*70)
        print("\nCopy this prompt and send it to Claude Code:\n")
        print("-"*70)
        print(f"""Translate this French text to Hebrew:

"{french}"

Please provide ONLY the Hebrew translation, nothing else.""")
        print("-"*70)

        print("\nWaiting for you to get the Hebrew translation from Claude...")
        print("Then paste it here and press Enter:")

        try:
            hebrew = input("Hebrew translation: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Skipping interactive input - using placeholder")
            hebrew = "[PASTE_HEBREW_HERE]"

        # Agent 3: HE → EN
        print("\n" + "="*70)
        print("STEP 3: HEBREW → ENGLISH")
        print("="*70)
        print("\nCopy this prompt and send it to Claude Code:\n")
        print("-"*70)
        print(f"""Translate this Hebrew text to English:

"{hebrew}"

Please provide ONLY the English translation, nothing else.""")
        print("-"*70)

        print("\nWaiting for you to get the final English translation from Claude...")
        print("Then paste it here and press Enter:")

        try:
            final = input("Final English: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Skipping interactive input - using placeholder")
            final = "[PASTE_FINAL_ENGLISH_HERE]"

        # Store result
        result = {
            'original': original,
            'misspelled': misspelled,
            'error_rate': error_rate,
            'french': french,
            'hebrew': hebrew,
            'final': final,
            'word_count': len(original.split())
        }

        all_results.append(result)

        print("\n✅ Test case complete!")

        if i < len(sentences):
            print("\nPress Enter to continue to next test case...")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\nContinuing...")

    # Generate results file
    print("\n" + "="*70)
    print("GENERATING RESULTS FILE")
    print("="*70)

    output_dir = Path("results/interactive_run")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    output_data = {
        "experiment_id": f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "mode": "interactive_claude_code",
        "results": all_results
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved to: {results_file}")
    print(f"\nYou can now analyze these results with:")
    print(f"python src/main.py analyze {results_file}")
    print()


if __name__ == '__main__':
    generate_interactive_session()
