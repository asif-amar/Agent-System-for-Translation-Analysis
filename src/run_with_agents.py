#!/usr/bin/env python3
"""
Run Translation Chain with Real SKILL-Based Agents

This script uses the actual SKILL-based agents with Claude API to perform
real translations (not word-by-word mapping like demo mode).

It invokes the agents programmatically using the Anthropic API.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic


class AgentTranslator:
    """
    Runs translation chain using real SKILL-based agents with Claude API.
    """

    def __init__(self, api_key: str = None):
        """Initialize translator with API key."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Set it in .env file or pass as argument."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Claude model

        # Load agent instructions
        self.agents_dir = Path(__file__).parent.parent / "agents"
        self.agent_instructions = self._load_agent_instructions()

    def _load_agent_instructions(self) -> dict:
        """Load instructions from SKILL.md files."""
        instructions = {}

        # Agent 1: EN→FR
        en_fr_path = self.agents_dir / "agent-en-to-fr" / "SKILL.md"
        if en_fr_path.exists():
            with open(en_fr_path, 'r', encoding='utf-8') as f:
                instructions['en_to_fr'] = f.read()

        # Agent 2: FR→HE
        fr_he_path = self.agents_dir / "agent-fr-to-he" / "SKILL.md"
        if fr_he_path.exists():
            with open(fr_he_path, 'r', encoding='utf-8') as f:
                instructions['fr_to_he'] = f.read()

        # Agent 3: HE→EN
        he_en_path = self.agents_dir / "agent-he-to-en" / "SKILL.md"
        if he_en_path.exists():
            with open(he_en_path, 'r', encoding='utf-8') as f:
                instructions['he_to_en'] = f.read()

        return instructions

    def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """
        Call Claude API with system prompt and user message.

        Args:
            system_prompt: Agent instructions from SKILL.md
            user_message: Text to translate

        Returns:
            Translation result
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract text from response
            return response.content[0].text.strip()

        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            raise

    def translate_en_to_fr(self, english_text: str) -> str:
        """
        Agent 1: Translate English to French using Claude.

        Args:
            english_text: English input (may contain errors)

        Returns:
            French translation
        """
        print(f"\n🔄 Agent 1: English → French")
        print(f"   Input:  {english_text}")

        # Use agent instructions from SKILL.md
        system_prompt = self.agent_instructions.get('en_to_fr', '')

        user_message = f"Translate this English text to French:\n\n{english_text}\n\nProvide ONLY the French translation, nothing else."

        french = self._call_claude(system_prompt, user_message)

        print(f"   Output: {french}")
        return french

    def translate_fr_to_he(self, french_text: str) -> str:
        """
        Agent 2: Translate French to Hebrew using Claude.

        Args:
            french_text: French input

        Returns:
            Hebrew translation
        """
        print(f"\n🔄 Agent 2: French → Hebrew")
        print(f"   Input:  {french_text}")

        system_prompt = self.agent_instructions.get('fr_to_he', '')

        user_message = f"Translate this French text to Hebrew:\n\n{french_text}\n\nProvide ONLY the Hebrew translation, nothing else."

        hebrew = self._call_claude(system_prompt, user_message)

        print(f"   Output: {hebrew}")
        return hebrew

    def translate_he_to_en(self, hebrew_text: str) -> str:
        """
        Agent 3: Translate Hebrew to English using Claude.

        Args:
            hebrew_text: Hebrew input

        Returns:
            English translation (final output)
        """
        print(f"\n🔄 Agent 3: Hebrew → English")
        print(f"   Input:  {hebrew_text}")

        system_prompt = self.agent_instructions.get('he_to_en', '')

        user_message = f"Translate this Hebrew text to English:\n\n{hebrew_text}\n\nProvide ONLY the English translation, nothing else."

        english = self._call_claude(system_prompt, user_message)

        print(f"   Output: {english}")
        return english

    def run_chain(self, original: str, misspelled: str, error_rate: float) -> dict:
        """
        Run complete translation chain with real Claude agents.

        Args:
            original: Original clean text
            misspelled: Text with errors injected
            error_rate: Error rate (0.0-1.0)

        Returns:
            Dictionary with all intermediate results
        """
        print(f"\n{'='*70}")
        print(f"REAL TRANSLATION CHAIN - {int(error_rate*100)}% Error Rate")
        print(f"{'='*70}")
        print(f"\n📝 Original:   {original}")
        print(f"🔧 Misspelled: {misspelled}")

        # Step 1: EN → FR
        french = self.translate_en_to_fr(misspelled)

        # Step 2: FR → HE
        hebrew = self.translate_fr_to_he(french)

        # Step 3: HE → EN
        final_english = self.translate_he_to_en(hebrew)

        print(f"\n{'='*70}")
        print(f"✅ CHAIN COMPLETE")
        print(f"{'='*70}")
        print(f"\n🎯 Final Result: {final_english}")
        print(f"📊 Compare to:   {original}\n")

        return {
            'original': original,
            'misspelled': misspelled,
            'error_rate': error_rate,
            'french': french,
            'hebrew': hebrew,
            'final': final_english,
            'word_count': len(original.split())
        }


def main():
    """Main function to run real translation chain."""
    print("\n" + "="*70)
    print("REAL TRANSLATION CHAIN WITH CLAUDE AGENTS")
    print("Using SKILL-based agents with Anthropic API")
    print("="*70)

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
        print("\nPlease set your API key:")
        print("1. Copy example.env to .env:")
        print("   cp example.env .env")
        print("2. Edit .env and add your API key:")
        print("   ANTHROPIC_API_KEY=sk-ant-xxxxx")
        print("3. Run this script again\n")
        sys.exit(1)

    # Get input file from command line or use default
    if len(sys.argv) > 1:
        sentences_file = Path(sys.argv[1])
    else:
        sentences_file = Path("data/input/sentences.json")

    if not sentences_file.exists():
        print(f"\n❌ Error: {sentences_file} not found")
        print("Please run from project root directory")
        sys.exit(1)

    print(f"\n📂 Loading: {sentences_file}")

    with open(sentences_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sentences = data.get('sentences', [])
    print(f"✅ Loaded {len(sentences)} test cases\n")

    # Initialize real translator
    translator = AgentTranslator(api_key=api_key)

    # Store all results
    all_results = []

    # Process each sentence
    for i, item in enumerate(sentences, 1):
        print(f"\n{'#'*70}")
        print(f"# Test Case {i}/{len(sentences)}")
        print(f"{'#'*70}")

        try:
            result = translator.run_chain(
                original=item['original'],
                misspelled=item['misspelled'],
                error_rate=item['error_rate']
            )

            all_results.append(result)

        except Exception as e:
            print(f"\n❌ Error processing test case {i}: {e}")
            print("Continuing with next test case...\n")
            continue

        # Pause between items for readability (only in interactive mode)
        if i < len(sentences) and sys.stdin.isatty():
            try:
                input("\nPress Enter to continue to next test case...")
            except (EOFError, KeyboardInterrupt):
                print("\n\nContinuing...")

    # Save results to file with new structure: results/YYYY-MM-DD/input_name/
    date_str = datetime.now().strftime('%Y-%m-%d')
    input_name = sentences_file.stem  # e.g., "sanity_check", "same_sentence_progressive"

    output_dir = Path("results") / date_str / input_name
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    output_data = {
        "experiment_id": f"real_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "mode": "real_claude_agents",
        "model": translator.model,
        "results": all_results
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print("REAL TRANSLATION COMPLETE")
    print(f"{'='*70}")
    print(f"\n✅ Results saved to: {results_file}")
    print(f"\nYou can now analyze these results with:")
    print(f"python src/main.py analyze {results_file}")
    print()


if __name__ == '__main__':
    main()
