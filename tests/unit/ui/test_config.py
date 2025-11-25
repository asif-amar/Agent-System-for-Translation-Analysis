"""
Unit tests for UI configuration module.
"""

import pytest
from pathlib import Path
import json
import tempfile
from src.ui.config import UIConfig


class TestUIConfig:
    """Test cases for UIConfig class."""

    def test_init_default(self):
        """Test default initialization."""
        config = UIConfig()

        assert config.project_root.is_dir()
        assert config.data_dir.name == "input"
        assert config.results_dir.name == "results"
        assert config.page_title == "Translation Quality Analysis System"

    def test_init_custom_root(self, tmp_path):
        """Test initialization with custom project root."""
        config = UIConfig(project_root=str(tmp_path))

        assert config.project_root == tmp_path
        assert config.data_dir == tmp_path / "data" / "input"
        assert config.results_dir == tmp_path / "results"

    def test_display_settings(self):
        """Test UI display settings."""
        config = UIConfig()

        assert config.page_icon == "🌐"
        assert config.layout == "wide"
        assert config.default_dpi == 300
        assert config.chart_height == 400

    def test_metrics_configuration(self):
        """Test metrics configuration."""
        config = UIConfig()

        assert 'cosine_distance' in config.distance_metrics
        assert 'euclidean_distance' in config.distance_metrics
        assert 'manhattan_distance' in config.distance_metrics
        assert 'cosine_similarity' in config.similarity_metrics

    def test_get_available_datasets_empty(self, tmp_path):
        """Test get_available_datasets with no datasets."""
        config = UIConfig(project_root=str(tmp_path))
        datasets = config.get_available_datasets()

        assert datasets == []

    def test_get_available_datasets(self, tmp_path):
        """Test get_available_datasets with mock datasets."""
        config = UIConfig(project_root=str(tmp_path))
        config.data_dir.mkdir(parents=True, exist_ok=True)

        # Create mock dataset
        dataset = {
            'sentences': [
                {'original': 'test', 'misspelled': 'tst', 'error_rate': 0.1}
            ],
            'metadata': {
                'type': 'test',
                'description': 'Test dataset',
                'created_at': '2025-11-23'
            }
        }

        dataset_file = config.data_dir / "test_dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(dataset, f)

        datasets = config.get_available_datasets()

        assert len(datasets) == 1
        assert datasets[0]['name'] == 'test_dataset'
        assert datasets[0]['type'] == 'test'
        assert datasets[0]['num_sentences'] == 1

    def test_get_available_results_empty(self, tmp_path):
        """Test get_available_results with no results."""
        config = UIConfig(project_root=str(tmp_path))
        results = config.get_available_results()

        assert results == []

    def test_get_available_results(self, tmp_path):
        """Test get_available_results with mock results."""
        config = UIConfig(project_root=str(tmp_path))

        # Create mock results structure
        results_dir = config.results_dir / "2025-11-23" / "test_input"
        results_dir.mkdir(parents=True, exist_ok=True)

        result_data = {
            'experiment_id': 'test_exp',
            'timestamp': '2025-11-23T12:00:00',
            'mode': 'test',
            'results': [{'original': 'test', 'final': 'test', 'error_rate': 0.0}]
        }

        result_file = results_dir / "results_20251123_120000.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f)

        results = config.get_available_results()

        assert len(results) == 1
        assert results[0]['date'] == '2025-11-23'
        assert results[0]['input_name'] == 'test_input'
        assert results[0]['experiment_id'] == 'test_exp'
        assert results[0]['num_results'] == 1

    def test_get_metrics_files(self, tmp_path):
        """Test get_metrics_files."""
        config = UIConfig(project_root=str(tmp_path))

        result_path = tmp_path / "results" / "2025-11-23" / "test" / "results.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)

        metrics_files = config.get_metrics_files(str(result_path))

        assert 'metrics_csv' in metrics_files
        assert 'distance_graph' in metrics_files
        assert 'dashboard' in metrics_files
        assert metrics_files['metrics_csv'].name == 'metrics_output.csv'
