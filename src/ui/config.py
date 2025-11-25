"""
UI configuration module.

Manages UI settings, paths, and display options.
"""

from pathlib import Path
from typing import List, Dict
import json


class UIConfig:
    """
    Configuration manager for UI settings.

    Attributes:
        project_root: Root directory of the project
        data_dir: Directory containing input data
        results_dir: Directory containing experiment results
        available_datasets: List of available input datasets
    """

    def __init__(self, project_root: str = None):
        """
        Initialize UI configuration.

        Args:
            project_root: Path to project root directory
        """
        if project_root is None:
            # Auto-detect from this file's location
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        self.data_dir = self.project_root / "data" / "input"
        self.results_dir = self.project_root / "results"
        self.src_dir = self.project_root / "src"

        # UI display settings
        self.page_title = "Translation Quality Analysis System"
        self.page_icon = "🌐"
        self.layout = "wide"

        # Visualization settings
        self.default_dpi = 300
        self.chart_height = 400
        self.chart_width = 800

        # Metrics to display
        self.distance_metrics = [
            'cosine_distance',
            'euclidean_distance',
            'manhattan_distance'
        ]

        self.similarity_metrics = [
            'cosine_similarity'
        ]

    def get_available_datasets(self) -> List[Dict]:
        """
        Get list of available input datasets.

        Returns:
            List of dataset info dictionaries
        """
        datasets = []

        if not self.data_dir.exists():
            return datasets

        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract metadata
                metadata = data.get('metadata', {})
                num_sentences = len(data.get('sentences', []))

                datasets.append({
                    'name': json_file.stem,
                    'path': str(json_file),
                    'type': metadata.get('type', 'unknown'),
                    'description': metadata.get('description', ''),
                    'num_sentences': num_sentences,
                    'created_at': metadata.get('created_at', 'unknown')
                })
            except Exception:
                continue

        return sorted(datasets, key=lambda x: x['name'])

    def get_available_results(self) -> List[Dict]:
        """
        Get list of available experiment results.

        Returns:
            List of result info dictionaries
        """
        results = []

        if not self.results_dir.exists():
            return results

        # Structure: results/YYYY-MM-DD/input_name/results_*.json
        for date_dir in self.results_dir.iterdir():
            if not date_dir.is_dir():
                continue

            for input_dir in date_dir.iterdir():
                if not input_dir.is_dir():
                    continue

                for result_file in input_dir.glob("results_*.json"):
                    try:
                        with open(result_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        results.append({
                            'date': date_dir.name,
                            'input_name': input_dir.name,
                            'file_name': result_file.name,
                            'path': str(result_file),
                            'experiment_id': data.get('experiment_id', ''),
                            'mode': data.get('mode', 'unknown'),
                            'num_results': len(data.get('results', [])),
                            'timestamp': data.get('timestamp', '')
                        })
                    except Exception:
                        continue

        return sorted(results, key=lambda x: x['timestamp'], reverse=True)

    def get_metrics_files(self, result_path: str) -> Dict:
        """
        Get associated metrics and visualization files for a result.

        Args:
            result_path: Path to results JSON file

        Returns:
            Dictionary with paths to associated files
        """
        result_file = Path(result_path)
        result_dir = result_file.parent

        return {
            'metrics_csv': result_dir / 'metrics_output.csv',
            'distance_graph': result_dir / 'error_vs_distance.png',
            'dashboard': result_dir / 'summary_dashboard.png',
            'multi_metrics': result_dir / 'multi_metrics.png'
        }
