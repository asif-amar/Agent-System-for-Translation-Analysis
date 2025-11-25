"""
Results comparison and analysis module.

Provides detailed comparison views for translation results.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd


logger = logging.getLogger(__name__)


class ResultsAnalyzer:
    """
    Analyze and compare translation results.

    This class provides methods for detailed analysis
    and side-by-side comparison of translations.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_comparison_dataframe(
        self,
        results: Dict
    ) -> pd.DataFrame:
        """
        Create DataFrame for side-by-side comparison.

        Args:
            results: Results dictionary from experiment

        Returns:
            DataFrame with comparison data
        """
        comparison_data = []

        for result in results.get('results', []):
            comparison_data.append({
                'id': result.get('id', 'N/A'),
                'error_rate': result['error_rate'] * 100,
                'original': result['original'],
                'misspelled': result.get('misspelled', result['original']),
                'french': result.get('french', 'N/A'),
                'hebrew': result.get('hebrew', 'N/A'),
                'final': result.get('final', 'N/A'),
                'word_count': result.get('word_count', len(result['original'].split()))
            })

        return pd.DataFrame(comparison_data)

    def calculate_text_changes(
        self,
        original: str,
        final: str
    ) -> Dict:
        """
        Calculate changes between original and final text.

        Args:
            original: Original text
            final: Final translated text

        Returns:
            Dictionary with change statistics
        """
        original_words = original.split()
        final_words = final.split()

        # Simple word-level comparison
        original_set = set(original_words)
        final_set = set(final_words)

        common_words = original_set.intersection(final_set)
        added_words = final_set - original_set
        removed_words = original_set - final_set

        return {
            'original_word_count': len(original_words),
            'final_word_count': len(final_words),
            'common_words': len(common_words),
            'added_words': len(added_words),
            'removed_words': len(removed_words),
            'word_retention_rate': len(common_words) / len(original_words) if original_words else 0
        }

    def get_error_level_statistics(
        self,
        df: pd.DataFrame,
        error_level: float
    ) -> Dict:
        """
        Get statistics for specific error level.

        Args:
            df: DataFrame with results and metrics
            error_level: Error rate to filter (0.0 to 0.5)

        Returns:
            Dictionary with statistics for that error level
        """
        filtered = df[df['error_rate'] == error_level * 100]

        if filtered.empty:
            return {'error': 'No data for this error level'}

        row = filtered.iloc[0]

        stats = {
            'error_rate': error_level,
            'original_text': row.get('original', 'N/A'),
            'misspelled_text': row.get('misspelled', 'N/A'),
            'final_text': row.get('final', 'N/A'),
            'word_count': row.get('word_count', 0)
        }

        # Add metrics if available
        metric_columns = [
            'cosine_distance', 'cosine_similarity',
            'euclidean_distance', 'manhattan_distance'
        ]

        for col in metric_columns:
            if col in row:
                stats[col] = row[col]

        return stats

    def compare_metrics_across_levels(
        self,
        df: pd.DataFrame,
        metric: str = 'cosine_distance'
    ) -> pd.DataFrame:
        """
        Compare metric values across error levels.

        Args:
            df: DataFrame with metrics
            metric: Metric to compare

        Returns:
            DataFrame with comparison statistics
        """
        if metric not in df.columns:
            raise ValueError(f"Metric '{metric}' not found in data")

        comparison = df[['error_rate', metric]].copy()
        comparison['change'] = comparison[metric].diff()
        comparison['percent_change'] = (
            comparison['change'] / comparison[metric].shift(1) * 100
        )

        return comparison

    def generate_summary_report(
        self,
        results: Dict,
        metrics_df: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Generate comprehensive summary report.

        Args:
            results: Results dictionary
            metrics_df: Optional metrics DataFrame

        Returns:
            Dictionary with summary information
        """
        result_list = results.get('results', [])

        summary = {
            'experiment_id': results.get('experiment_id', 'unknown'),
            'timestamp': results.get('timestamp', 'unknown'),
            'mode': results.get('mode', 'unknown'),
            'input_file': results.get('input_file', 'unknown'),
            'description': results.get('description', ''),
            'total_sentences': len(result_list),
            'error_rates': sorted(set(r['error_rate'] for r in result_list))
        }

        if metrics_df is not None and not metrics_df.empty:
            summary['metrics'] = {
                'min_distance': metrics_df['cosine_distance'].min() if 'cosine_distance' in metrics_df.columns else None,
                'max_distance': metrics_df['cosine_distance'].max() if 'cosine_distance' in metrics_df.columns else None,
                'mean_distance': metrics_df['cosine_distance'].mean() if 'cosine_distance' in metrics_df.columns else None,
                'total_degradation': (
                    metrics_df['cosine_distance'].iloc[-1] - metrics_df['cosine_distance'].iloc[0]
                    if 'cosine_distance' in metrics_df.columns and len(metrics_df) > 1
                    else None
                )
            }

        return summary

    def filter_by_error_range(
        self,
        df: pd.DataFrame,
        min_error: float,
        max_error: float
    ) -> pd.DataFrame:
        """
        Filter results by error rate range.

        Args:
            df: DataFrame with results
            min_error: Minimum error rate (0.0 to 0.5)
            max_error: Maximum error rate (0.0 to 0.5)

        Returns:
            Filtered DataFrame
        """
        min_pct = min_error * 100
        max_pct = max_error * 100

        return df[(df['error_rate'] >= min_pct) & (df['error_rate'] <= max_pct)]
