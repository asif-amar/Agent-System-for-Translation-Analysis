# 🚀 Quick Start - Translation Quality Analysis

Get your first experiment running in 10 minutes!

## Prerequisites

- Python 3.9+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Step 1: Setup (2 minutes)

```bash
# Navigate to project
cd "llm with agents/HW3"

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp example.env .env
nano .env  # Or use any text editor
# Add your ANTHROPIC_API_KEY
```

## Step 2: Prepare Experiment (1 minute)

```bash
# Generate experiment with error injection
python src/main.py prepare \
    "The quick brown fox jumps over the lazy dog while the sun shines brightly in the sky"
```

**Output**: Creates `results/exp_TIMESTAMP/` with:
- `agent_prompts.txt` - Ready-to-use prompts
- `results_template.json` - Template for recording outputs
- `experiment_config.json` - Configuration

## Step 3: Run Translation Chain (5-7 minutes)

### Option A: Using Claude Code (Recommended)

Open `results/exp_*/agent_prompts.txt` and run each prompt:

```bash
# Copy-paste from agent_prompts.txt
claude-code "Translate to French: [misspelled text]"
# Record the French output

claude-code "Translate to Hebrew: [French output]"
# Record the Hebrew output

claude-code "Translate to English: [Hebrew output]"
# Record the final English output
```

### Option B: Using Claude.ai Chat

1. Open https://claude.ai
2. For each test case (0%, 25%, 50% error rates):
   - Start a new conversation
   - Paste the prompt from `agent_prompts.txt`
   - Copy the response
   - Record in `results_template.json`

## Step 4: Record Results (2 minutes)

Edit `results/exp_*/results_template.json`:

```json
{
  "experiment_id": "exp_20251123_123456",
  "results": [
    {
      "error_rate": 0.0,
      "original": "The quick brown fox...",
      "misspelled": "The quick brown fox...",
      "french": "Le renard brun rapide...",      ← Paste Agent 1 output
      "hebrew": "השועל החום המהיר...",             ← Paste Agent 2 output
      "final": "The fast brown fox...",          ← Paste Agent 3 output
      "word_count": 16
    }
  ]
}
```

Save as `results.json` (remove `_template` from filename).

## Step 5: Analyze & Visualize (1 minute)

```bash
python src/main.py analyze results/exp_*/results.json
```

**Output**:
- 📊 `error_vs_distance.png` - Beautiful graph
- 📈 `metrics_output.csv` - Raw metrics data
- 📋 Console summary with statistics

## View Your Results

```bash
# Open the graph
open results/exp_*/error_vs_distance.png  # macOS
# or
xdg-open results/exp_*/error_vs_distance.png  # Linux
```

## Example Output

```
METRICS SUMMARY
==============================================================

Error Rate | Distance | Change
--------------------------------------------------------------
     0%    |  0.0234  |   -
    25%    |  0.1123  | +0.0889
    50%    |  0.2789  | +0.1666

Total degradation: 0.2555
```

## What You Just Did

✅ Injected spelling errors at controlled rates
✅ Ran a 3-stage translation chain (EN→FR→HE→EN)
✅ Calculated semantic similarity using embeddings
✅ Generated publication-quality visualization
✅ Demonstrated translation quality degradation

## Next Steps

### Run More Experiments

```bash
# Test different error rates
python src/main.py prepare "Your sentence" --error-rates 0,10,20,30,40,50

# Use a different sentence
python src/main.py prepare "Artificial intelligence transforms technology remarkably"
```

### Understand the System

- Read [README.md](README.md) for complete documentation
- Check [PRD.md](PRD.md) for requirements
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Explore agent SKILL files in `agents/` directory

### Advanced Usage

```bash
# See all commands
python src/main.py --help

# Get system information
python src/main.py info

# Custom visualization
python src/main.py visualize results/exp_*/metrics_output.csv --dpi 300
```

## Troubleshooting

### "Configuration error"
→ Make sure `.env` file exists with `ANTHROPIC_API_KEY`

### "Module not found"
→ Activate venv: `source venv/bin/activate`

### "Hebrew not displaying"
→ Export UTF-8: `export LANG=en_US.UTF-8`

### Dependencies failing
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Common Questions

**Q: How long does this take?**
A: ~10 minutes total (2 min setup + 5 min translations + 2 min analysis + 1 min review)

**Q: Can I use different sentences?**
A: Yes! Any sentence with 15+ words works. The system will inject errors automatically.

**Q: What if I don't have Claude Code?**
A: Use Claude.ai chat interface manually. Just copy the prompts from `agent_prompts.txt`.

**Q: Do I need GPU?**
A: No, but it speeds up embeddings. CPU works fine for small experiments.

## System Requirements Met

✅ Multi-agent translation chain (3 agents)
✅ Error injection (0% to 50%)
✅ Vector distance calculation
✅ Visualization graphs
✅ Reproducible experiments
✅ Complete documentation

## Support

If you run into issues:
1. Check this QUICK_START guide
2. Review [README.md](README.md)
3. Check logs in `logs/` directory
4. Verify `.env` configuration

---

**Ready to start?** Run:
```bash
python src/main.py info
```

Then follow Step 2 above!

🎉 **Happy experimenting!**
