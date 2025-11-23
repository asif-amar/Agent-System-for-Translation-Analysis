---
name: translation-metrics-analyzer
description: Calculates vector embeddings and distance metrics for translation chain experiments. Computes semantic similarity between original and translated text using embeddings, generates comparison graphs, and analyzes error rate impact. Use for measuring translation fidelity and visualizing degradation patterns.
---

# Translation Metrics Analyzer

This skill handles all mathematical and analytical aspects of the translation chain experiment, including embeddings, distance calculations, and visualization.

## Core Capabilities

### 1. Embedding Generation
### 2. Vector Distance Calculation  
### 3. Statistical Analysis
### 4. Visualization

## Embedding Methods

### Option A: Using sentence-transformers

**Recommended Model:** `all-MiniLM-L6-v2` (fast, efficient)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
original_embedding = model.encode(original_text)
final_embedding = model.encode(final_text)
```

**Alternative Models:**
- `all-mpnet-base-v2` (higher quality, slower)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual support)

### Option B: Using OpenAI API

```python
import openai

def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response['data'][0]['embedding']

original_embedding = get_embedding(original_text)
final_embedding = get_embedding(final_text)
```

## Distance Metrics

### Cosine Similarity

**Formula:** Measures angular similarity (range: -1 to 1)

```python
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(
    [original_embedding], 
    [final_embedding]
)[0][0]

# Convert to distance (0 = identical, 2 = opposite)
cosine_distance = 1 - similarity
```

**Interpretation:**
- 0.0: Perfect semantic match
- 0.1-0.3: High similarity
- 0.3-0.5: Moderate similarity
- 0.5+: Low similarity

### Euclidean Distance

**Formula:** Straight-line distance in embedding space

```python
import numpy as np

euclidean_distance = np.linalg.norm(
    original_embedding - final_embedding
)
```

**Note:** Scale depends on embedding dimensionality

### Manhattan Distance (L1)

```python
manhattan_distance = np.sum(
    np.abs(original_embedding - final_embedding)
)
```

## Batch Processing

### Process Multiple Error Rates

```python
import pandas as pd

results = []

for error_rate in [0, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5]:
    # Run translation chain
    original, final = run_chain(base_text, error_rate)
    
    # Calculate embeddings
    orig_emb = model.encode(original)
    final_emb = model.encode(final)
    
    # Calculate distance
    distance = 1 - cosine_similarity([orig_emb], [final_emb])[0][0]
    
    results.append({
        'error_rate': error_rate,
        'distance': distance,
        'original': original,
        'final': final
    })

df = pd.DataFrame(results)
```

## Visualization

### Generate Error Rate vs. Distance Graph

```python
import matplotlib.pyplot as plt

# Prepare data
error_rates = df['error_rate'] * 100  # Convert to percentage
distances = df['distance']

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(error_rates, distances, marker='o', linewidth=2, markersize=8)
plt.xlabel('Spelling Error Rate (%)', fontsize=12)
plt.ylabel('Vector Distance (Cosine)', fontsize=12)
plt.title('Translation Chain Semantic Degradation', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save
plt.savefig('error_vs_distance.png', dpi=300)
plt.show()
```

### Enhanced Visualization

```python
# Add confidence intervals or error bars
plt.figure(figsize=(12, 7))

# Main plot
plt.plot(error_rates, distances, 'o-', linewidth=2, markersize=10, 
         label='Cosine Distance', color='#2E86AB')

# Add trend line
z = np.polyfit(error_rates, distances, 2)
p = np.poly1d(z)
plt.plot(error_rates, p(error_rates), '--', 
         label='Polynomial Fit', color='#A23B72', alpha=0.7)

plt.xlabel('Spelling Error Rate (%)', fontsize=13)
plt.ylabel('Semantic Distance', fontsize=13)
plt.title('Impact of Spelling Errors on Translation Chain Fidelity', 
          fontsize=15, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('enhanced_error_analysis.png', dpi=300, bbox_inches='tight')
```

## Statistical Analysis

### Calculate Correlation

```python
from scipy.stats import pearsonr, spearmanr

# Pearson correlation (linear)
pearson_r, pearson_p = pearsonr(error_rates, distances)
print(f"Pearson r: {pearson_r:.3f} (p={pearson_p:.4f})")

# Spearman correlation (monotonic)
spearman_r, spearman_p = spearmanr(error_rates, distances)
print(f"Spearman ρ: {spearman_r:.3f} (p={spearman_p:.4f})")
```

### Degradation Rate

```python
# Calculate degradation per 10% error increase
degradation_rate = (distances.iloc[-1] - distances.iloc[0]) / 5
print(f"Average degradation per 10% error: {degradation_rate:.4f}")
```

## Complete Analysis Pipeline

```python
#!/usr/bin/env python3
"""
Translation Chain Metrics Calculator
Analyzes semantic degradation across error rates
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_translation_chain(results_file):
    """
    Complete analysis pipeline
    
    Args:
        results_file: JSON or CSV with translation results
    
    Returns:
        DataFrame with metrics and saves visualization
    """
    
    # Load results
    df = pd.read_json(results_file)
    
    # Initialize model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Calculate embeddings and distances
    distances = []
    for _, row in df.iterrows():
        orig_emb = model.encode(row['original'])
        final_emb = model.encode(row['final'])
        dist = 1 - cosine_similarity([orig_emb], [final_emb])[0][0]
        distances.append(dist)
    
    df['distance'] = distances
    
    # Generate visualization
    plt.figure(figsize=(10, 6))
    plt.plot(df['error_rate'] * 100, df['distance'], 'o-', linewidth=2)
    plt.xlabel('Error Rate (%)')
    plt.ylabel('Semantic Distance')
    plt.title('Translation Chain Degradation Analysis')
    plt.grid(True, alpha=0.3)
    plt.savefig('analysis_results.png', dpi=300)
    
    # Save results
    df.to_csv('metrics_output.csv', index=False)
    
    return df

if __name__ == "__main__":
    df = analyze_translation_chain('translation_results.json')
    print("\nAnalysis Summary:")
    print(df[['error_rate', 'distance']].to_string())
```

## Output Format

### Metrics Report

```
TRANSLATION CHAIN METRICS ANALYSIS
==================================

Embedding Model: all-MiniLM-L6-v2
Distance Metric: Cosine Distance
Sample Size: 7 error rates

Results:
--------
Error Rate | Distance | Change
     0%    |  0.0234  |   -
    10%    |  0.0456  | +0.0222
    20%    |  0.0891  | +0.0435
    25%    |  0.1123  | +0.0232
    30%    |  0.1456  | +0.0333
    40%    |  0.2134  | +0.0678
    50%    |  0.2789  | +0.0655

Statistics:
-----------
Pearson Correlation: 0.987 (p < 0.001)
Average Degradation: 0.0511 per 10% error
Max Distance: 0.2789 at 50% errors
Min Distance: 0.0234 at 0% errors

Graph saved: error_vs_distance.png
Data saved: metrics_output.csv
```

## Dependencies

Required Python packages:

```bash
pip install sentence-transformers scikit-learn numpy pandas matplotlib scipy
```

Alternative with OpenAI:
```bash
pip install openai numpy pandas matplotlib scipy
```

## Critical Guidelines

- Use consistent embedding model across all comparisons
- Normalize text before embedding (lowercase, strip whitespace)
- Use same distance metric throughout experiment
- Run embeddings on GPU if available for speed
- Cache embeddings to avoid recomputation
- Validate embedding dimensions match
- Handle Unicode (Hebrew) properly in embeddings
