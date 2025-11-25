"""
Unit tests for comparison module.
"""

import pytest
import pandas as pd
from src.ui.comparison import ResultsAnalyzer


class TestResultsAnalyzer:
    """Test cases for ResultsAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create ResultsAnalyzer instance."""
        return ResultsAnalyzer()

    @pytest.fixture
    def sample_results(self):
        """Create sample results data."""
        return {
            'experiment_id': 'test_exp',
            'results': [
                {
                    'id': 'test_001',
                    'original': 'The quick brown fox jumps over the lazy dog',
                    'misspelled': 'The quik brown fox jumps ovr the lazy dog',
                    'french': 'Le renard brun rapide saute par-dessus le chien paresseux',
                    'hebrew': 'השועל החום המהיר קופץ מעל הכלב העצלן',
                    'final': 'The fast brown fox jumps over the lazy dog',
                    'error_rate': 0.15,
                    'word_count': 9
                },
                {
                    'id': 'test_002',
                    'original': 'Another test sentence with more words',
                    'misspelled': 'Another tst sentence with more words',
                    'french': 'Une autre phrase de test avec plus de mots',
                    'hebrew': 'משפט בדיקה נוסף עם יותר מילים',
                    'final': 'Another test sentence with additional words',
                    'error_rate': 0.25,
                    'word_count': 6
                }
            ]
        }

    def test_create_comparison_dataframe(self, analyzer, sample_results):
        """Test creating comparison DataFrame."""
        df = analyzer.create_comparison_dataframe(sample_results)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'error_rate' in df.columns
        assert 'original' in df.columns
        assert 'final' in df.columns
        assert df['error_rate'].iloc[0] == 15.0  # Converted to percentage

    def test_calculate_text_changes(self, analyzer):
        """Test text changes calculation."""
        original = "The quick brown fox jumps"
        final = "The fast brown fox leaps"

        changes = analyzer.calculate_text_changes(original, final)

        assert changes['original_word_count'] == 5
        assert changes['final_word_count'] == 5
        assert changes['common_words'] == 3  # the, brown, fox
        assert changes['removed_words'] == 2  # quick, jumps
        assert changes['added_words'] == 2  # fast, leaps
        assert 0 < changes['word_retention_rate'] < 1

    def test_calculate_text_changes_identical(self, analyzer):
        """Test text changes with identical texts."""
        text = "The quick brown fox"
        changes = analyzer.calculate_text_changes(text, text)

        assert changes['common_words'] == 4
        assert changes['removed_words'] == 0
        assert changes['added_words'] == 0
        assert changes['word_retention_rate'] == 1.0

    def test_calculate_text_changes_empty(self, analyzer):
        """Test text changes with empty original."""
        changes = analyzer.calculate_text_changes("", "test")

        assert changes['original_word_count'] == 0
        assert changes['word_retention_rate'] == 0

    def test_get_error_level_statistics(self, analyzer, sample_results):
        """Test getting statistics for specific error level."""
        df = analyzer.create_comparison_dataframe(sample_results)

        stats = analyzer.get_error_level_statistics(df, 0.15)

        assert stats['error_rate'] == 0.15
        assert 'original_text' in stats
        assert 'final_text' in stats
        assert stats['word_count'] == 9

    def test_get_error_level_statistics_not_found(self, analyzer, sample_results):
        """Test getting statistics for non-existent error level."""
        df = analyzer.create_comparison_dataframe(sample_results)

        stats = analyzer.get_error_level_statistics(df, 0.99)

        assert 'error' in stats

    def test_compare_metrics_across_levels(self, analyzer):
        """Test comparing metrics across error levels."""
        df = pd.DataFrame({
            'error_rate': [0, 10, 20, 30],
            'cosine_distance': [0.0, 0.1, 0.25, 0.4]
        })

        comparison = analyzer.compare_metrics_across_levels(df, 'cosine_distance')

        assert 'change' in comparison.columns
        assert 'percent_change' in comparison.columns
        assert len(comparison) == 4

    def test_compare_metrics_invalid_metric(self, analyzer):
        """Test comparing with invalid metric name."""
        df = pd.DataFrame({'error_rate': [0, 10]})

        with pytest.raises(ValueError, match="not found in data"):
            analyzer.compare_metrics_across_levels(df, 'invalid_metric')

    def test_generate_summary_report(self, analyzer, sample_results):
        """Test generating summary report."""
        summary = analyzer.generate_summary_report(sample_results)

        assert summary['experiment_id'] == 'test_exp'
        assert summary['total_sentences'] == 2
        assert 0.15 in summary['error_rates']
        assert 0.25 in summary['error_rates']

    def test_generate_summary_report_with_metrics(self, analyzer, sample_results):
        """Test generating summary report with metrics."""
        metrics_df = pd.DataFrame({
            'error_rate': [15, 25],
            'cosine_distance': [0.1, 0.3]
        })

        summary = analyzer.generate_summary_report(sample_results, metrics_df)

        assert 'metrics' in summary
        assert summary['metrics']['min_distance'] == 0.1
        assert summary['metrics']['max_distance'] == 0.3

    def test_filter_by_error_range(self, analyzer):
        """Test filtering by error rate range."""
        df = pd.DataFrame({
            'error_rate': [0, 10, 20, 30, 40, 50],
            'value': [1, 2, 3, 4, 5, 6]
        })

        filtered = analyzer.filter_by_error_range(df, 0.1, 0.3)

        assert len(filtered) == 3
        assert filtered['error_rate'].min() == 10
        assert filtered['error_rate'].max() == 30

    def test_filter_by_error_range_no_results(self, analyzer):
        """Test filtering with range that matches nothing."""
        df = pd.DataFrame({
            'error_rate': [0, 10, 20],
            'value': [1, 2, 3]
        })

        filtered = analyzer.filter_by_error_range(df, 0.5, 1.0)

        assert len(filtered) == 0
