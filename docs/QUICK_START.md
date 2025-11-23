# 🚀 Quick Start Guide - Translation Chain Experiment

## What You Have

Complete agent-based system for translation chain experiments with automated metrics:

```
✅ 3 Translation Agents (EN→FR, FR→HE, HE→EN)
✅ Orchestrator for managing the chain
✅ Metrics analyzer with vector embeddings
✅ Automated experiment runner
✅ Python scripts for analysis & visualization
✅ Complete documentation
```

## Fastest Way to Start

### 1️⃣ Run the Experiment Preparation (30 seconds)

```bash
cd translation-agents
python run_experiment.py "The quick brown fox jumps over the lazy dog in the deep forest" \
    --error-rates 0 0.25 0.5
```

This creates everything you need in `experiment_output/`:
- Pre-generated sentences with errors
- Ready-to-use Claude Code prompts
- Results template for recording outputs

### 2️⃣ Execute Translations (5 minutes per error rate)

Open `experiment_output/agent_prompts.txt` and copy-paste each prompt into Claude Code:

```bash
# Example prompts (auto-generated):
claude-code "Using agent-en-to-fr, translate: 'Teh quik brown fox...'"
claude-code "Using agent-fr-to-he, translate: '[paste French output]'"
claude-code "Using agent-he-to-en, translate: '[paste Hebrew output]'"
```

### 3️⃣ Record Results (2 minutes)

Fill in `experiment_output/results_template.json` with your agent outputs, then rename to `results.json`

### 4️⃣ Calculate Metrics & Generate Graph (1 minute)

```bash
pip install sentence-transformers scikit-learn numpy pandas matplotlib scipy

python translation-metrics-analyzer/scripts/calculate_metrics.py \
    experiment_output/results.json \
    --output-dir experiment_output
```

### 5️⃣ View Results

You now have:
- 📊 `error_vs_distance.png` - Beautiful visualization
- 📈 `metrics_output.csv` - Raw data
- 📋 Console output with statistics

## File Structure

```
translation-agents/
├── 📘 SYSTEM_SUMMARY.md          ← Full system overview
├── 📗 README.md                  ← Detailed documentation
├── 🤖 agent-en-to-fr/            ← Agent 1: English → French
├── 🤖 agent-fr-to-he/            ← Agent 2: French → Hebrew
├── 🤖 agent-he-to-en/            ← Agent 3: Hebrew → English
├── 🎯 translation-chain-orchestrator/  ← Chain manager
├── 📊 translation-metrics-analyzer/    ← Metrics & graphs
└── ⚙️  run_experiment.py         ← Automated setup
```

## The Agents Explained

### Agent 1: English → French
- Accepts misspelled English (0-50% errors)
- Intelligently corrects spelling
- Produces clean French translation

### Agent 2: French → Hebrew
- Translates to Hebrew script (right-to-left)
- Maintains semantic fidelity
- Handles cascaded translation errors

### Agent 3: Hebrew → English
- Completes the translation loop
- Returns to English for comparison
- Enables vector distance measurement

## Expected Output Example

```
TRANSLATION CHAIN RESULTS
========================

Original: "The quick brown fox jumps over the lazy dog"
Error Rate: 25%

INPUT (with errors):
"Teh quik brown fox jumps ovr the lasy dog"

CHAIN:
├─ French:  "Le renard brun rapide saute par-dessus le chien paresseux"
├─ Hebrew:  "השועל החום המהיר קופץ מעל הכלב העצלן"
└─ English: "The fast brown fox jumps over the lazy dog"

Vector Distance: 0.0823
```

## Common Questions

**Q: How long does this take?**
A: ~15 minutes total (3 min setup + 10 min translations + 2 min analysis)

**Q: Can I use different sentences?**
A: Yes! Just pass any sentence ≥15 words to `run_experiment.py`

**Q: What if I don't have Claude Code?**
A: You can manually run agents through Claude.ai chat by referencing the skills

**Q: Can I test more error rates?**
A: Yes! Add any rates between 0-0.5: `--error-rates 0 0.1 0.15 0.2 0.25...`

## Troubleshooting

### Hebrew not displaying correctly?
Ensure UTF-8 encoding: `export LANG=en_US.UTF-8`

### Embeddings too slow?
Use smaller model: Edit `calculate_metrics.py` line 27 to use `'all-MiniLM-L6-v2'` (already default)

### Missing dependencies?
```bash
pip install sentence-transformers scikit-learn numpy pandas matplotlib scipy
```

## What Makes This Special

1. **Fully Automated**: One command prepares everything
2. **Production Ready**: Professional code with error handling
3. **Scientific**: Proper embeddings, statistics, correlations
4. **Complete**: Documentation, scripts, agents all included
5. **Flexible**: Works with Claude Code, API, or manual execution

## Next Steps

1. Read `SYSTEM_SUMMARY.md` for full details
2. Review agent SKILL.md files to understand behaviors
3. Run your first experiment with the commands above
4. Examine the generated graph and metrics
5. Include everything in your assessment deliverables

## Support Files

- **SYSTEM_SUMMARY.md** - Complete system documentation
- **README.md** - Detailed usage guide  
- **SKILL.md** (in each agent) - Agent-specific instructions
- **calculate_metrics.py** - Fully commented Python code
- **ANALYSIS_INSTRUCTIONS.md** - Auto-generated per experiment

---

**Ready?** Start with:
```bash
python run_experiment.py "Your sentence here with at least fifteen words for testing"
```

🎉 Everything is ready to go!
