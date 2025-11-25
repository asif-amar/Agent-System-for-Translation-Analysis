"""
Experiment execution module.

Handles running translation experiments with progress tracking.
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Callable
from datetime import datetime


logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Execute translation experiments with progress tracking.

    This class provides interfaces for running experiments
    using both API and Claude Code modes.
    """

    def __init__(self, project_root: str):
        """
        Initialize experiment runner.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.logger = logging.getLogger(self.__class__.__name__)

    def prepare_experiment(
        self,
        input_file: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Prepare experiment configuration.

        Args:
            input_file: Path to input dataset file
            output_dir: Output directory (auto-generated if None)

        Returns:
            Dictionary with experiment information

        Raises:
            FileNotFoundError: If input file doesn't exist
            subprocess.CalledProcessError: If preparation fails
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_dir is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_dir = self.project_root / "results" / date_str / input_path.stem

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Preparing experiment for {input_path.name}")

        # Run prepare command
        cmd = [
            'python',
            str(self.src_dir / 'main.py'),
            'prepare',
            str(input_path),
            '--output-dir',
            str(output_dir)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_root)
            )

            self.logger.info("Experiment prepared successfully")

            return {
                'success': True,
                'output_dir': str(output_dir),
                'prompts_file': str(output_dir / 'agent_prompts.txt'),
                'template_file': str(output_dir / 'results_template.json'),
                'config_file': str(output_dir / 'experiment_config.json'),
                'message': 'Experiment prepared successfully'
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Experiment preparation failed: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr,
                'message': 'Experiment preparation failed'
            }

    def run_analysis(
        self,
        results_file: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Run analysis on experiment results.

        Args:
            results_file: Path to results JSON file
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with analysis results

        Raises:
            FileNotFoundError: If results file doesn't exist
        """
        results_path = Path(results_file)
        if not results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")

        output_dir = results_path.parent

        self.logger.info(f"Running analysis on {results_path.name}")

        if progress_callback:
            progress_callback("Loading results...")

        # Run analyze command
        cmd = [
            'python',
            str(self.src_dir / 'main.py'),
            'analyze',
            str(results_path),
            '--output-dir',
            str(output_dir)
        ]

        try:
            if progress_callback:
                progress_callback("Calculating metrics...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_root)
            )

            if progress_callback:
                progress_callback("Analysis complete!")

            self.logger.info("Analysis completed successfully")

            return {
                'success': True,
                'metrics_file': str(output_dir / 'metrics_output.csv'),
                'graph_file': str(output_dir / 'error_vs_distance.png'),
                'output': result.stdout,
                'message': 'Analysis completed successfully'
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Analysis failed: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr,
                'message': 'Analysis failed'
            }

    def run_full_experiment(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Run full automatic experiment with Claude Code translations.

        Args:
            input_file: Path to input dataset file
            output_dir: Output directory (auto-generated if None)
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with experiment results
        """
        import json
        import time

        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_dir is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_dir = self.project_root / "results" / date_str / input_path.stem

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback("Loading input dataset...")

        # Load input data
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        sentences = input_data.get('sentences', [])
        total = len(sentences)

        if progress_callback:
            progress_callback(f"Starting translations for {total} sentences...")

        # Import translation function
        import sys
        sys.path.insert(0, str(self.src_dir))

        results = []

        for i, item in enumerate(sentences):
            if progress_callback:
                progress_callback(f"Translating sentence {i+1}/{total}...")

            # Perform translations using Claude's built-in capabilities
            misspelled = item['misspelled']

            # EN -> FR (with retry on rate limit)
            french = self._translate_with_retry(self._translate_en_to_fr, misspelled, progress_callback)

            # FR -> HE (with retry on rate limit)
            hebrew = self._translate_with_retry(self._translate_fr_to_he, french, progress_callback)

            # HE -> EN (with retry on rate limit)
            final = self._translate_with_retry(self._translate_he_to_en, hebrew, progress_callback)

            results.append({
                'id': item.get('id', f'test_{i}'),
                'original': item['original'],
                'misspelled': misspelled,
                'error_rate': item.get('error_rate', 0.0),
                'french': french,
                'hebrew': hebrew,
                'final': final,
                'word_count': item.get('word_count', len(item['original'].split()))
            })

        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = output_dir / f'results_ui_{timestamp}.json'

        output_data = {
            'experiment_id': f'ui_experiment_{timestamp}',
            'timestamp': datetime.now().isoformat(),
            'mode': 'ui_automatic_execution',
            'input_file': input_path.name,
            'results': results,
            'metadata': {
                'total_test_cases': len(results),
                'translation_chain': 'EN → FR → HE → EN'
            }
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if progress_callback:
            progress_callback("Experiment complete!")

        return {
            'success': True,
            'results_file': str(results_file),
            'output_dir': str(output_dir),
            'num_sentences': len(results),
            'message': f'Successfully translated {len(results)} sentences'
        }

    def _translate_with_retry(
        self,
        translate_func: Callable[[str], str],
        text: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        max_retries: int = 3
    ) -> str:
        """
        Translate text with retry logic for rate limiting.

        Args:
            translate_func: Translation function to call
            text: Text to translate
            progress_callback: Optional callback for progress updates
            max_retries: Maximum number of retry attempts

        Returns:
            Translated text
        """
        import time
        from google.api_core import exceptions

        for attempt in range(max_retries):
            try:
                return translate_func(text)
            except exceptions.ResourceExhausted as e:
                # Extract retry delay from error message
                error_msg = str(e)
                retry_delay = 10  # Default to 10 seconds

                # Try to parse retry delay from error message
                if "retry in" in error_msg.lower():
                    import re
                    match = re.search(r'retry in (\d+\.?\d*)', error_msg.lower())
                    if match:
                        retry_delay = float(match.group(1))

                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"Rate limit hit. Waiting {retry_delay:.0f} seconds...")
                    time.sleep(retry_delay + 1)  # Add 1 second buffer
                else:
                    raise

        return ""

    def _translate_en_to_fr(self, text: str) -> str:
        """Translate English to French using Gemini API."""
        import os
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are a professional English to French translator.

Translate the following English text to French. The text may contain spelling errors - use context to infer the correct words and produce natural, grammatically correct French.

English text: {text}

Provide ONLY the French translation, no explanations."""

        response = model.generate_content(prompt)
        return response.text.strip()

    def _translate_fr_to_he(self, text: str) -> str:
        """Translate French to Hebrew using Gemini API."""
        import os
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are a professional French to Hebrew translator.

Translate the following French text to Hebrew. Produce natural, grammatically correct Hebrew with proper syntax.

French text: {text}

Provide ONLY the Hebrew translation, no explanations."""

        response = model.generate_content(prompt)
        return response.text.strip()

    def _translate_he_to_en(self, text: str) -> str:
        """Translate Hebrew to English using Gemini API."""
        import os
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are a professional Hebrew to English translator.

Translate the following Hebrew text to English. Produce natural, grammatically correct English.

Hebrew text: {text}

Provide ONLY the English translation, no explanations."""

        response = model.generate_content(prompt)
        return response.text.strip()

    def get_experiment_status(self, output_dir: str) -> Dict:
        """
        Check status of experiment in a directory.

        Args:
            output_dir: Path to experiment output directory

        Returns:
            Dictionary with experiment status information
        """
        output_path = Path(output_dir)

        if not output_path.exists():
            return {'status': 'not_found', 'message': 'Directory does not exist'}

        config_file = output_path / 'experiment_config.json'
        template_file = output_path / 'results_template.json'
        results_files = list(output_path.glob('results_*.json'))

        has_config = config_file.exists()
        has_template = template_file.exists()
        has_results = len(results_files) > 0

        if not has_config:
            status = 'not_prepared'
        elif has_results:
            status = 'completed'
        elif has_template:
            status = 'prepared'
        else:
            status = 'unknown'

        return {
            'status': status,
            'has_config': has_config,
            'has_template': has_template,
            'has_results': has_results,
            'results_files': [str(f) for f in results_files]
        }
