# Translation Quality Analysis Pipeline

Multi-Step Agent System for Translation Quality Analysis through error-injected translation chains.

## 📋 Overview

This system measures how spelling errors affect translation quality through a three-stage translation chain (EN→FR→HE→EN). It uses SKILL-based agents with Claude Code for translations and Python for automation, metrics calculation, and visualization.

### Translation Chain

```
Original English (with errors)
       ↓
   [Agent 1] English → French (with error correction)
       ↓
   [Agent 2] French → Hebrew (semantic translation)
       ↓
   [Agent 3] Hebrew → English (final translation)
       ↓
Final English → Vector Distance Calculation
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd "llm with agents/HW3"

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp example.env .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Configure API Keys

Edit `.env` file:
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 3. Run Your First Experiment

```bash
# Prepare experiment with error injection
python src/main.py prepare "The quick brown fox jumps over the lazy dog while the sun shines brightly"

# Follow the generated prompts in results/exp_*/agent_prompts.txt
# Record agent outputs in results/exp_*/results_template.json

# Analyze results and generate graphs
python src/main.py analyze results/exp_*/results.json
```

## 📂 Project Structure

```
HW3/
├── agents/                           # SKILL-based agents for Claude Code
│   ├── agent-en-to-fr/              # English → French translator
│   ├── agent-fr-to-he/              # French → Hebrew translator
│   ├── agent-he-to-en/              # Hebrew → English translator
│   ├── translation-chain-orchestrator/  # Workflow coordinator
│   └── translation-metrics-analyzer/    # Metrics calculator
│       └── scripts/
│           └── calculate_metrics.py     # Standalone metrics script
├── src/                             # Python support modules
│   ├── main.py                      # Main CLI interface
│   ├── error_injection/             # Error injection strategies
│   ├── metrics/                     # Embeddings & distance calculation
│   ├── pipeline/                    # Workflow orchestration
│   ├── utils/                       # Config, logging, cost tracking
│   └── visualization/               # Graph generation
├── scripts/
│   └── run_experiment.py            # Automated experiment preparation
├── data/
│   └── input/
│       └── sentences.json           # Sample sentences
├── docs/
│   ├── PRD.md                       # Product Requirements Document
│   ├── ARCHITECTURE.md              # Architecture Document
│   ├── QUICK_START.md               # Quick start guide
│   └── ADRs/                        # Architecture Decision Records
├── .env                             # Configuration (create from example.env)
├── example.env                      # Configuration template
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🎯 System Components

### SKILL-Based Agents

The translation agents are defined as SKILL files that work with Claude Code:

1. **agent-en-to-fr**: Translates English to French with error correction
2. **agent-fr-to-he**: Translates French to Hebrew with semantic preservation
3. **agent-he-to-en**: Translates Hebrew back to English
4. **translation-chain-orchestrator**: Manages the complete workflow
5. **translation-metrics-analyzer**: Calculates embeddings and distances

### Python Modules

Supporting automation and analysis:

- **Error Injection**: Multiple strategies (substitution, deletion, transposition, insertion)
- **Metrics Calculation**: Sentence embeddings and vector distances
- **Visualization**: Publication-quality graphs
- **Pipeline Orchestration**: Workflow management
- **Cost Tracking**: Token usage and API cost monitoring

## 💻 CLI Commands

### Prepare Experiment

```bash
python src/main.py prepare "Your sentence here" \
    --error-rates 0,10,25,35,50 \
    --output-dir ./results \
    --seed 42
```

**Output:**
- `experiment_config.json` - Experiment configuration
- `agent_prompts.txt` - Ready-to-use prompts for Claude Code
- `results_template.json` - Template for recording agent outputs

### Analyze Results

```bash
python src/main.py analyze results/exp_*/results.json
```

**Output:**
- `metrics_output.csv` - Distance metrics for all error rates
- `error_vs_distance.png` - Visualization graph
- Console summary with statistics

### Visualize Metrics

```bash
python src/main.py visualize results/exp_*/metrics_output.csv \
    --output custom_graph.png \
    --dpi 300
```

### System Information

```bash
python src/main.py info
```

## 🔬 Running Experiments

### Complete Workflow

#### Step 1: Prepare

```bash
python src/main.py prepare "The artificial intelligence system processes natural language with remarkable accuracy"
```

This generates misspelled versions with different error rates.

#### Step 2: Execute Translation Chain

Open the generated `agent_prompts.txt` and run each agent:

```bash
# Agent 1: EN→FR
claude-code "Translate to French: Teh artifical inteligence sistem..."

# Agent 2: FR→HE
claude-code "Translate to Hebrew: [French output]"

# Agent 3: HE→EN
claude-code "Translate to English: [Hebrew output]"
```

#### Step 3: Record Results

Fill in `results_template.json` with agent outputs:

```json
{
  "experiment_id": "exp_20251123_123456",
  "results": [
    {
      "error_rate": 0.0,
      "original": "The artificial intelligence system...",
      "final": "[Paste Agent 3 output]",
      "word_count": 10
    }
  ]
}
```

#### Step 4: Analyze

```bash
python src/main.py analyze results/exp_*/results.json
```

View the generated graph and metrics!

## 📊 Understanding Results

### Distance Metrics

**Cosine Distance** (Primary metric):
- **0.0**: Perfect semantic match
- **0.1-0.3**: High similarity (minor changes)
- **0.3-0.5**: Moderate similarity (noticeable drift)
- **0.5+**: Low similarity (significant degradation)

### Expected Patterns

- Distance increases with error rate
- Non-linear growth (accelerating degradation)
- Threshold effects at certain error levels

### Sample Output

```
METRICS SUMMARY
==============================================================

Error Rate | Distance | Change
--------------------------------------------------------------
     0%    |  0.0234  |   -
    10%    |  0.0456  | +0.0222
    25%    |  0.1123  | +0.0667
    50%    |  0.2789  | +0.1666

Total degradation: 0.2555
Average per step: 0.0852
```

## 🛠️ Advanced Usage

### Using Alternative Scripts

The project includes standalone scripts for flexibility:

```bash
# Automated experiment preparation with error injection
python scripts/run_experiment.py "Your sentence" \
    --error-rates 0 0.1 0.2 0.25 0.3 0.4 0.5 \
    --output-dir experiment_output

# Direct metrics calculation
python agents/translation-metrics-analyzer/scripts/calculate_metrics.py \
    results.json \
    --output-dir output
```

### Custom Error Injection

```python
from src.error_injection import ErrorInjector

injector = ErrorInjector(random_seed=42)
misspelled = injector.inject("Your text", error_rate=0.25)
```

### Custom Metrics

```python
from src.metrics import Embedder, VectorMetrics

embedder = Embedder(model_name="all-MiniLM-L6-v2")
metrics = VectorMetrics(embedder)

distance = metrics.calculate_distance(text1, text2, metric="cosine")
```

## 🔧 Configuration

Edit `.env` file for customization:

```bash
# Translation model
TRANSLATION_MODEL=claude-3-5-sonnet-20250929

# Embedding model (local)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Or use OpenAI embeddings
USE_OPENAI_EMBEDDINGS=false
# OPENAI_API_KEY=your-key

# Experiment settings
DEFAULT_ERROR_RATES=0,10,25,35,50
RANDOM_SEED=42

# Performance
MAX_RETRIES=3
TIMEOUT_SECONDS=30
CACHE_ENABLED=true

# Output
GRAPH_DPI=300
LOG_LEVEL=INFO
```

## 📚 Documentation

- **[PRD.md](PRD.md)** - Complete requirements and specifications
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[QUICK_START.md](docs/QUICK_START.md)** - Quick start guide
- **[Agent SKILL files](agents/)** - Individual agent documentation

## 🎓 Academic Requirements

This system fulfills all M.Sc. project requirements:

✅ Multi-agent translation chain (EN→FR→HE→EN)
✅ Error injection (0% to 50% spelling errors)
✅ Vector distance calculation with embeddings
✅ Visualization graphs (error rate vs. distance)
✅ Cost tracking and prompt engineering log
✅ Comprehensive documentation (PRD, Architecture, ADRs)
✅ Modular architecture with 70%+ test coverage capability
✅ Professional code quality with docstrings

## 🐛 Troubleshooting

### Hebrew Text Not Displaying

```bash
export LANG=en_US.UTF-8
```

### Import Errors

```bash
pip install -r requirements.txt
```

### API Errors

Check your `.env` file has valid `ANTHROPIC_API_KEY`.

### Embeddings Slow

Use GPU if available or switch to smaller model:
```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Faster, smaller
```

## 📈 Performance

- **Translation**: ~2-4 seconds per agent call
- **Error Injection**: <1 second
- **Embeddings**: ~0.5 seconds per text (CPU)
- **Full Experiment**: ~15 minutes for 7 error rates

## 🔒 Security

- API keys stored in `.env` (not in git)
- Input validation on all boundaries
- No secrets logged
- Secure credential handling

## 📝 License

Academic project for M.Sc. Computer Science coursework.

## 🤝 Support

For issues or questions:
1. Check [QUICK_START.md](docs/QUICK_START.md)
2. Review agent SKILL.md files
3. Check PRD.md for requirements
4. Review error logs in `logs/`

## 🎉 Getting Started Now

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp example.env .env
nano .env  # Add your ANTHROPIC_API_KEY

# 3. Run quick start
python src/main.py info

# 4. Prepare your first experiment
python src/main.py prepare "The quick brown fox jumps over the lazy dog while the sun shines"
```

Follow the generated instructions and you'll have results in 15 minutes!

---

**Created**: 2025-11-23
**Version**: 1.0
**For**: M.Sc. Computer Science - LLM with Agents Course
