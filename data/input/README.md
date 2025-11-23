# Input Files Guide

This directory contains three different test input files for the translation quality analysis system.

## Overview

| File | Test Cases | Purpose |
|------|-----------|---------|
| `sanity_check.json` | 1 | Quick validation |
| `same_sentence_progressive.json` | 11 | Same content, varying errors |
| `different_sentences_progressive.json` | 11 | Different content, varying errors |

---

## 1. Sanity Check (`sanity_check.json`)

**Purpose**: Quick validation that the system works correctly

**Contents**:
- **1 test case** with 15% error rate
- Single sentence: "The quick brown fox jumps over the lazy dog..."
- Use this for rapid testing during development

**When to use**:
- ✅ Testing if the system is set up correctly
- ✅ Quick validation after code changes
- ✅ Debugging individual components
- ✅ Verifying agent connectivity

**Expected runtime**: ~10 seconds

**Example usage**:
```bash
# Quick sanity check
python src/run_with_agents.py data/input/sanity_check.json

# Or manually
python src/main.py prepare data/input/sanity_check.json
```

---

## 2. Same Sentence Progressive (`same_sentence_progressive.json`)

**Purpose**: Test how error rate affects translation quality for **identical semantic content**

**Contents**:
- **11 test cases** (same sentence)
- Error rates: 0%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%
- Sentence: "The quick brown fox jumps over the lazy dog while the sun shines brightly in the clear blue sky"

**Research question**:
*How does increasing spelling error rate affect semantic preservation when translating the same content?*

**When to use**:
- ✅ Studying error rate impact
- ✅ Measuring translation robustness
- ✅ Comparing error correction effectiveness
- ✅ Creating error rate vs distance graphs

**Expected runtime**: ~2-3 minutes (33 API calls)

**Example usage**:
```bash
python src/run_with_agents.py data/input/same_sentence_progressive.json
```

**Expected results**:
- Should show correlation between error rate and semantic distance
- Tests if more errors = more semantic drift
- Baseline for comparing with different sentences

**Graph visualization**:
Will show a single semantic content tested at 11 different error levels.

---

## 3. Different Sentences Progressive (`different_sentences_progressive.json`)

**Purpose**: Test how error rate affects translation quality across **different semantic domains**

**Contents**:
- **11 test cases** (different sentences)
- Error rates: 0%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%
- Topics:
  1. Animals/Nature (0%)
  2. Technology/AI (5%)
  3. Climate/Science (10%)
  4. Communication/Technology (15%)
  5. Education (20%)
  6. Medical Research (25%)
  7. Economics (30%)
  8. Environment (35%)
  9. Culture (40%)
  10. Space Exploration (45%)
  11. Democracy/Society (50%)

**Research questions**:
- *Does error rate affect different topics differently?*
- *Are some semantic domains more robust to errors?*
- *How does sentence complexity interact with error rate?*

**When to use**:
- ✅ Testing across diverse content
- ✅ Measuring generalization of error correction
- ✅ Comparing topic-specific robustness
- ✅ Publication-quality research

**Expected runtime**: ~2-3 minutes (33 API calls)

**Example usage**:
```bash
python src/run_with_agents.py data/input/different_sentences_progressive.json
```

**Expected results**:
- May show variation based on topic complexity
- Some domains might be more error-tolerant
- Tests real-world diversity of content

**Graph visualization**:
Will show how different semantic content responds to increasing error rates.

---

## Comparison: Same vs Different Sentences

| Aspect | Same Sentence | Different Sentences |
|--------|---------------|---------------------|
| **Semantic Content** | Identical | Varies |
| **Error Rate** | 0-50% | 0-50% |
| **Vocabulary** | Same words | Different words |
| **Complexity** | Constant | Varies |
| **Topic** | Animals/nature | 11 different topics |
| **Research Value** | Isolates error effect | Tests generalization |
| **Best For** | Error rate analysis | Domain robustness |

---

## File Format

All input files follow this JSON schema:

```json
{
  "sentences": [
    {
      "id": "unique_id",
      "original": "Original clean text",
      "misspelled": "Text with spelling errors",
      "error_rate": 0.15,
      "word_count": 19
    }
  ],
  "metadata": {
    "version": "1.0",
    "type": "file_type",
    "created_at": "2025-11-23",
    "description": "Description of test set",
    "purpose": "Research purpose"
  }
}
```

**Fields**:
- `id`: Unique identifier for the test case
- `original`: Clean text without errors
- `misspelled`: Text with intentional spelling errors
- `error_rate`: Percentage of words with errors (0.0 to 1.0)
- `word_count`: Number of words in the sentence

---

## How to Run Each Input

### Option 1: Automated with API Key

```bash
# Set API key in .env first
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env

# Run any input file
python src/run_with_agents.py data/input/sanity_check.json
python src/run_with_agents.py data/input/same_sentence_progressive.json
python src/run_with_agents.py data/input/different_sentences_progressive.json
```

### Option 2: Manual with Claude Code (No API Key)

The current approach - I translate them for you using SKILL agents!

Just say: **"Run [filename] with real agents"**

And I'll:
1. Load the input file
2. Translate each test case (EN→FR→HE→EN)
3. Save results.json
4. Run analysis
5. Generate graphs

---

## Analyzing Results

After running any input file, analyze with:

```bash
python src/main.py analyze results/[output_directory]/results_*.json
```

This generates:
- `metrics_output.csv` - Distance metrics
- `error_vs_distance.png` - Visualization graph

---

## Expected Outputs

### For Sanity Check:
```
1 test case → 1 result
Quick validation that system works
```

### For Same Sentence Progressive:
```
11 test cases → 11 results
Graph shows: Error Rate (x-axis) vs Distance (y-axis)
Expected: Increasing trend (more errors = more distance)
```

### For Different Sentences Progressive:
```
11 test cases → 11 results
Graph shows: Error Rate (x-axis) vs Distance (y-axis)
Expected: Variation by topic, overall increasing trend
```

---

## Research Workflow

### Step 1: Sanity Check
```bash
# Quick test
python src/run_with_agents.py data/input/sanity_check.json
# Verify it works
```

### Step 2: Same Sentence Analysis
```bash
# Test error rate effect
python src/run_with_agents.py data/input/same_sentence_progressive.json
python src/main.py analyze results/*/results_*.json
```

### Step 3: Different Sentences Analysis
```bash
# Test domain generalization
python src/run_with_agents.py data/input/different_sentences_progressive.json
python src/main.py analyze results/*/results_*.json
```

### Step 4: Compare Results
```bash
# Compare the two graphs
open results/same_*/error_vs_distance.png
open results/different_*/error_vs_distance.png
```

---

## Files Summary

```
data/input/
├── README.md                              ← This file
├── sanity_check.json                      ← 1 test case (15% errors)
├── same_sentence_progressive.json         ← 11 cases, same content
├── different_sentences_progressive.json   ← 11 cases, different content
└── sentences.json                         ← Legacy/backup

Total test cases available: 23
```

---

## Tips

1. **Start with sanity check** to verify system works
2. **Run same sentence** first to isolate error rate effect
3. **Run different sentences** to test generalization
4. **Compare results** to see if content type matters
5. **Use sanity check** for debugging

---

## Which File Should I Use?

**For quick testing**: `sanity_check.json`
**For error rate research**: `same_sentence_progressive.json`
**For comprehensive research**: `different_sentences_progressive.json`
**For publication**: Run both progressive files and compare

---

**Last Updated**: November 23, 2025
