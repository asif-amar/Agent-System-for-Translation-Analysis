---
name: translation-chain-orchestrator
description: Orchestrates a three-stage translation chain (English→French→Hebrew→English) for linguistic degradation experiments. Manages sequential agent execution, tracks intermediate results, and prepares data for vector distance analysis. Use when conducting translation chain experiments or multi-stage translation analysis.
model: sonnet
color: yellow
---

# Translation Chain Orchestrator

This skill manages the complete translation chain experiment workflow, coordinating three translation agents sequentially and tracking results for analysis.

## Experiment Overview

### Purpose
Measure semantic degradation in a three-stage translation chain to analyze how spelling errors affect translation fidelity across multiple language conversions.

### Translation Chain
1. **Agent 1**: English → French (with error correction)
2. **Agent 2**: French → Hebrew  
3. **Agent 3**: Hebrew → English

### Success Criteria
- All three translations execute successfully
- Intermediate results are captured
- Final output is ready for vector distance comparison

## Workflow Steps

### 1. Input Preparation

**Requirements:**
- Sentence length: ≥15 words
- Spelling error rate: Configurable (0%-50%)
- Input format: Plain English text

**Error Introduction:**
- If error rate specified, introduce spelling mistakes
- Distribute errors throughout the sentence
- Maintain readability despite errors
- Document original vs. modified versions

### 2. Chain Execution

Execute agents sequentially:

```
Original English (with errors)
    ↓
[Agent 1: EN→FR]
    ↓
French Translation
    ↓
[Agent 2: FR→HE]
    ↓
Hebrew Translation
    ↓
[Agent 3: HE→EN]
    ↓
Final English
```

**Between Each Stage:**
- Capture intermediate result
- Verify successful translation
- Pass output as input to next agent
- Log any errors or warnings

### 3. Results Collection

**Data to Capture:**

```
Experiment Results:
------------------
Original English: [original text]
Error Rate: [percentage]
Misspelled English: [text with errors]

Translation Chain:
├─ Agent 1 Output (French): [french text]
├─ Agent 2 Output (Hebrew): [hebrew text]
└─ Agent 3 Output (English): [final text]

Metrics Ready For:
- Vector distance calculation
- Semantic similarity analysis
- Error propagation study
```

### 4. Data Formatting

Prepare structured output for analysis:

**For Python Processing:**
```python
{
    "original": "original english text",
    "error_rate": 0.25,
    "misspelled": "text with errors",
    "french": "traduction française",
    "hebrew": "תרגום עברי",
    "final": "final english translation",
    "word_count": 15
}
```

## Usage Instructions

### Running Single Experiment

1. Provide English sentence (≥15 words)
2. Specify error rate (0.0 to 0.5)
3. Introduce spelling errors if rate > 0
4. Execute three agents in sequence
5. Collect all intermediate results
6. Format for analysis

### Running Multiple Experiments

For error rate sweep (0% to 50%):

1. Use same base sentence
2. Create versions with different error rates:
   - 0% (control)
   - 10%, 20%, 25%, 30%, 40%, 50%
3. Run complete chain for each version
4. Compile results in structured format
5. Ready for vector distance calculation

## Output Format

### Individual Run Output

```
TRANSLATION CHAIN RESULTS
========================

Original Sentence: "[original]"
Word Count: [count]
Error Rate: [percentage]%

INPUT (with errors):
"[misspelled text]"

TRANSLATION CHAIN:
─────────────────
Step 1 (EN→FR): "[french]"
Step 2 (FR→HE): "[hebrew]"  
Step 3 (HE→EN): "[final]"

COMPARISON:
Original: "[original]"
Final:    "[final]"

Ready for vector distance calculation
```

### Batch Run Output

Create CSV or JSON file with all results for analysis.

## Integration with Metrics Calculation

After chain execution, results feed into:
- Embedding generation (using sentence-transformers or OpenAI)
- Vector distance calculation (cosine similarity, Euclidean distance)
- Visualization (error rate vs. distance graph)

## Critical Guidelines

- Execute agents in strict sequence
- Never skip intermediate translations
- Preserve exact agent outputs
- Document all error rates accurately
- Maintain Unicode encoding for Hebrew
- Do not attempt to "improve" agent outputs
- Capture timestamps for chain execution
- Handle agent failures gracefully

## Error Handling

If any agent fails:
1. Document which agent failed
2. Capture error message
3. Save intermediate results up to failure point
4. Abort chain execution cleanly
5. Report failure details for debugging
