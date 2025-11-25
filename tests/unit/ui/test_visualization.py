"""
Unit tests for visualization module.
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from src.ui.visualization import InteractiveVisualizer


class TestInteractiveVisualizer:
    """Test cases for InteractiveVisualizer class."""

    @pytest.fixture
    def visualizer(self):
        """Create InteractiveVisualizer instance."""
        return InteractiveVisualizer()

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'error_rate': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            'cosine_distance': [0.0, 0.05, 0.12, 0.20, 0.30, 0.45],
            'euclidean_distance': [0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
            'manhattan_distance': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        })

    def test_init(self, visualizer):
        """Test visualizer initialization."""
        assert visualizer is not None
        assert isinstance(visualizer.default_colors, list)

    def test_plot_error_vs_distance(self, visualizer, sample_data):
        """Test error vs distance plot generation."""
        fig = visualizer.plot_error_vs_distance(
            df=sample_data,
            metric='cosine_distance',
            title='Test Plot'
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1  # At least one trace
        assert fig.layout.title.text == 'Test Plot'

    def test_plot_error_vs_distance_with_trendline(self, visualizer, sample_data):
        """Test plot with trendline."""
        fig = visualizer.plot_error_vs_distance(
            df=sample_data,
            metric='cosine_distance'
        )

        # Should have main plot + trendline
        assert len(fig.data) == 2

    def test_plot_error_vs_distance_insufficient_data(self, visualizer):
        """Test plot with insufficient data for trendline."""
        small_data = pd.DataFrame({
            'error_rate': [0.0, 0.1],
            'cosine_distance': [0.0, 0.05]
        })

        fig = visualizer.plot_error_vs_distance(
            df=small_data,
            metric='cosine_distance'
        )

        # Should have only main plot, no trendline
        assert len(fig.data) == 1

    def test_plot_multiple_metrics(self, visualizer, sample_data):
        """Test multiple metrics plot."""
        metrics = ['cosine_distance', 'euclidean_distance', 'manhattan_distance']

        fig = visualizer.plot_multiple_metrics(
            df=sample_data,
            metrics=metrics,
            title='Multi-Metric Test'
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # One trace per metric
        assert fig.layout.title.text == 'Multi-Metric Test'

    def test_plot_multiple_metrics_missing_column(self, visualizer, sample_data):
        """Test multiple metrics with missing column."""
        metrics = ['cosine_distance', 'nonexistent_metric']

        fig = visualizer.plot_multiple_metrics(
            df=sample_data,
            metrics=metrics
        )

        # Should only plot existing metrics
        assert len(fig.data) == 1

    def test_plot_distribution(self, visualizer, sample_data):
        """Test distribution plot generation."""
        fig = visualizer.plot_distribution(
            df=sample_data,
            metric='cosine_distance',
            title='Distribution Test'
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.layout.title.text == 'Distribution Test'

    def test_create_dashboard(self, visualizer, sample_data):
        """Test dashboard creation."""
        fig = visualizer.create_dashboard(
            df=sample_data,
            metric='cosine_distance'
        )

        assert isinstance(fig, go.Figure)
        # Dashboard has 4 subplots
        assert len(fig.data) >= 4

    def test_create_dashboard_custom_metric(self, visualizer, sample_data):
        """Test dashboard with different metric."""
        fig = visualizer.create_dashboard(
            df=sample_data,
            metric='euclidean_distance'
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 4

    def test_plot_with_empty_dataframe(self, visualizer):
        """Test plotting with empty DataFrame."""
        empty_df = pd.DataFrame()

        with pytest.raises(Exception):
            visualizer.plot_error_vs_distance(empty_df)

    def test_color_assignment(self, visualizer, sample_data):
        """Test that colors are assigned correctly."""
        fig = visualizer.plot_multiple_metrics(
            df=sample_data,
            metrics=['cosine_distance', 'euclidean_distance']
        )

        # Verify different colors for different traces
        colors = [trace.line.color for trace in fig.data]
        assert len(set(colors)) == len(colors)  # All unique

    def test_interactive_features(self, visualizer, sample_data):
        """Test that interactive features are configured."""
        fig = visualizer.plot_error_vs_distance(
            df=sample_data,
            metric='cosine_distance'
        )

        # Check hover mode is set
        assert fig.layout.hovermode in ['closest', 'x unified', 'x', 'y']

        # Check template is set
        assert fig.layout.template is not None
