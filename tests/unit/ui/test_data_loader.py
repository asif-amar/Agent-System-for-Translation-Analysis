"""
Unit tests for data loader module.
"""

import pytest
import json
import pandas as pd
from pathlib import Path
from src.ui.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class."""

    @pytest.fixture
    def loader(self):
        """Create DataLoader instance."""
        return DataLoader()

    @pytest.fixture
    def sample_input(self, tmp_path):
        """Create sample input file."""
        data = {
            'sentences': [
                {
                    'id': 'test_001',
                    'original': 'The quick brown fox',
                    'misspelled': 'The quik brown fox',
                    'error_rate': 0.15,
                    'word_count': 4
                }
            ],
            'metadata': {
                'type': 'test',
                'description': 'Test dataset'
            }
        }

        file_path = tmp_path / "test_input.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)

        return file_path

    @pytest.fixture
    def sample_results(self, tmp_path):
        """Create sample results file."""
        data = {
            'experiment_id': 'test_exp',
            'timestamp': '2025-11-23T12:00:00',
            'results': [
                {
                    'original': 'The quick brown fox',
                    'final': 'The fast brown fox',
                    'error_rate': 0.15
                }
            ]
        }

        file_path = tmp_path / "test_results.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)

        return file_path

    @pytest.fixture
    def sample_metrics(self, tmp_path):
        """Create sample metrics CSV."""
        df = pd.DataFrame({
            'error_rate': [0.0, 0.1, 0.2],
            'cosine_distance': [0.0, 0.1, 0.2],
            'euclidean_distance': [0.0, 0.5, 1.0]
        })

        file_path = tmp_path / "metrics.csv"
        df.to_csv(file_path, index=False)

        return file_path

    def test_load_input_dataset_success(self, loader, sample_input):
        """Test successful input dataset loading."""
        data = loader.load_input_dataset(str(sample_input))

        assert 'sentences' in data
        assert len(data['sentences']) == 1
        assert data['sentences'][0]['id'] == 'test_001'

    def test_load_input_dataset_file_not_found(self, loader):
        """Test loading non-existent input file."""
        with pytest.raises(FileNotFoundError):
            loader.load_input_dataset('/nonexistent/file.json')

    def test_load_input_dataset_invalid_format(self, loader, tmp_path):
        """Test loading invalid format."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, 'w') as f:
            json.dump({'invalid': 'format'}, f)

        with pytest.raises(ValueError, match="missing 'sentences' key"):
            loader.load_input_dataset(str(invalid_file))

    def test_load_input_dataset_caching(self, loader, sample_input):
        """Test data caching."""
        # First load
        data1 = loader.load_input_dataset(str(sample_input))

        # Second load (should use cache)
        data2 = loader.load_input_dataset(str(sample_input))

        assert data1 is data2  # Same object reference

    def test_load_results_success(self, loader, sample_results):
        """Test successful results loading."""
        data = loader.load_results(str(sample_results))

        assert 'results' in data
        assert len(data['results']) == 1
        assert data['experiment_id'] == 'test_exp'

    def test_load_results_file_not_found(self, loader):
        """Test loading non-existent results file."""
        with pytest.raises(FileNotFoundError):
            loader.load_results('/nonexistent/results.json')

    def test_load_results_invalid_format(self, loader, tmp_path):
        """Test loading invalid results format."""
        invalid_file = tmp_path / "invalid_results.json"
        with open(invalid_file, 'w') as f:
            json.dump({'no_results': 'here'}, f)

        with pytest.raises(ValueError, match="missing 'results' key"):
            loader.load_results(str(invalid_file))

    def test_load_metrics_success(self, loader, sample_metrics):
        """Test successful metrics loading."""
        df = loader.load_metrics(str(sample_metrics))

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'error_rate' in df.columns
        assert 'cosine_distance' in df.columns

    def test_load_metrics_file_not_found(self, loader):
        """Test loading non-existent metrics file."""
        with pytest.raises(FileNotFoundError):
            loader.load_metrics('/nonexistent/metrics.csv')

    def test_get_result_summary(self, loader, sample_results):
        """Test result summary generation."""
        results = loader.load_results(str(sample_results))
        summary = loader.get_result_summary(results)

        assert summary['experiment_id'] == 'test_exp'
        assert summary['total_sentences'] == 1
        assert summary['mode'] == 'unknown'

    def test_get_result_summary_empty(self, loader):
        """Test summary for empty results."""
        results = {'results': []}
        summary = loader.get_result_summary(results)

        assert 'error' in summary

    def test_clear_cache(self, loader, sample_input):
        """Test cache clearing."""
        # Load data to populate cache
        loader.load_input_dataset(str(sample_input))

        # Clear cache
        loader.clear_cache()

        # Verify cache is empty
        assert len(loader._cache) == 0
