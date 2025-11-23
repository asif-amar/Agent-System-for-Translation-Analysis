# How to Run Experiments - Complete Guide

This guide shows you how to run translation experiments with **automatic setup**.

## 🚀 Quick Start (One Command)

```bash
./run_experiment.sh
```

That's it! The script will:
1. ✅ Create `.env` from `example.env` if needed
2. ✅ Create `venv` if it doesn't exist
3. ✅ Install all dependencies
4. ✅ Show menu to select which input to run
5. ✅ Run translations (with or without API key)
6. ✅ Analyze results automatically
7. ✅ Generate graphs

---

## 📋 What the Script Does

### Automatic Setup

The `run_experiment.sh` script handles everything:

**Environment Setup**:
- Creates `.env` from `example.env` (if missing)
- Checks for API key
- Creates virtual environment (if needed)
- Installs all Python dependencies

**Smart Mode Selection**:
- **Has API key?** → Uses Anthropic API (automated)
- **No API key?** → Uses Claude Code (you're using it now!)

**Run Experiments**:
- Choose which input to run (sanity, same, different, or all)
- Executes translations
- Analyzes results
- Generates graphs

---

## 🎯 Usage Options

### Option 1: Interactive Menu (Recommended)

```bash
./run_experiment.sh
```

You'll see:
```
Select which input to run:
  1) Sanity Check (1 test case, ~10 seconds)
  2) Same Sentence Progressive (11 test cases, ~2-3 minutes)
  3) Different Sentences Progressive (11 test cases, ~2-3 minutes)
  4) All three (23 test cases total)

Enter choice (1-4):
```

### Option 2: Command Line Arguments

```bash
# Run sanity check
./run_experiment.sh sanity

# Run same sentence progressive
./run_experiment.sh same

# Run different sentences progressive
./run_experiment.sh different

# Run all three
./run_experiment.sh all
```

---

## 🔑 Two Modes of Operation

### Mode 1: With API Key (Automated)

If you have an Anthropic API key:

1. Script creates `.env` from `example.env`
2. Edit `.env` and add your key:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
   ```
3. Run script - it uses API automatically
4. Fully automated, no manual steps

**Pros**: Fully automated, fast
**Cons**: Requires API key, costs ~$0.02-0.05

### Mode 2: Without API Key (Claude Code)

If you don't have an API key:

1. Script detects no API key
2. Uses Claude Code (this conversation!)
3. I execute the SKILL agents for you
4. Results saved automatically

**Pros**: Free, no API key needed
**Cons**: Manual (but I do the work!)

---

## 📂 What Each Input Tests

### 1. Sanity Check
- **File**: `data/input/sanity_check.json`
- **Test Cases**: 1
- **Time**: ~10 seconds
- **Purpose**: Verify system works

### 2. Same Sentence Progressive
- **File**: `data/input/same_sentence_progressive.json`
- **Test Cases**: 11 (0% to 50% errors)
- **Time**: ~2-3 minutes
- **Purpose**: Measure error rate effect

### 3. Different Sentences Progressive
- **File**: `data/input/different_sentences_progressive.json`
- **Test Cases**: 11 (different topics)
- **Time**: ~2-3 minutes
- **Purpose**: Test domain generalization

---

## 🔧 How It Works

### Step-by-Step Process

1. **Environment Check**
   ```
   [Step 1/5] Checking environment configuration...
   ✓ .env file exists
   ✓ API key found (or ⚠ No API key - using Claude Code)
   ```

2. **Virtual Environment**
   ```
   [Step 2/5] Checking Python virtual environment...
   ✓ Virtual environment exists (or creating new one)
   ```

3. **Dependencies**
   ```
   [Step 3/5] Installing dependencies...
   ✓ Dependencies already installed (or installing now)
   ```

4. **Input Selection**
   ```
   [Step 4/5] Selecting input file(s)...
   ✓ Selected: Same Sentence Progressive
   ```

5. **Run Experiment**
   ```
   [Step 5/5] Running experiments...
   Running: Same Sentence Progressive
   Mode: CLAUDE_CODE (or API)
   ```

### With API Key (Automated)

```bash
./run_experiment.sh same
```

Output:
```
✓ Running with Anthropic API...
Processing test case 1/11... ✓
Processing test case 2/11... ✓
...
✓ All translations complete
✓ Analysis complete
✓ Graph saved: results/api_run/error_vs_distance.png
```

### Without API Key (Claude Code)

```bash
./run_experiment.sh same
```

Output:
```
⚠ Running in Claude Code mode...
⚠ This requires Claude Code to execute translations

INSTRUCTIONS:
1. The script will generate a request
2. Copy and paste the request to Claude Code
3. Claude will execute all translations
4. Results will be saved automatically
```

Then I (Claude) will:
1. Receive the request
2. Execute all 11 translations using SKILL agents
3. Provide complete JSON results
4. Save to `results/claude_code_run/results_TIMESTAMP.json`
5. Run analysis automatically
6. Generate graphs

---

## 📊 Results Location

After running, find results in:

**With API**:
```
results/api_run/
├── results_20251123_HHMMSS.json
├── metrics_output.csv
└── error_vs_distance.png
```

**Without API (Claude Code)**:
```
results/claude_code_run/
├── results_20251123_HHMMSS.json
├── metrics_output.csv
└── error_vs_distance.png
```

---

## 📈 Analyzing Results

The script automatically runs analysis, but you can also run manually:

```bash
# Analyze specific results
python src/main.py analyze results/claude_code_run/results_20251123_HHMMSS.json

# View graph
open results/claude_code_run/error_vs_distance.png

# View metrics
cat results/claude_code_run/metrics_output.csv
```

---

## 🎬 Complete Example

### Scenario: Run all three inputs without API key

```bash
# 1. Run the script
./run_experiment.sh all

# Output:
# [Step 1/5] Checking environment configuration...
# ✓ Creating .env from example.env...
# ⚠ No API key found - will use Claude Code
#
# [Step 2/5] Checking Python virtual environment...
# ✓ Creating virtual environment...
#
# [Step 3/5] Installing dependencies...
# ✓ Installing Python packages...
#
# [Step 4/5] Selecting input file(s)...
# ✓ Selected: Sanity Check, Same Sentence Progressive, Different Sentences Progressive
#
# [Step 5/5] Running experiments...

# For each input, Claude Code will execute translations
# Results automatically saved and analyzed
```

**Total time**: ~5-7 minutes for all 23 test cases

**Output**: 3 complete result sets with analysis and graphs

---

## 🆘 Troubleshooting

### "Permission denied"
```bash
chmod +x run_experiment.sh
./run_experiment.sh
```

### "Python not found"
```bash
# Install Python 3.9+
# On Mac: brew install python3
# Then run script again
```

### "venv creation failed"
```bash
# Remove old venv and try again
rm -rf venv
./run_experiment.sh
```

### "Dependencies won't install"
```bash
# Activate venv manually and install
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔄 Running Multiple Times

### First Run
```bash
./run_experiment.sh
# Sets up everything, runs experiment
```

### Subsequent Runs
```bash
./run_experiment.sh same
# Skips setup (already done), runs experiment immediately
```

The script is smart:
- **Already have .env?** Skip creation
- **Already have venv?** Skip creation
- **Already installed packages?** Skip installation
- **Only runs what's needed!**

---

## 📝 Advanced Usage

### Run Specific Input Directly

```bash
# Just sanity check
./run_experiment.sh sanity

# Just same sentence
./run_experiment.sh same

# Just different sentences
./run_experiment.sh different
```

### Manual Mode (Skip Script)

If you want to run manually:

```bash
# 1. Setup
cp example.env .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run with API key
python src/run_with_agents.py data/input/same_sentence_progressive.json

# 3. Or run with Claude Code
python src/run_with_claude_code.py data/input/same_sentence_progressive.json
```

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `run_experiment.sh` | Main script - runs everything |
| `src/run_with_agents.py` | API mode - automated |
| `src/run_with_claude_code.py` | Claude Code mode - manual |
| `example.env` | Environment template |
| `.env` | Your configuration (created automatically) |

---

## ✅ Summary

**Simplest way to run experiments**:
```bash
./run_experiment.sh
```

**What it does**:
- ✅ Creates .env (if needed)
- ✅ Creates venv (if needed)
- ✅ Installs dependencies (if needed)
- ✅ Detects API key (or uses Claude Code)
- ✅ Runs selected experiments
- ✅ Analyzes results
- ✅ Generates graphs

**You just run one command and get complete results!** 🎉

---

## 🎯 Recommended Workflow

1. **First time**: Run sanity check
   ```bash
   ./run_experiment.sh sanity
   ```

2. **Once working**: Run same sentence
   ```bash
   ./run_experiment.sh same
   ```

3. **For research**: Run different sentences
   ```bash
   ./run_experiment.sh different
   ```

4. **For publication**: Run all
   ```bash
   ./run_experiment.sh all
   ```

---

**Questions?** The script is self-documenting - just run it and follow the prompts!

**Last Updated**: November 23, 2025
