"""
Interactive visualization components.

Provides Plotly-based interactive visualizations for the UI.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


logger = logging.getLogger(__name__)


class InteractiveVisualizer:
    """
    Create interactive visualizations using Plotly.

    This class generates publication-quality interactive charts
    for exploring translation quality degradation.
    """

    def __init__(self):
        """Initialize the visualizer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_colors = px.colors.qualitative.Set2

    def plot_error_vs_distance(
        self,
        df: pd.DataFrame,
        metric: str = 'cosine_distance',
        title: str = "Error Rate vs Semantic Distance"
    ) -> go.Figure:
        """
        Create interactive error rate vs distance plot.

        Args:
            df: DataFrame with error_rate and metric columns
            metric: Distance metric to plot
            title: Chart title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        error_pct = df['error_rate'] * 100

        # Add line plot
        fig.add_trace(go.Scatter(
            x=error_pct,
            y=df[metric],
            mode='lines+markers',
            name='Measured Distance',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=10, color='#2E86AB'),
            hovertemplate='Error Rate: %{x:.0f}%<br>Distance: %{y:.4f}<extra></extra>'
        ))

        # Add trendline
        if len(df) >= 3:
            z = np.polyfit(error_pct, df[metric], 2)
            p = np.poly1d(z)
            x_trend = np.linspace(error_pct.min(), error_pct.max(), 100)

            fig.add_trace(go.Scatter(
                x=x_trend,
                y=p(x_trend),
                mode='lines',
                name='Polynomial Fit',
                line=dict(color='#A23B72', width=2, dash='dash'),
                hovertemplate='Trend<extra></extra>'
            ))

        fig.update_layout(
            title=title,
            xaxis_title='Spelling Error Rate (%)',
            yaxis_title=f'{metric.replace("_", " ").title()}',
            hovermode='closest',
            template='plotly_white',
            height=500,
            font=dict(size=12)
        )

        return fig

    def plot_multiple_metrics(
        self,
        df: pd.DataFrame,
        metrics: List[str],
        title: str = "Multiple Distance Metrics Comparison"
    ) -> go.Figure:
        """
        Plot multiple metrics on same chart.

        Args:
            df: DataFrame with error_rate and metric columns
            metrics: List of metric column names
            title: Chart title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        error_pct = df['error_rate'] * 100

        for i, metric in enumerate(metrics):
            if metric not in df.columns:
                continue

            color = self.default_colors[i % len(self.default_colors)]

            fig.add_trace(go.Scatter(
                x=error_pct,
                y=df[metric],
                mode='lines+markers',
                name=metric.replace('_', ' ').title(),
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                hovertemplate=f'{metric}: %{{y:.4f}}<extra></extra>'
            ))

        fig.update_layout(
            title=title,
            xaxis_title='Spelling Error Rate (%)',
            yaxis_title='Distance Value',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            font=dict(size=12),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        return fig

    def plot_distribution(
        self,
        df: pd.DataFrame,
        metric: str = 'cosine_distance',
        title: str = "Distance Distribution"
    ) -> go.Figure:
        """
        Create histogram of distance values.

        Args:
            df: DataFrame with metric column
            metric: Distance metric to plot
            title: Chart title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=df[metric],
            nbinsx=15,
            name='Distance',
            marker=dict(color='#2E86AB', line=dict(color='black', width=1))
        ))

        fig.update_layout(
            title=title,
            xaxis_title=f'{metric.replace("_", " ").title()}',
            yaxis_title='Frequency',
            template='plotly_white',
            height=400,
            font=dict(size=12)
        )

        return fig

    def create_dashboard(
        self,
        df: pd.DataFrame,
        metric: str = 'cosine_distance'
    ) -> go.Figure:
        """
        Create comprehensive dashboard with multiple views.

        Args:
            df: DataFrame with experiment data
            metric: Primary distance metric

        Returns:
            Plotly figure with subplots
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Error Rate vs Distance',
                'Distance Distribution',
                'Change in Distance',
                'Summary Statistics'
            ),
            specs=[[{'type': 'scatter'}, {'type': 'histogram'}],
                   [{'type': 'bar'}, {'type': 'table'}]]
        )

        error_pct = df['error_rate'] * 100

        # Plot 1: Error vs Distance
        fig.add_trace(
            go.Scatter(x=error_pct, y=df[metric], mode='lines+markers',
                      name='Distance', line=dict(color='#2E86AB')),
            row=1, col=1
        )

        # Plot 2: Distribution
        fig.add_trace(
            go.Histogram(x=df[metric], nbinsx=15, name='Distribution',
                        marker=dict(color='#2E86AB')),
            row=1, col=2
        )

        # Plot 3: Changes
        changes = df[metric].diff().fillna(0)
        fig.add_trace(
            go.Bar(x=error_pct, y=changes, name='Change',
                  marker=dict(color='#A23B72')),
            row=2, col=1
        )

        # Plot 4: Statistics table
        stats_data = {
            'Metric': ['Sample Size', 'Min Distance', 'Max Distance',
                      'Mean Distance', 'Std Distance'],
            'Value': [
                len(df),
                f"{df[metric].min():.4f}",
                f"{df[metric].max():.4f}",
                f"{df[metric].mean():.4f}",
                f"{df[metric].std():.4f}"
            ]
        }

        fig.add_trace(
            go.Table(
                header=dict(values=['<b>Metric</b>', '<b>Value</b>'],
                           fill_color='lightgray'),
                cells=dict(values=[stats_data['Metric'], stats_data['Value']],
                          align='left')
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Translation Chain Analysis Dashboard",
            template='plotly_white'
        )

        return fig
