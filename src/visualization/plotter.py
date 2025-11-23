"""
Visualization module for generating graphs and plots.

This module provides functionality to visualize translation quality degradation
across different error rates.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


logger = logging.getLogger(__name__)


class GraphPlotter:
    """
    Generate visualization graphs for translation experiments.

    This class creates publication-quality graphs showing the relationship
    between spelling error rates and semantic distance.
    """

    def __init__(self, style: str = "seaborn-v0_8"):
        """
        Initialize the graph plotter.

        Args:
            style: Matplotlib style to use for plots
        """
        self.style = style
        self.logger = logging.getLogger(self.__class__.__name__)

        # Set default style
        try:
            plt.style.use(style)
        except OSError:
            self.logger.warning(f"Style '{style}' not found, using default")

        # Set seaborn style
        sns.set_palette("husl")

    def plot_error_vs_distance(
        self,
        data: pd.DataFrame,
        output_path: str = "error_vs_distance.png",
        title: str = "Translation Chain Semantic Degradation Analysis",
        dpi: int = 300,
        add_trendline: bool = True,
    ) -> Path:
        """
        Generate error rate vs. distance plot.

        Args:
            data: DataFrame with 'error_rate' and 'distance' columns
            output_path: Path to save the graph
            title: Graph title
            dpi: Image resolution (dots per inch)
            add_trendline: Whether to add polynomial trendline

        Returns:
            Path to saved graph file

        Raises:
            ValueError: If required columns are missing
        """
        if 'error_rate' not in data.columns or 'distance' not in data.columns:
            raise ValueError("DataFrame must contain 'error_rate' and 'distance' columns")

        self.logger.info(f"Generating error vs distance plot: {output_path}")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Convert error rate to percentage
        error_pct = data['error_rate'] * 100
        distances = data['distance']

        # Main plot
        ax.plot(error_pct, distances, 'o-', linewidth=2, markersize=10,
                color='#2E86AB', label='Measured Distance', zorder=3)

        # Add trend line if requested and enough points
        if add_trendline and len(data) >= 3:
            z = np.polyfit(error_pct, distances, 2)
            p = np.poly1d(z)
            x_trend = np.linspace(error_pct.min(), error_pct.max(), 100)
            ax.plot(x_trend, p(x_trend), '--',
                   label='Polynomial Fit', color='#A23B72', alpha=0.7, zorder=2)

        # Labels and styling
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=13)
        ax.set_ylabel('Semantic Distance (Cosine)', fontsize=13)
        ax.set_title(title, fontsize=15, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, zorder=1)

        plt.tight_layout()

        # Save figure
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

        self.logger.info(f"Graph saved: {output_file}")

        return output_file

    def plot_multiple_metrics(
        self,
        data: pd.DataFrame,
        metrics: List[str],
        output_path: str = "multi_metrics.png",
        title: str = "Translation Quality Metrics Comparison",
        dpi: int = 300,
    ) -> Path:
        """
        Plot multiple distance metrics on the same graph.

        Args:
            data: DataFrame with 'error_rate' and metric columns
            metrics: List of metric column names to plot
            output_path: Path to save the graph
            title: Graph title
            dpi: Image resolution

        Returns:
            Path to saved graph file
        """
        self.logger.info(f"Generating multi-metric plot: {output_path}")

        fig, ax = plt.subplots(figsize=(12, 7))

        error_pct = data['error_rate'] * 100

        # Plot each metric
        for metric in metrics:
            if metric in data.columns:
                ax.plot(error_pct, data[metric], 'o-', linewidth=2,
                       markersize=8, label=metric.replace('_', ' ').title())

        # Labels and styling
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=13)
        ax.set_ylabel('Distance Value', fontsize=13)
        ax.set_title(title, fontsize=15, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save figure
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

        self.logger.info(f"Graph saved: {output_file}")

        return output_file

    def plot_with_confidence_intervals(
        self,
        data: pd.DataFrame,
        output_path: str = "error_vs_distance_ci.png",
        confidence: float = 0.95,
        dpi: int = 300,
    ) -> Path:
        """
        Plot error vs distance with confidence intervals.

        Args:
            data: DataFrame with multiple runs per error rate
            output_path: Path to save the graph
            confidence: Confidence level (0-1)
            dpi: Image resolution

        Returns:
            Path to saved graph file
        """
        self.logger.info(f"Generating plot with confidence intervals: {output_path}")

        # Group by error rate and calculate statistics
        grouped = data.groupby('error_rate')['distance'].agg(['mean', 'std', 'count'])
        error_pct = grouped.index * 100

        # Calculate confidence interval
        from scipy import stats
        ci = grouped.apply(
            lambda row: stats.t.interval(
                confidence,
                row['count'] - 1,
                loc=row['mean'],
                scale=row['std'] / np.sqrt(row['count'])
            ) if row['count'] > 1 else (row['mean'], row['mean']),
            axis=1
        )

        ci_lower = [c[0] for c in ci]
        ci_upper = [c[1] for c in ci]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot mean with confidence interval
        ax.plot(error_pct, grouped['mean'], 'o-', linewidth=2,
               markersize=10, color='#2E86AB', label='Mean Distance')
        ax.fill_between(error_pct, ci_lower, ci_upper,
                        alpha=0.3, color='#2E86AB',
                        label=f'{int(confidence*100)}% CI')

        # Labels and styling
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=13)
        ax.set_ylabel('Semantic Distance (Cosine)', fontsize=13)
        ax.set_title('Translation Degradation with Confidence Intervals',
                    fontsize=15, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save figure
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

        self.logger.info(f"Graph saved: {output_file}")

        return output_file

    def create_summary_dashboard(
        self,
        data: pd.DataFrame,
        output_path: str = "summary_dashboard.png",
        dpi: int = 300,
    ) -> Path:
        """
        Create a dashboard with multiple visualizations.

        Args:
            data: DataFrame with experiment results
            output_path: Path to save the dashboard
            dpi: Image resolution

        Returns:
            Path to saved dashboard file
        """
        self.logger.info(f"Generating summary dashboard: {output_path}")

        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Error vs Distance
        ax1 = fig.add_subplot(gs[0, 0])
        error_pct = data['error_rate'] * 100
        ax1.plot(error_pct, data['distance'], 'o-', linewidth=2, markersize=8)
        ax1.set_xlabel('Error Rate (%)')
        ax1.set_ylabel('Distance')
        ax1.set_title('Error Rate vs Distance')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Distribution of distances
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(data['distance'], bins=15, edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Distance')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distance Distribution')
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Change in distance
        ax3 = fig.add_subplot(gs[1, 0])
        changes = data['distance'].diff()
        ax3.bar(range(1, len(changes)), changes[1:], edgecolor='black', alpha=0.7)
        ax3.set_xlabel('Step')
        ax3.set_ylabel('Change in Distance')
        ax3.set_title('Distance Change Between Error Rates')
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: Statistics summary (text)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')

        stats_text = f"""
        SUMMARY STATISTICS

        Sample Size: {len(data)}
        Error Rates: {data['error_rate'].min()*100:.0f}% - {data['error_rate'].max()*100:.0f}%

        Distance Metrics:
          Min: {data['distance'].min():.4f}
          Max: {data['distance'].max():.4f}
          Mean: {data['distance'].mean():.4f}
          Std: {data['distance'].std():.4f}

        Degradation:
          Total: {data['distance'].iloc[-1] - data['distance'].iloc[0]:.4f}
          Per 10%: {(data['distance'].iloc[-1] - data['distance'].iloc[0]) / (len(data)-1) if len(data) > 1 else 0:.4f}
        """

        ax4.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center')

        fig.suptitle('Translation Chain Experiment Dashboard', fontsize=16, fontweight='bold')

        # Save figure
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

        self.logger.info(f"Dashboard saved: {output_file}")

        return output_file
