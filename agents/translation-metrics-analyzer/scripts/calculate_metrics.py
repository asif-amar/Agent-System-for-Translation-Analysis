#!/usr/bin/env python3
"""
Translation Chain Metrics Calculator

Calculates vector embeddings and distance metrics for translation experiments.
Generates analysis graphs showing relationship between error rates and semantic distance.

Usage:
    python calculate_metrics.py results.json
    python calculate_metrics.py results.csv --output-dir ./graphs
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not installed. Install with:")
    print("  pip install sentence-transformers scikit-learn")
    EMBEDDINGS_AVAILABLE = False


class TranslationMetricsAnalyzer:
    """Analyzes translation chain results and calculates metrics"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize with embedding model"""
        if not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("sentence-transformers package required")
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
    
    def calculate_distance(self, text1, text2, metric='cosine'):
        """
        Calculate distance between two texts
        
        Args:
            text1: First text
            text2: Second text
            metric: 'cosine', 'euclidean', or 'manhattan'
            
        Returns:
            Distance value
        """
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        
        if metric == 'cosine':
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            return 1 - similarity
        elif metric == 'euclidean':
            return np.linalg.norm(emb1 - emb2)
        elif metric == 'manhattan':
            return np.sum(np.abs(emb1 - emb2))
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def analyze_results(self, results_data):
        """
        Analyze translation results and calculate distances
        
        Args:
            results_data: List of dicts with 'original', 'final', 'error_rate'
            
        Returns:
            DataFrame with analysis results
        """
        print(f"\nAnalyzing {len(results_data)} translation results...")
        
        analysis = []
        for i, result in enumerate(results_data, 1):
            print(f"  Processing result {i}/{len(results_data)}...", end='\r')
            
            distance = self.calculate_distance(
                result['original'],
                result['final']
            )
            
            analysis.append({
                'error_rate': result['error_rate'],
                'distance': distance,
                'original': result['original'],
                'final': result['final'],
                'word_count': result.get('word_count', len(result['original'].split()))
            })
        
        print("\nAnalysis complete!")
        return pd.DataFrame(analysis).sort_values('error_rate')
    
    def generate_graph(self, df, output_path='error_vs_distance.png'):
        """
        Generate visualization of error rate vs distance
        
        Args:
            df: DataFrame with 'error_rate' and 'distance' columns
            output_path: Path to save graph
        """
        print(f"\nGenerating graph: {output_path}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Convert error rate to percentage
        error_pct = df['error_rate'] * 100
        distances = df['distance']
        
        # Main plot
        ax.plot(error_pct, distances, 'o-', linewidth=2, markersize=10,
                color='#2E86AB', label='Measured Distance')
        
        # Add trend line if enough points
        if len(df) >= 3:
            z = np.polyfit(error_pct, distances, 2)
            p = np.poly1d(z)
            x_trend = np.linspace(error_pct.min(), error_pct.max(), 100)
            ax.plot(x_trend, p(x_trend), '--', 
                   label='Polynomial Fit', color='#A23B72', alpha=0.7)
        
        # Labels and styling
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=13)
        ax.set_ylabel('Semantic Distance (Cosine)', fontsize=13)
        ax.set_title('Translation Chain Semantic Degradation Analysis', 
                    fontsize=15, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved: {output_path}")
        
        return fig
    
    def print_summary(self, df):
        """Print analysis summary statistics"""
        print("\n" + "="*60)
        print("TRANSLATION CHAIN METRICS ANALYSIS")
        print("="*60)
        
        print(f"\nEmbedding Model: all-MiniLM-L6-v2")
        print(f"Distance Metric: Cosine Distance")
        print(f"Sample Size: {len(df)} error rates")
        
        print("\nResults:")
        print("-" * 60)
        print(f"{'Error Rate':<12} | {'Distance':<10} | {'Change':<10}")
        print("-" * 60)
        
        prev_dist = None
        for _, row in df.iterrows():
            err_pct = row['error_rate'] * 100
            dist = row['distance']
            change = f"+{dist - prev_dist:.4f}" if prev_dist is not None else "-"
            print(f"{err_pct:>6.0f}%      | {dist:>8.4f}  | {change:>10}")
            prev_dist = dist
        
        # Statistics
        print("\nStatistics:")
        print("-" * 60)
        
        pearson_r, pearson_p = pearsonr(df['error_rate'], df['distance'])
        print(f"Pearson Correlation: {pearson_r:.3f} (p={pearson_p:.4f})")
        
        degradation = (df['distance'].iloc[-1] - df['distance'].iloc[0]) / (len(df) - 1)
        print(f"Average Degradation: {degradation:.4f} per step")
        
        print(f"Max Distance: {df['distance'].max():.4f} at {df['error_rate'].iloc[-1]*100:.0f}% errors")
        print(f"Min Distance: {df['distance'].min():.4f} at {df['error_rate'].iloc[0]*100:.0f}% errors")
        print("="*60 + "\n")


def load_results(file_path):
    """Load translation results from JSON or CSV"""
    path = Path(file_path)
    
    if path.suffix == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif path.suffix == '.csv':
        df = pd.read_csv(path)
        return df.to_dict('records')
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def main():
    parser = argparse.ArgumentParser(
        description='Calculate metrics for translation chain experiments'
    )
    parser.add_argument('results_file', help='Path to results JSON or CSV file')
    parser.add_argument('--output-dir', default='.', help='Output directory for graphs')
    parser.add_argument('--output-csv', help='Path to save metrics CSV')
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading results from: {args.results_file}")
    results = load_results(args.results_file)
    print(f"Loaded {len(results)} results")
    
    # Initialize analyzer
    analyzer = TranslationMetricsAnalyzer()
    
    # Analyze
    df = analyzer.analyze_results(results)
    
    # Print summary
    analyzer.print_summary(df)
    
    # Generate graph
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    graph_path = output_dir / 'error_vs_distance.png'
    analyzer.generate_graph(df, graph_path)
    
    # Save metrics
    if args.output_csv:
        csv_path = Path(args.output_csv)
    else:
        csv_path = output_dir / 'metrics_output.csv'
    
    df.to_csv(csv_path, index=False)
    print(f"Metrics saved: {csv_path}")
    
    print("\nAnalysis complete!")


if __name__ == '__main__':
    main()
