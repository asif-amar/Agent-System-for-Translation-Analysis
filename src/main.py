#!/usr/bin/env python3
"""
Translation Quality Analysis Pipeline - Main CLI

This is the main command-line interface for running translation chain experiments,
calculating metrics, and generating visualizations.

Usage:
    python src/main.py prepare "Your sentence here"
    python src/main.py analyze results/exp_*/results.json
    python src/main.py visualize results/exp_*/metrics.csv
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Optional

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from metrics import Embedder, VectorMetrics
from visualization import GraphPlotter
from pipeline import TranslationPipeline
from utils import Config, setup_logging, CostTracker


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), help='Log file path')
@click.pass_context
def cli(ctx, verbose, log_file):
    """Translation Quality Analysis Pipeline CLI"""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level=log_level, log_file=log_file)

    # Store config in context
    ctx.ensure_object(dict)
    try:
        ctx.obj['config'] = Config()
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        click.echo("Please check your .env file or set required environment variables", err=True)
        sys.exit(1)


@cli.command()
@click.argument('sentences_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./results',
              help='Output directory for experiment files')
@click.pass_context
def prepare(ctx, sentences_file, output_dir):
    """
    Prepare experiment from pre-corrupted sentences file.

    This command:
    1. Loads sentences with different error rates from JSON file
    2. Creates experiment configuration
    3. Generates ready-to-use agent prompts
    4. Creates results template

    Example:
        python src/main.py prepare data/input/sentences.json
    """
    import json

    click.echo(f"\n{'='*70}")
    click.echo("PREPARING TRANSLATION CHAIN EXPERIMENT")
    click.echo(f"{'='*70}\n")

    # Load sentences from file
    click.echo(f"Loading sentences from: {sentences_file}")
    with open(sentences_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'sentences' in data:
        sentences_list = data['sentences']
    else:
        sentences_list = data if isinstance(data, list) else [data]

    click.echo(f"Loaded {len(sentences_list)} test cases\n")

    # Initialize pipeline
    pipeline = TranslationPipeline(output_dir=output_dir)

    # Prepare experiment data from pre-corrupted sentences
    click.echo("Preparing experiment files...")

    # Extract data from sentences
    test_cases = []
    for item in sentences_list:
        original = item.get('original', item.get('text', ''))
        misspelled = item.get('misspelled', item.get('corrupted', original))
        error_rate = item.get('error_rate', 0.0)

        test_cases.append({
            'original': original,
            'misspelled': misspelled,
            'error_rate': error_rate,
            'word_count': len(original.split())
        })

        click.echo(f"  {error_rate*100:>5.0f}% error: {misspelled[:60]}...")

    # Create experiment configuration
    experiment_data = {
        "experiment_id": pipeline.experiment_id,
        "timestamp": ctx.obj.get('timestamp', ''),
        "test_cases": test_cases
    }

    # Save configuration
    import json
    from pathlib import Path
    config_file = pipeline.output_dir / "experiment_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(experiment_data, f, indent=2, ensure_ascii=False)

    # Generate agent prompts
    prompts_file = pipeline.generate_agent_prompts(experiment_data)

    # Create results template
    template_file = pipeline.create_results_template(experiment_data)

    click.echo(f"\n{'='*70}")
    click.echo("EXPERIMENT PREPARATION COMPLETE")
    click.echo(f"{'='*70}\n")

    click.echo(f"Experiment ID: {pipeline.experiment_id}")
    click.echo(f"Output directory: {pipeline.output_dir.absolute()}\n")

    click.echo("Generated files:")
    click.echo(f"  ✓ experiment_config.json - Experiment configuration")
    click.echo(f"  ✓ agent_prompts.txt - Ready-to-use prompts")
    click.echo(f"  ✓ results_template.json - Template for recording outputs\n")

    click.echo("Next steps:")
    click.echo("  1. Open agent_prompts.txt")
    click.echo("  2. Run each prompt with Claude Code or manually")
    click.echo("  3. Fill in results_template.json with agent outputs")
    click.echo("  4. Rename to results.json")
    click.echo(f"  5. Run: python src/main.py analyze {pipeline.output_dir}/results.json\n")


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', help='Output directory (default: same as results file)')
@click.option('--embedding-model', help='Embedding model to use')
@click.pass_context
def analyze(ctx, results_file, output_dir, embedding_model):
    """
    Analyze translation results and calculate vector distances.

    This command:
    1. Loads translation results from JSON file
    2. Generates embeddings for original and final sentences
    3. Calculates distance metrics
    4. Saves metrics to CSV
    5. Generates visualization graph

    Example:
        python src/main.py analyze results/exp_20251123_123456/results.json
    """
    config = ctx.obj['config']

    results_path = Path(results_file)
    if output_dir is None:
        output_dir = results_path.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"\n{'='*70}")
    click.echo("ANALYZING TRANSLATION RESULTS")
    click.echo(f"{'='*70}\n")

    # Load results
    click.echo(f"Loading results from: {results_path}")
    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data.get('results', data) if isinstance(data, dict) else data
    click.echo(f"Loaded {len(results)} result entries\n")

    # Initialize embedder
    model = embedding_model or config.embedding_model
    click.echo(f"Loading embedding model: {model}")

    embedder = Embedder(
        model_name=model,
        use_openai=config.use_openai_embeddings,
        openai_api_key=config.openai_api_key if config.use_openai_embeddings else None
    )

    # Initialize metrics calculator
    metrics_calc = VectorMetrics(embedder)

    # Calculate metrics for each result
    click.echo("\nCalculating vector distances...")

    import pandas as pd
    metrics_data = []

    for i, result in enumerate(results, 1):
        click.echo(f"  Processing result {i}/{len(results)}...", nl=False)

        original = result['original']
        final = result['final']
        error_rate = result['error_rate']

        # Calculate all metrics
        metrics = metrics_calc.calculate_all_metrics(original, final)

        metrics_data.append({
            'error_rate': error_rate,
            'cosine_distance': metrics['cosine_distance'],
            'cosine_similarity': metrics['cosine_similarity'],
            'euclidean_distance': metrics['euclidean_distance'],
            'manhattan_distance': metrics['manhattan_distance'],
            'original': original,
            'final': final,
            'word_count': result.get('word_count', len(original.split()))
        })

        click.echo(f" Distance: {metrics['cosine_distance']:.4f}")

    # Create DataFrame
    df = pd.DataFrame(metrics_data).sort_values('error_rate')

    # Save metrics
    metrics_file = output_dir / 'metrics_output.csv'
    df.to_csv(metrics_file, index=False)
    click.echo(f"\n✓ Metrics saved: {metrics_file}")

    # Print summary
    click.echo(f"\n{'='*70}")
    click.echo("METRICS SUMMARY")
    click.echo(f"{'='*70}\n")

    click.echo(f"{'Error Rate':<12} | {'Distance':<10} | {'Change':<10}")
    click.echo("-" * 70)

    prev_dist = None
    for _, row in df.iterrows():
        err_pct = row['error_rate'] * 100
        dist = row['cosine_distance']
        change = f"+{dist - prev_dist:.4f}" if prev_dist is not None else "-"
        click.echo(f"{err_pct:>6.0f}%      | {dist:>8.4f}  | {change:>10}")
        prev_dist = dist

    click.echo(f"\nTotal degradation: {df['cosine_distance'].iloc[-1] - df['cosine_distance'].iloc[0]:.4f}")
    click.echo(f"Average per step: {(df['cosine_distance'].iloc[-1] - df['cosine_distance'].iloc[0]) / (len(df) - 1):.4f}")

    # Generate visualization
    click.echo(f"\n{'='*70}")
    click.echo("GENERATING VISUALIZATION")
    click.echo(f"{'='*70}\n")

    plotter = GraphPlotter()
    graph_file = output_dir / 'error_vs_distance.png'

    # Add 'distance' column for plotter (use cosine_distance)
    df_plot = df.copy()
    df_plot['distance'] = df['cosine_distance']

    plotter.plot_error_vs_distance(
        data=df_plot,
        output_path=str(graph_file),
        dpi=300
    )

    click.echo(f"✓ Graph saved: {graph_file}\n")

    click.echo("Analysis complete! Files generated:")
    click.echo(f"  - {metrics_file.name}")
    click.echo(f"  - {graph_file.name}\n")


@cli.command()
@click.argument('metrics_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output image path')
@click.option('--dpi', default=300, help='Image resolution (DPI)')
@click.option('--title', help='Graph title')
def visualize(metrics_file, output, dpi, title):
    """
    Generate visualization from metrics CSV file.

    Example:
        python src/main.py visualize results/exp_*/metrics_output.csv
    """
    import pandas as pd

    click.echo(f"\nLoading metrics from: {metrics_file}")
    df = pd.read_csv(metrics_file)

    if output is None:
        output = Path(metrics_file).parent / 'error_vs_distance.png'

    click.echo(f"Generating graph: {output}")

    plotter = GraphPlotter()
    plotter.plot_error_vs_distance(
        data=df,
        output_path=str(output),
        title=title or "Translation Chain Semantic Degradation Analysis",
        dpi=dpi
    )

    click.echo(f"✓ Graph saved: {output}\n")


@cli.command()
@click.argument('sentences_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./results',
              help='Output directory')
@click.pass_context
def quick_start(ctx, sentences_file, output_dir):
    """
    Quick start: Prepare experiment and show next steps.

    This is a simplified command that prepares everything you need
    to run an experiment from a pre-corrupted sentences file.

    Example:
        python src/main.py quick-start data/input/sentences.json
    """
    # Call prepare command
    ctx.invoke(prepare, sentences_file=sentences_file, output_dir=output_dir)


@cli.command()
def info():
    """Display system information and configuration."""
    try:
        config = Config()

        click.echo("\n" + "="*70)
        click.echo("TRANSLATION QUALITY ANALYSIS PIPELINE")
        click.echo("="*70 + "\n")

        click.echo("Configuration:")
        click.echo(f"  Translation Model: {config.translation_model}")
        click.echo(f"  Embedding Model: {config.embedding_model}")
        click.echo(f"  Use OpenAI Embeddings: {config.use_openai_embeddings}")
        click.echo(f"  Default Error Rates: {', '.join(f'{int(r*100)}%' for r in config.default_error_rates)}")
        click.echo(f"  Random Seed: {config.random_seed}")
        click.echo(f"  Max Retries: {config.max_retries}")
        click.echo(f"  Timeout: {config.timeout_seconds}s")
        click.echo(f"  Cache Enabled: {config.cache_enabled}\n")

        click.echo("Available Commands:")
        click.echo("  prepare   - Prepare experiment with error injection")
        click.echo("  analyze   - Analyze results and calculate metrics")
        click.echo("  visualize - Generate graphs from metrics")
        click.echo("  info      - Show this information\n")

        click.echo("Agents Directory: ./agents/")
        agents_dir = Path("./agents")
        if agents_dir.exists():
            agents = [d.name for d in agents_dir.iterdir() if d.is_dir()]
            for agent in agents:
                click.echo(f"  ✓ {agent}")
        click.echo()

    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        click.echo("\nPlease create a .env file with required configuration.", err=True)
        click.echo("See example.env for template.\n", err=True)


if __name__ == '__main__':
    cli(obj={})
