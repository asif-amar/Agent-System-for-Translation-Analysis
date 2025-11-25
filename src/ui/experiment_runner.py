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
