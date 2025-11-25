#!/usr/bin/env python3
"""
Simple Gemini Translation Chain Runner

Uses Google Gemini API to run EN→FR→HE→EN translation chain.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()


def run_translation_chain(input_file: str):
    """Run translation chain with Gemini API."""

    # Setup Gemini
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Load input
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sentences = data.get('sentences', [])
    print(f"\n✅ Loaded {len(sentences)} test cases\n")

    # Load agent instructions
    agents_dir = Path("agents")

    with open(agents_dir / "agent-en-to-fr" / "SKILL.md", 'r') as f:
        en_fr_prompt = f.read()
    with open(agents_dir / "agent-fr-to-he" / "SKILL.md", 'r') as f:
        fr_he_prompt = f.read()
    with open(agents_dir / "agent-he-to-en" / "SKILL.md", 'r') as f:
        he_en_prompt = f.read()

    results = []

    for i, item in enumerate(sentences, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}/{len(sentences)} - {int(item['error_rate']*100)}% errors")
        print(f"{'='*70}")
        print(f"Input: {item['misspelled']}")

        # EN → FR
        response = model.generate_content(f"{en_fr_prompt}\n\nTranslate to French: {item['misspelled']}")
        french = response.text.strip()
        print(f"\n→ French: {french}")

        # FR → HE
        response = model.generate_content(f"{fr_he_prompt}\n\nTranslate to Hebrew: {french}")
        hebrew = response.text.strip()
        print(f"→ Hebrew: {hebrew}")

        # HE → EN
        response = model.generate_content(f"{he_en_prompt}\n\nTranslate to English: {hebrew}")
        final = response.text.strip()
        print(f"→ Final: {final}\n")

        results.append({
            'original': item['original'],
            'misspelled': item['misspelled'],
            'error_rate': item['error_rate'],
            'french': french,
            'hebrew': hebrew,
            'final': final,
            'word_count': len(item['original'].split())
        })

    # Save results
    date_str = datetime.now().strftime('%Y-%m-%d')
    input_name = Path(input_file).stem
    output_dir = Path("results") / date_str / input_name
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "experiment_id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "model": "gemini-2.5-flash",
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved: {results_file}")
    print(f"\n📊 Run analysis:\n   python src/main.py analyze {results_file}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_gemini.py <input_file.json>")
        sys.exit(1)

    run_translation_chain(sys.argv[1])
