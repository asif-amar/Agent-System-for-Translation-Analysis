"""
Data loading and caching module.

Handles loading input datasets, experiment results, and metrics.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load and cache experiment data.

    This class provides efficient data loading with caching
    for input datasets, results, and computed metrics.
    """

    def __init__(self):
        """Initialize the data loader."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {}

    def load_input_dataset(self, file_path: str) -> Dict:
        """
        Load input dataset from JSON file.

        Args:
            file_path: Path to input JSON file

        Returns:
            Dictionary containing dataset information

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        cache_key = f"input_{file_path}"

        if cache_key in self._cache:
            self.logger.debug(f"Loading from cache: {file_path}")
            return self._cache[cache_key]

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'sentences' not in data:
                raise ValueError("Invalid dataset format: missing 'sentences' key")

            self._cache[cache_key] = data
            self.logger.info(f"Loaded dataset: {file_path_obj.name} ({len(data['sentences'])} sentences)")
            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def load_results(self, file_path: str) -> Dict:
        """
        Load experiment results from JSON file.

        Args:
            file_path: Path to results JSON file

        Returns:
            Dictionary containing experiment results

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        cache_key = f"results_{file_path}"

        if cache_key in self._cache:
            self.logger.debug(f"Loading from cache: {file_path}")
            return self._cache[cache_key]

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Results file not found: {file_path}")

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'results' not in data:
                raise ValueError("Invalid results format: missing 'results' key")

            self._cache[cache_key] = data
            self.logger.info(f"Loaded results: {file_path_obj.name} ({len(data['results'])} entries)")
            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def load_metrics(self, file_path: str) -> pd.DataFrame:
        """
        Load metrics from CSV file.

        Args:
            file_path: Path to metrics CSV file

        Returns:
            DataFrame containing metrics data

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        cache_key = f"metrics_{file_path}"

        if cache_key in self._cache:
            self.logger.debug(f"Loading from cache: {file_path}")
            return self._cache[cache_key]

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Metrics file not found: {file_path}")

        df = pd.read_csv(file_path_obj)
        self._cache[cache_key] = df
        self.logger.info(f"Loaded metrics: {file_path_obj.name} ({len(df)} rows)")
        return df

    def get_result_summary(self, results: Dict) -> Dict:
        """
        Generate summary statistics from results.

        Args:
            results: Results dictionary

        Returns:
            Dictionary with summary statistics
        """
        result_list = results.get('results', [])

        if not result_list:
            return {'error': 'No results found'}

        error_rates = [r['error_rate'] for r in result_list]

        return {
            'experiment_id': results.get('experiment_id', 'unknown'),
            'timestamp': results.get('timestamp', 'unknown'),
            'mode': results.get('mode', 'unknown'),
            'input_file': results.get('input_file', 'unknown'),
            'num_sentences': len(result_list),
            'error_rate_min': min(error_rates),
            'error_rate_max': max(error_rates),
            'error_rate_step': error_rates[1] - error_rates[0] if len(error_rates) > 1 else 0
        }

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self.logger.info("Cache cleared")
