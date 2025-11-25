# Translation Quality Analysis System - UI Guide

## Overview

The Translation Quality Analysis System provides a comprehensive web-based interface built with Streamlit for running experiments, analyzing results, and visualizing translation quality degradation.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Features](#features)
5. [Workflows](#workflows)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment:**

Create a `.env` file based on `example.env`:

```bash
cp example.env .env
```

Edit `.env` and add your API keys:

```
ANTHROPIC_API_KEY=your_key_here
```

## Getting Started

### Launch the UI

Run the Streamlit application:

```bash
streamlit run src/ui/app.py
```

The interface will open in your default browser at `http://localhost:8501`

### Quick Start

1. Navigate to the **Home** page for system overview
2. Go to **Run Experiment** to prepare a new experiment
3. Use **Analyze Results** to calculate metrics
4. Explore **Visualize Data** for interactive charts
5. Compare translations in **Compare Translations**

## User Interface Overview

### Navigation

The sidebar provides navigation between five main pages:

- **Home**: System overview and quick actions
- **Run Experiment**: Prepare and execute experiments
- **Analyze Results**: Calculate semantic distance metrics
- **Visualize Data**: Interactive charts and graphs
- **Compare Translations**: Side-by-side text comparison

### Layout

The UI follows a **wide layout** design for optimal data presentation:

- **Header**: Page title and description
- **Content Area**: Main content with forms, tables, and visualizations
- **Sidebar**: Navigation and system information
- **Status Messages**: Success/error/warning messages

## Features

### 1. Home Page

**Purpose**: System overview and quick access

**Features**:
- System statistics (datasets, results, metrics)
- Available datasets list with expandable details
- Recent experiment results
- Quick action buttons
- Project information

**Key Metrics Displayed**:
- Number of available datasets
- Number of experiment results
- Supported distance metrics

### 2. Run Experiment Page

**Purpose**: Prepare and execute translation chain experiments

**Features**:
- Dataset selection from available input files
- Dataset preview with sample sentences
- Output location configuration
- Experiment preparation
- Agent prompts generation
- Results template creation

**Workflow**:
1. Select input dataset
2. Preview dataset contents
3. Configure output location
4. Choose execution mode
5. Click "Prepare Experiment"
6. Download agent prompts
7. Execute translations manually or with agents
8. Fill results template

**Generated Files**:
- `experiment_config.json`: Experiment configuration
- `agent_prompts.txt`: Ready-to-use translation prompts
- `results_template.json`: Template for recording outputs

### 3. Analyze Results Page

**Purpose**: Load results and calculate semantic distance metrics

**Features**:
- Results file selection
- Results preview and validation
- Embedding model selection
- Metric calculation (Cosine, Euclidean, Manhattan)
- Progress tracking
- Summary statistics
- Metrics table display
- CSV export

**Metrics Calculated**:
- **Cosine Distance**: Semantic similarity (0-2)
- **Cosine Similarity**: Directional similarity (-1 to 1)
- **Euclidean Distance**: L2 distance
- **Manhattan Distance**: L1 distance

**Workflow**:
1. Select results file from dropdown
2. Preview results summary
3. Choose embedding model (optional)
4. Click "Run Analysis"
5. View generated metrics
6. Download metrics CSV

### 4. Visualize Data Page

**Purpose**: Interactive visualization of experiment results

**Features**:
- Multiple chart types
- Interactive Plotly charts
- Metric selection
- Static graph display
- Export capabilities

**Chart Types**:

#### Error Rate vs Distance
- Line plot with markers
- Polynomial trendline
- Hover tooltips
- Summary statistics

#### Multiple Metrics Comparison
- Multi-line chart
- Unified hover
- Comparison table at key error rates
- Legend

#### Distance Distribution
- Histogram
- Bin customization
- Statistical summary (mean, median, std, range)

#### Comprehensive Dashboard
- 4-panel layout
- Error vs Distance plot
- Distribution histogram
- Change in distance bar chart
- Statistics table

**Static Visualizations**:
- Matplotlib-generated publication-quality graphs
- High-resolution (300 DPI)
- Embedded image display

### 5. Compare Translations Page

**Purpose**: Detailed side-by-side comparison of translations

**Features**:
- Translation chain viewing
- Error rate filtering
- Multiple view types
- Text change analysis
- Metrics integration

**View Types**:

#### Detailed Comparison
- Tabbed interface for each translation stage
- Original → Misspelled → French → Hebrew → Final
- Word count display
- Change statistics
- Distance metrics (if available)

#### Summary Table
- Tabular view of all results
- Sortable columns
- CSV export
- Quick overview

#### Text Changes Analysis
- Word-level change tracking
- Common/added/removed words
- Retention rate calculation
- Change visualization
- Statistical summary

**Filtering Options**:
- Minimum error rate slider (0-50%)
- Maximum error rate slider (0-50%)
- Dynamic result count

## Workflows

### Complete Experiment Workflow

#### Step 1: Prepare Experiment

1. Go to **Run Experiment** page
2. Select dataset: `data/input/sanity_check.json`
3. Review dataset preview
4. Click "Prepare Experiment"
5. Download `agent_prompts.txt`

#### Step 2: Execute Translations

**Option A: Manual Execution**
1. Open each SKILL agent in Claude
2. Run prompts from `agent_prompts.txt`
3. Record outputs in `results_template.json`

**Option B: Automated Execution**
1. Use existing `run_experiment.sh` script
2. Results saved automatically

#### Step 3: Analyze Results

1. Go to **Analyze Results** page
2. Select your results file
3. Choose embedding model (default: all-MiniLM-L6-v2)
4. Click "Run Analysis"
5. Wait for completion
6. Review metrics summary

#### Step 4: Visualize Data

1. Go to **Visualize Data** page
2. Select analyzed dataset
3. Choose chart type: "Error Rate vs Distance"
4. Select metric: "Cosine Distance"
5. Explore interactive chart
6. Try other visualizations

#### Step 5: Compare Translations

1. Go to **Compare Translations** page
2. Select dataset
3. Choose view: "Detailed Comparison"
4. Adjust error rate filters
5. Review translation chain
6. Analyze text changes

### Analysis-Only Workflow

If you already have experiment results:

1. Go to **Analyze Results**
2. Select existing results file
3. Run analysis
4. Proceed to visualization and comparison

### Visualization-Only Workflow

If metrics are already calculated:

1. Go to **Visualize Data**
2. Select dataset with metrics
3. Explore different chart types
4. Export visualizations if needed

## Troubleshooting

### Common Issues

#### UI Won't Start

**Problem**: Streamlit fails to start

**Solutions**:
- Check Python version: `python --version` (requires 3.11+)
- Verify installation: `pip list | grep streamlit`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check port availability: Try `streamlit run src/ui/app.py --server.port 8502`

#### No Datasets Found

**Problem**: "No input datasets found" message

**Solutions**:
- Verify files exist in `data/input/` directory
- Check JSON format (must have 'sentences' key)
- Ensure file permissions are correct
- Refresh page

#### No Results Found

**Problem**: "No experiment results found" message

**Solutions**:
- Check results directory structure: `results/YYYY-MM-DD/input_name/`
- Verify JSON format (must have 'results' key)
- Run an experiment first
- Check file naming: `results_YYYYMMDD_HHMMSS.json`

#### Analysis Fails

**Problem**: "Analysis failed" error

**Solutions**:
- Verify results file format
- Check Python path configuration
- Ensure embedding model can load
- Review error message in expanded output
- Check available memory for model loading

#### Metrics Don't Display

**Problem**: Calculated metrics don't show

**Solutions**:
- Verify `metrics_output.csv` exists in results directory
- Check CSV format
- Clear browser cache
- Refresh page
- Recalculate metrics

#### Visualizations Don't Render

**Problem**: Charts don't display

**Solutions**:
- Check browser console for errors
- Verify Plotly installation: `pip show plotly`
- Ensure metrics data is loaded
- Try different browser
- Update Plotly: `pip install --upgrade plotly`

### Performance Tips

1. **Large Datasets**: For datasets with >20 sentences, analysis may take several minutes
2. **Memory Usage**: Embedding models require 1-2GB RAM
3. **Caching**: Data is cached automatically; use "Recalculate" if data changes
4. **Browser**: Chrome/Firefox recommended for best performance
5. **Network**: Local execution only; no external data transmission

### Error Messages

#### "Invalid dataset format: missing 'sentences' key"

Input JSON must have this structure:
```json
{
  "sentences": [...],
  "metadata": {...}
}
```

#### "Invalid results format: missing 'results' key"

Results JSON must have:
```json
{
  "experiment_id": "...",
  "results": [...]
}
```

#### "Metric 'X' not found in data"

Metrics CSV must include all standard columns. Rerun analysis.

## Accessibility Features

The UI follows Nielsen's 10 Usability Heuristics:

1. **Visibility of System Status**: Progress bars and status messages
2. **Match System and Real World**: Clear, intuitive terminology
3. **User Control and Freedom**: Easy navigation, back buttons
4. **Consistency**: Uniform design across pages
5. **Error Prevention**: Validation and helpful warnings
6. **Recognition Over Recall**: Clear labels and tooltips
7. **Flexibility**: Multiple view types and filters
8. **Minimalist Design**: Clean, uncluttered interface
9. **Error Recovery**: Clear error messages with solutions
10. **Help**: This documentation and in-app tooltips

## Best Practices

1. **Organize Results**: Use descriptive experiment names
2. **Regular Backups**: Save important results
3. **Documentation**: Record experiment parameters
4. **Validation**: Always preview datasets before running
5. **Metrics**: Calculate metrics immediately after experiments
6. **Exploration**: Try different visualizations for insights
7. **Comparison**: Use filters to focus on specific error ranges

## Support

For issues or questions:

1. Check this documentation
2. Review error messages carefully
3. Check project README.md
4. Review source code comments
5. Check system logs: `logs/` directory

## Updates and Maintenance

The UI is actively maintained. Check for updates:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Last Updated**: 2025-11-25
**Version**: 1.0.0
