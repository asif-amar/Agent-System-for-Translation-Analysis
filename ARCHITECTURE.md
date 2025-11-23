# Architecture Document
## Multi-Step Agent System for Translation Analysis

### Document Information
- **Version:** 1.0
- **Date:** 2025-11-23
- **System Name:** Translation Quality Analysis Pipeline
- **Architecture Status:** Proposed

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [C4 Model Diagrams](#2-c4-model-diagrams)
3. [Component Architecture](#3-component-architecture)
4. [Data Architecture](#4-data-architecture)
5. [Deployment Architecture](#5-deployment-architecture)
6. [Operational Architecture](#6-operational-architecture)
7. [Architectural Decision Records](#7-architectural-decision-records)
8. [API Specifications](#8-api-specifications)
9. [Security Architecture](#9-security-architecture)
10. [Technical Constraints](#10-technical-constraints)

---

## 1. System Overview

### 1.1 Purpose
The Translation Quality Analysis Pipeline is a research tool designed to measure translation quality degradation through multi-step translation chains with varying levels of input errors.

### 1.2 Architectural Goals
- **Modularity:** Each agent operates independently and can be replaced
- **Extensibility:** Support for additional languages and error types
- **Reproducibility:** Deterministic results with seed control
- **Observability:** Comprehensive logging of all transformations
- **Performance:** Efficient processing of batch experiments

### 1.3 Technology Stack
- **Language:** Python 3.9+
- **CLI Framework:** Click or argparse
- **LLM Integration:** Anthropic Claude API / OpenAI API
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2) or OpenAI embeddings
- **Visualization:** Matplotlib / Plotly
- **Data Processing:** Pandas, NumPy
- **Testing:** pytest
- **Dependency Management:** pip + requirements.txt

---

## 2. C4 Model Diagrams

### 2.1 Level 1: System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    External Systems                         │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Claude API │      │  OpenAI API  │                   │
│  │              │      │              │                   │
│  │ Translation  │      │ Embeddings   │                   │
│  └──────┬───────┘      └──────┬───────┘                   │
│         │                     │                            │
└─────────┼─────────────────────┼────────────────────────────┘
          │                     │
          │   API Calls         │  API Calls
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│          Translation Quality Analysis Pipeline              │
│                                                             │
│  • Processes sentences with spelling errors                │
│  • Chains translations: EN → FR → HE → EN                  │
│  • Calculates vector distances                             │
│  • Generates quality degradation graphs                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │                     │
          │  Reads/Writes       │  Reads/Writes
          ▼                     ▼
┌──────────────────┐      ┌──────────────────┐
│                  │      │                  │
│  File System     │      │  Results Store   │
│                  │      │                  │
│  • Input         │      │  • Metrics       │
│    sentences     │      │  • Graphs        │
│  • Config        │      │  • Logs          │
└──────────────────┘      └──────────────────┘

          ▲
          │
          │  CLI Commands
          │
    ┌─────┴──────┐
    │            │
    │  Researcher│
    │            │
    └────────────┘
```

**Description:**
- **Researcher:** Provides input sentences, runs experiments via CLI
- **Translation API:** External LLM service for language translation
- **Embedding API:** External service for semantic embeddings
- **File System:** Local storage for inputs and configurations
- **Results Store:** Local storage for outputs, metrics, and visualizations

---

### 2.2 Level 2: Container Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                Translation Quality Analysis Pipeline                  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                       CLI Application                        │    │
│  │                    (Python/Click)                            │    │
│  │                                                              │    │
│  │  • Command parsing                                           │    │
│  │  • Workflow orchestration                                    │    │
│  │  • User interaction                                          │    │
│  └────────────┬────────────────────────────────┬────────────────┘    │
│               │                                │                     │
│               ▼                                ▼                     │
│  ┌────────────────────────┐      ┌────────────────────────┐         │
│  │  Translation Pipeline  │      │   Analysis Engine      │         │
│  │      (Python)          │      │      (Python)          │         │
│  │                        │      │                        │         │
│  │  • Agent 1 (EN→FR)    │      │  • Error Injection     │         │
│  │  • Agent 2 (FR→HE)    │      │  • Vector Distance     │         │
│  │  • Agent 3 (HE→EN)    │      │  • Metrics Calculation │         │
│  │  • Chain orchestration│      │  • Graph Generation    │         │
│  └────────┬───────────────┘      └────────┬───────────────┘         │
│           │                               │                          │
│           ▼                               ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Data Management Layer                      │    │
│  │                       (Python/Pandas)                        │    │
│  │                                                              │    │
│  │  • Input loading         • Result storage                   │    │
│  │  • Metadata tracking     • Export functions                 │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

**Container Responsibilities:**

1. **CLI Application:**
   - Entry point for user interaction
   - Command routing and validation
   - Progress reporting

2. **Translation Pipeline:**
   - Manages three sequential translation agents
   - Handles API communication
   - Implements retry logic

3. **Analysis Engine:**
   - Injects spelling errors at specified rates
   - Computes embeddings and vector distances
   - Generates visualization graphs

4. **Data Management Layer:**
   - Centralized I/O operations
   - Data serialization/deserialization
   - Results aggregation

---

### 2.3 Level 3: Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Application                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Parser     │  │  Commander   │  │   Reporter   │         │
│  │              │  │              │  │              │         │
│  │ • Arg parse  │→ │ • Dispatch   │→ │ • Progress   │         │
│  │ • Validation │  │ • Workflow   │  │ • Results    │         │
│  └──────────────┘  └──────┬───────┘  └──────────────┘         │
└─────────────────────────────┼──────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Translation   │  │  Error Injection │  │ Metrics          │
│ Pipeline      │  │  Module          │  │ Calculator       │
│               │  │                  │  │                  │
│ ┌───────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │Agent Base │ │  │ │ErrorInjector │ │  │ │ Embedder     │ │
│ │           │ │  │ │              │ │  │ │              │ │
│ │• execute()│ │  │ │• inject()    │ │  │ │• encode()    │ │
│ │• validate │ │  │ │• strategies  │ │  │ │• model mgmt  │ │
│ └─────┬─────┘ │  │ └──────────────┘ │  │ └──────┬───────┘ │
│       │       │  │                  │  │        │         │
│ ┌─────▼─────┐ │  │ ┌──────────────┐ │  │ ┌──────▼───────┐ │
│ │EN→FR Agent│ │  │ │ErrorStrategy │ │  │ │VectorCalc    │ │
│ └───────────┘ │  │ │              │ │  │ │              │ │
│ ┌───────────┐ │  │ │• substitute  │ │  │ │• cosine()    │ │
│ │FR→HE Agent│ │  │ │• delete      │ │  │ │• euclidean() │ │
│ └───────────┘ │  │ │• transpose   │ │  │ └──────────────┘ │
│ ┌───────────┐ │  │ └──────────────┘ │  │                  │
│ │HE→EN Agent│ │  │                  │  │                  │
│ └───────────┘ │  └──────────────────┘  └──────────────────┘
└───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Visualization    │
                    │ Generator        │
                    │                  │
                    │ ┌──────────────┐ │
                    │ │GraphPlotter  │ │
                    │ │              │ │
                    │ │• plot()      │ │
                    │ │• style()     │ │
                    │ │• export()    │ │
                    │ └──────────────┘ │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Data Layer       │
                    │                  │
                    │ • FileIO         │
                    │ • Serializer     │
                    │ • DataStore      │
                    └──────────────────┘
```

---

### 2.4 Level 4: Code-Level Class Diagram (UML)

```
┌─────────────────────────┐
│      «interface»        │
│    TranslationAgent     │
├─────────────────────────┤
│ + source_lang: str      │
│ + target_lang: str      │
├─────────────────────────┤
│ + translate(text): str  │
│ + validate_input(text)  │
└───────────▲─────────────┘
            │
            │ implements
    ┌───────┼───────┬───────────┐
    │       │       │           │
┌───▼───────┴┐  ┌──▼──────────┐  ┌▼─────────────┐
│EnglishToFr │  │FrenchToHebr │  │HebrewToEngl  │
│enchAgent   │  │ewAgent      │  │ishAgent      │
├────────────┤  ├─────────────┤  ├──────────────┤
│-api_client │  │-api_client  │  │-api_client   │
├────────────┤  ├─────────────┤  ├──────────────┤
│+translate()│  │+translate() │  │+translate()  │
└────────────┘  └─────────────┘  └──────────────┘

┌──────────────────────────┐
│    ErrorInjector         │
├──────────────────────────┤
│ - error_rate: float      │
│ - random_seed: int       │
│ - strategies: List       │
├──────────────────────────┤
│ + inject(text): str      │
│ + set_rate(rate): void   │
│ - _apply_errors(): str   │
└──────────────────────────┘

┌──────────────────────────┐
│    VectorMetrics         │
├──────────────────────────┤
│ - embedder: Embedder     │
├──────────────────────────┤
│ + calculate_distance()   │
│ + cosine_similarity()    │
│ + euclidean_distance()   │
└──────────────────────────┘

┌──────────────────────────┐
│    TranslationPipeline   │
├──────────────────────────┤
│ - agents: List[Agent]    │
│ - logger: Logger         │
├──────────────────────────┤
│ + execute(text): Result  │
│ + add_agent(agent)       │
│ - _chain_translate()     │
└──────────────────────────┘

┌──────────────────────────┐
│    ExperimentRunner      │
├──────────────────────────┤
│ - pipeline: Pipeline     │
│ - injector: ErrorInject  │
│ - metrics: VectorMetrics │
├──────────────────────────┤
│ + run_experiment()       │
│ + batch_process()        │
│ - _collect_results()     │
└──────────────────────────┘

┌──────────────────────────┐
│    GraphGenerator        │
├──────────────────────────┤
│ - plot_lib: str          │
│ - style: dict            │
├──────────────────────────┤
│ + create_graph(data)     │
│ + export(path, format)   │
│ - _configure_axes()      │
└──────────────────────────┘
```

---

## 3. Component Architecture

### 3.1 Translation Agent Architecture

**Base Agent Interface:**
```python
from abc import ABC, abstractmethod
from typing import Optional

class TranslationAgent(ABC):
    """Base class for all translation agents."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.source_lang: str
        self.target_lang: str

    @abstractmethod
    def translate(self, text: str) -> str:
        """Translate text from source to target language."""
        pass

    def validate_input(self, text: str) -> bool:
        """Validate input text."""
        return len(text.strip()) > 0
```

**Agent Implementations:**
- `EnglishToFrenchAgent`: Translates EN→FR
- `FrenchToHebrewAgent`: Translates FR→HE
- `HebrewToEnglishAgent`: Translates HE→EN

**Agent Communication Flow:**
```
Input Text
    │
    ▼
┌────────────────┐
│ Agent 1: EN→FR │
│ (Claude API)   │
└───────┬────────┘
        │ French Text
        ▼
┌────────────────┐
│ Agent 2: FR→HE │
│ (Claude API)   │
└───────┬────────┘
        │ Hebrew Text
        ▼
┌────────────────┐
│ Agent 3: HE→EN │
│ (Claude API)   │
└───────┬────────┘
        │
        ▼
    Output Text
```

### 3.2 Error Injection Architecture

**Error Strategies:**
1. **Character Substitution:** Replace characters with nearby keyboard keys
2. **Character Deletion:** Remove random characters
3. **Character Transposition:** Swap adjacent characters
4. **Word-Level Errors:** Misspell entire words

**Error Distribution:**
```python
class ErrorInjector:
    def inject(self, text: str, error_rate: float) -> str:
        words = text.split()
        num_errors = int(len(words) * error_rate)
        error_positions = random.sample(range(len(words)), num_errors)

        for pos in error_positions:
            words[pos] = self._apply_random_error(words[pos])

        return ' '.join(words)
```

### 3.3 Metrics Calculation Architecture

**Embedding Pipeline:**
```
Original Text → Embedder → Vector A (768-dim)
Final Text    → Embedder → Vector B (768-dim)
                            │
                            ▼
                    Distance Calculator
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    Cosine Similarity  Euclidean Dist  Manhattan Dist
```

**Vector Distance Formulas:**
- **Cosine Distance:** `1 - (A·B) / (||A|| ||B||)`
- **Euclidean Distance:** `sqrt(Σ(A[i] - B[i])²)`

---

## 4. Data Architecture

### 4.1 Data Models

**Input Data Structure:**
```json
{
  "sentences": [
    {
      "id": "sent_001",
      "text": "The quick brown fox jumps over the lazy dog...",
      "word_count": 15,
      "language": "en"
    }
  ]
}
```

**Experiment Result Structure:**
```json
{
  "experiment_id": "exp_20250123_001",
  "timestamp": "2025-01-23T10:30:00Z",
  "sentence_id": "sent_001",
  "original_text": "The quick brown fox...",
  "error_variants": [
    {
      "error_rate": 0.25,
      "text_with_errors": "Teh qiuck brown fox...",
      "translations": {
        "french": "Le renard brun rapide...",
        "hebrew": "השועל החום המהיר...",
        "english_final": "The quick brow fox..."
      },
      "metrics": {
        "cosine_distance": 0.042,
        "euclidean_distance": 1.23,
        "cosine_similarity": 0.958
      },
      "embeddings": {
        "original": [0.123, -0.456, ...],
        "final": [0.118, -0.451, ...]
      }
    }
  ]
}
```

### 4.2 Data Flow Diagram

```
┌─────────────┐
│ Input Files │
│             │
│ sentences.  │
│    json     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Error Injection  │
│                  │
│ • 0% errors      │
│ • 25% errors     │
│ • 50% errors     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐      ┌─────────────────┐
│ Translation      │─────→│ Intermediate    │
│ Pipeline         │      │ Results Store   │
│                  │      │                 │
│ EN→FR→HE→EN     │      │ • Translations  │
└────────┬─────────┘      │ • Logs          │
         │                └─────────────────┘
         ▼
┌──────────────────┐
│ Vector Distance  │
│ Calculation      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐      ┌─────────────────┐
│ Results          │─────→│ Output Files    │
│ Aggregation      │      │                 │
└────────┬─────────┘      │ • metrics.csv   │
         │                │ • results.json  │
         ▼                │ • graph.png     │
┌──────────────────┐      └─────────────────┘
│ Visualization    │
│ Generation       │
└──────────────────┘
```

### 4.3 File Structure

```
project/
├── data/
│   ├── input/
│   │   ├── sentences.json          # Original sentences
│   │   └── config.yaml              # Experiment configuration
│   ├── intermediate/
│   │   ├── error_variants.json     # Sentences with injected errors
│   │   └── translations.json       # All translation steps
│   └── output/
│       ├── metrics.csv              # Distance measurements
│       ├── results.json             # Complete experiment results
│       ├── graph.png                # Visualization
│       └── embeddings.pkl           # Cached embeddings
├── logs/
│   └── experiment_YYYYMMDD.log
└── cache/
    └── api_responses.db             # Optional API response cache
```

---

## 5. Deployment Architecture

### 5.1 Local Development Environment

```
Developer Machine
├── Python 3.9+ Virtual Environment
│   ├── translation_pipeline/       (source code)
│   ├── requirements.txt
│   └── .env                         (API keys)
├── Data Directory
│   └── (input/output files)
└── Configuration
    └── config.yaml
```

### 5.2 Deployment Diagram

```
┌────────────────────────────────────────────────────┐
│              Developer Workstation                 │
│                                                    │
│  ┌──────────────────────────────────────────┐    │
│  │  Python Virtual Environment              │    │
│  │                                          │    │
│  │  ┌────────────────────────────────────┐ │    │
│  │  │   CLI Application                  │ │    │
│  │  │   (main.py)                        │ │    │
│  │  └────────────┬───────────────────────┘ │    │
│  │               │                          │    │
│  │  ┌────────────▼───────────────────────┐ │    │
│  │  │   Core Libraries                   │ │    │
│  │  │   • agents/                        │ │    │
│  │  │   • metrics/                       │ │    │
│  │  │   • visualization/                 │ │    │
│  │  └────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  ┌──────────────────────────────────────────┐    │
│  │  Local File System                       │    │
│  │  • data/                                 │    │
│  │  • logs/                                 │    │
│  │  • cache/                                │    │
│  └──────────────────────────────────────────┘    │
└────────────────┬───────────────────────────────────┘
                 │
                 │ HTTPS
                 │
        ┌────────▼──────────┐
        │   External APIs   │
        │                   │
        │ ┌───────────────┐ │
        │ │ Claude API    │ │
        │ │ (Translation) │ │
        │ └───────────────┘ │
        │                   │
        │ ┌───────────────┐ │
        │ │ OpenAI API    │ │
        │ │ (Embeddings)  │ │
        │ └───────────────┘ │
        └───────────────────┘
```

### 5.3 Environment Configuration

**.env file structure:**
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Model Configuration
TRANSLATION_MODEL=claude-3-5-sonnet-20250929
EMBEDDING_MODEL=text-embedding-3-small

# Experiment Settings
DEFAULT_ERROR_RATES=0,10,25,35,50
RANDOM_SEED=42

# Performance Tuning
MAX_RETRIES=3
TIMEOUT_SECONDS=30
CACHE_ENABLED=true
```

---

## 6. Operational Architecture

### 6.1 Logging Architecture

**Log Levels and Categories:**
```
DEBUG   → Detailed agent I/O, API requests/responses
INFO    → Pipeline progress, major steps
WARNING → Retries, fallback mechanisms
ERROR   → Failed translations, API errors
CRITICAL→ System failures, data corruption
```

**Log Format:**
```
[2025-01-23 10:30:15] [INFO] [EnglishToFrenchAgent] Translation started
[2025-01-23 10:30:16] [DEBUG] [API] Request to Claude: {"text": "..."}
[2025-01-23 10:30:17] [DEBUG] [API] Response: {"translation": "..."}
[2025-01-23 10:30:17] [INFO] [EnglishToFrenchAgent] Translation completed (1.2s)
```

### 6.2 Error Handling Strategy

**Error Categories and Responses:**

| Error Type | Example | Recovery Strategy |
|------------|---------|-------------------|
| API Rate Limit | 429 Too Many Requests | Exponential backoff, retry after delay |
| API Timeout | Request timeout after 30s | Retry with increased timeout |
| Invalid Input | Empty string | Validate and reject with error message |
| Network Error | Connection refused | Retry up to 3 times, then fail |
| Invalid API Key | 401 Unauthorized | Fail immediately with clear message |
| Model Unavailable | 503 Service Unavailable | Retry with different model if configured |

**Retry Logic:**
```python
def translate_with_retry(text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return agent.translate(text)
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
        except TransientError:
            continue
        except PermanentError as e:
            raise
    raise MaxRetriesExceeded()
```

### 6.3 Monitoring and Observability

**Metrics to Track:**
- API call count and latency
- Error rate per agent
- Total experiment duration
- Cache hit rate
- Embedding calculation time
- Token usage and costs
- Test coverage percentage
- Code quality scores (linting)

**Progress Reporting:**
```
Running Experiment: 0% errors
[████████████████████████████████████████] 100% Complete
Translation chain: 4.2s | Metrics: 0.8s | Total: 5.0s
Cost: $0.054 | Tokens: 1800

Running Experiment: 25% errors
[████████████████████████████████████████] 100% Complete
Translation chain: 4.5s | Metrics: 0.9s | Total: 5.4s
Cost: $0.056 | Tokens: 1850
```

### 6.4 Cost Tracking Architecture

**Cost Tracker Component:**
```python
class CostTracker:
    """Track API usage and costs."""

    def __init__(self):
        self.calls: List[APICall] = []
        self.pricing = {
            "claude-3-5-sonnet": {
                "input": 3.00 / 1_000_000,   # per token
                "output": 15.00 / 1_000_000
            }
        }

    def log_call(
        self,
        agent: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        experiment_id: str
    ):
        """Log an API call with token usage."""
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        self.calls.append(APICall(
            timestamp=datetime.now(),
            agent=agent,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            experiment_id=experiment_id
        ))

    def generate_report(self) -> pd.DataFrame:
        """Generate cost analysis report."""
        return pd.DataFrame([
            {
                "date": call.timestamp.date(),
                "agent": call.agent,
                "model": call.model,
                "input_tokens": call.input_tokens,
                "output_tokens": call.output_tokens,
                "cost_usd": call.cost,
                "experiment_id": call.experiment_id
            }
            for call in self.calls
        ])
```

**Cost Monitoring Flow:**
```
API Call
    │
    ▼
┌────────────────┐
│ Agent wraps    │
│ API client     │
└───────┬────────┘
        │ Captures tokens
        ▼
┌────────────────┐
│ CostTracker    │
│ logs usage     │
└───────┬────────┘
        │
        ▼
┌────────────────┐      ┌─────────────────┐
│ In-memory      │─────→│ Reports         │
│ accumulation   │      │ (CSV export)    │
└────────────────┘      └─────────────────┘
```

### 6.5 Prompt Engineering Log Architecture

**Log Structure:**
```markdown
# Prompt Engineering Log

## Entry 001: English to French Translation
**Date:** 2025-01-23
**Goal:** Accurate translation preserving meaning even with spelling errors
**Model:** claude-3-5-sonnet-20250929

**Prompt:**
```
You are a professional translator. Translate the following English text to French.
The text may contain spelling errors - infer the intended meaning.

Text: {text}

Provide only the French translation, no explanations.
```

**Sample Input:** "The qiuck brown fox jumps over the lazy dog"
**Sample Output:** "Le renard brun rapide saute par-dessus le chien paresseux"

**Analysis:**
- ✅ Handled spelling error "qiuck" correctly
- ✅ Natural French phrasing
- ⚠️  Could test with more severe errors

**Iterations:**
v1: Initial prompt (above)
v2: (future) Add instruction about preserving tone
```

**Storage Location:** `docs/prompts.md`

---

## 7. Architectural Decision Records (ADRs)

### ADR-001: Use Python for Implementation

**Status:** Accepted

**Context:**
Need to choose primary implementation language for CLI, agents, and analysis.

**Decision:**
Implement entire system in Python 3.9+.

**Rationale:**
- Rich ecosystem for ML/NLP (sentence-transformers, numpy, pandas)
- Excellent API client libraries (anthropic, openai)
- Strong visualization libraries (matplotlib, plotly)
- Familiar to research community
- Quick prototyping and iteration

**Consequences:**
- Positive: Fast development, extensive libraries
- Negative: Slower than compiled languages (acceptable for this use case)
- Mitigation: Use numpy/scipy for performance-critical calculations

---

### ADR-002: Use Claude API for Translation

**Status:** Accepted

**Context:**
Need reliable translation service for EN→FR→HE→EN chain.

**Decision:**
Use Anthropic Claude API as primary translation backend.

**Rationale:**
- High-quality multilingual support
- Consistent API across languages
- Flexible prompting for translation tasks
- Good error handling and rate limiting
- Available through standard API

**Alternatives Considered:**
- Google Translate API: Less flexible, harder to control translation style
- OpenAI GPT: Viable alternative, kept as fallback option
- Dedicated translation services: More expensive, less flexible

**Consequences:**
- Positive: High translation quality, flexible prompting
- Negative: API costs, rate limits
- Mitigation: Implement caching, retry logic

---

### ADR-003: Cosine Distance as Primary Metric

**Status:** Accepted

**Context:**
Need to quantify semantic similarity between original and final sentences.

**Decision:**
Use cosine distance between sentence embeddings as primary quality metric.

**Rationale:**
- Standard metric for semantic similarity in NLP
- Normalized (0-2 range), easier to interpret
- Less sensitive to embedding magnitude than euclidean distance
- Well-understood in research community

**Alternatives Considered:**
- Euclidean distance: More sensitive to magnitude differences
- BLEU score: Designed for exact matches, not semantic similarity
- BERTScore: More complex, requires additional setup

**Consequences:**
- Positive: Interpretable, comparable across experiments
- Negative: Requires consistent embedding model
- Mitigation: Document embedding model version

---

### ADR-004: Local File-Based Storage

**Status:** Accepted

**Context:**
Need to persist experiment results and intermediate data.

**Decision:**
Use local JSON and CSV files for data storage.

**Rationale:**
- Simple, no database setup required
- Human-readable for debugging
- Easy to version control (git)
- Sufficient for research workload (100s of sentences)
- Portable across systems

**Alternatives Considered:**
- SQLite: Overhead not justified for small dataset
- Cloud storage: Unnecessary complexity
- In-memory only: Results would be lost

**Consequences:**
- Positive: Simple, portable, version-controllable
- Negative: Not suitable for large-scale production
- Mitigation: Document file formats clearly

---

### ADR-005: CLI-Only Interface

**Status:** Accepted

**Context:**
Need user interface for running experiments and viewing results.

**Decision:**
Implement command-line interface only (no GUI, no web UI).

**Rationale:**
- Requirement explicitly specified CLI
- Scriptable and automatable
- Lower development complexity
- Standard for research tools
- Easy integration with workflows

**Consequences:**
- Positive: Fast development, scriptable, automatable
- Negative: Less accessible to non-technical users
- Mitigation: Provide clear documentation and examples

---

### ADR-006: Sentence-Transformers for Embeddings

**Status:** Accepted

**Context:**
Need to generate semantic embeddings for vector distance calculation.

**Decision:**
Use sentence-transformers library with all-MiniLM-L6-v2 model as default.

**Rationale:**
- Fast inference (CPU-friendly)
- Good semantic quality for similarity tasks
- Open-source, no API costs
- 384-dimensional vectors (compact)
- Well-maintained library

**Alternatives Considered:**
- OpenAI embeddings: Requires API calls, costs money
- Universal Sentence Encoder: Larger model, slower
- Custom-trained embeddings: Unnecessary complexity

**Consequences:**
- Positive: Free, fast, good quality
- Negative: Requires local model download (~80MB)
- Mitigation: Auto-download on first run, cache embeddings

---

### ADR-007: Sequential Agent Execution

**Status:** Accepted

**Context:**
Translation agents can be executed sequentially or in parallel.

**Decision:**
Execute agents sequentially in strict order: EN→FR→HE→EN.

**Rationale:**
- Translation chain is inherently sequential (output of N is input to N+1)
- Parallel execution not applicable
- Simpler implementation and debugging
- Preserves translation chain integrity

**Consequences:**
- Positive: Clear execution flow, easier debugging
- Negative: Cannot leverage parallelism (not applicable anyway)

---

## 8. API Specifications

### 8.1 CLI API

**Command Structure:**
```bash
translation-pipeline [COMMAND] [OPTIONS]
```

**Commands:**

#### `translate`
Run translation pipeline on input sentences.

```bash
translation-pipeline translate \
  --input sentences.json \
  --output results.json \
  --error-rates 0,10,25,50 \
  --seed 42 \
  --verbose
```

**Options:**
- `--input, -i`: Path to input sentences file (JSON)
- `--output, -o`: Path to output results file (JSON)
- `--error-rates, -e`: Comma-separated error rates (default: 0,25,50)
- `--seed, -s`: Random seed for reproducibility (default: 42)
- `--verbose, -v`: Enable verbose logging
- `--cache/--no-cache`: Enable/disable API response caching

#### `analyze`
Calculate vector distances from results file.

```bash
translation-pipeline analyze \
  --results results.json \
  --output metrics.csv \
  --embedding-model all-MiniLM-L6-v2
```

**Options:**
- `--results, -r`: Path to translation results file
- `--output, -o`: Path to output metrics file (CSV)
- `--embedding-model, -m`: Embedding model to use
- `--distance-metric`: Metric to calculate (cosine, euclidean, both)

#### `visualize`
Generate visualization graphs.

```bash
translation-pipeline visualize \
  --metrics metrics.csv \
  --output graph.png \
  --title "Translation Quality vs Error Rate"
```

**Options:**
- `--metrics, -m`: Path to metrics CSV file
- `--output, -o`: Path to output graph file (PNG/SVG/PDF)
- `--title, -t`: Graph title
- `--style`: Graph style (seaborn, ggplot, default)
- `--dpi`: Image resolution (default: 300)

#### `run-experiment`
Run complete experiment (translate + analyze + visualize).

```bash
translation-pipeline run-experiment \
  --input sentences.json \
  --output-dir ./results \
  --error-rates 0,10,20,30,40,50 \
  --seed 42
```

**Options:**
- `--input, -i`: Input sentences file
- `--output-dir, -d`: Output directory for all results
- `--error-rates, -e`: Error rates to test
- `--seed, -s`: Random seed
- `--skip-viz`: Skip visualization generation

---

### 8.2 Internal API Specifications

**Translation Agent Interface:**
```python
class TranslationAgent:
    def translate(self, text: str) -> str:
        """
        Translate text from source to target language.

        Args:
            text: Input text in source language

        Returns:
            Translated text in target language

        Raises:
            ValueError: If text is empty or invalid
            APIError: If translation service fails
        """
        pass
```

**Error Injector Interface:**
```python
class ErrorInjector:
    def inject(
        self,
        text: str,
        error_rate: float,
        seed: Optional[int] = None
    ) -> str:
        """
        Inject spelling errors into text.

        Args:
            text: Original text
            error_rate: Percentage of words to corrupt (0.0-1.0)
            seed: Random seed for reproducibility

        Returns:
            Text with injected errors

        Raises:
            ValueError: If error_rate not in valid range
        """
        pass
```

**Metrics Calculator Interface:**
```python
class VectorMetrics:
    def calculate_distance(
        self,
        text1: str,
        text2: str,
        metric: str = "cosine"
    ) -> float:
        """
        Calculate vector distance between two texts.

        Args:
            text1: First text
            text2: Second text
            metric: Distance metric ("cosine", "euclidean")

        Returns:
            Distance value (float)

        Raises:
            ValueError: If metric not supported
        """
        pass
```

---

## 9. Security Architecture

### 9.1 API Key Management

**Storage:**
- API keys stored in `.env` file (not version controlled)
- `.gitignore` must include `.env`
- Environment variables loaded at runtime
- No keys hardcoded in source code

**Access Control:**
- File permissions: `.env` should be 600 (owner read/write only)
- Keys never logged or printed to console
- Keys not included in error messages

### 9.2 Input Validation

**Text Input Validation:**
```python
def validate_input(text: str) -> bool:
    # Check for empty input
    if not text or not text.strip():
        raise ValueError("Empty input text")

    # Check for excessive length (prevent API abuse)
    if len(text) > 10000:
        raise ValueError("Text exceeds maximum length")

    # Check for minimum word count
    words = text.split()
    if len(words) < 15:
        raise ValueError("Sentence must contain at least 15 words")

    return True
```

**File Path Validation:**
- Prevent path traversal attacks
- Validate file extensions
- Check write permissions before output

### 9.3 Dependency Security

**Requirements Management:**
- Pin all dependency versions in requirements.txt
- Regular security audits with `pip-audit`
- Minimal dependency footprint
- Avoid dependencies with known vulnerabilities

**Example requirements.txt:**
```
anthropic==0.18.1
openai==1.12.0
sentence-transformers==2.3.1
matplotlib==3.8.2
pandas==2.1.4
numpy==1.26.3
click==8.1.7
python-dotenv==1.0.0
pytest==7.4.4
```

### 9.4 Data Privacy

- No user data sent to external services except translation APIs
- Translation APIs: Anthropic and OpenAI privacy policies apply
- No persistent logging of sensitive content
- Local data storage only (no cloud sync without user control)

---

## 10. Technical Constraints

### 10.1 Performance Constraints

- **API Rate Limits:**
  - Claude API: ~50 requests/minute (varies by tier)
  - OpenAI API: ~60 requests/minute (varies by tier)
  - Mitigation: Implement exponential backoff

- **Memory Constraints:**
  - Embedding model: ~500MB RAM
  - Runtime overhead: ~1GB for typical workload
  - Maximum simultaneous experiments: Limited by available RAM

- **Execution Time:**
  - Translation per sentence: ~2-4 seconds per agent = 12s total
  - Embedding calculation: ~0.5s per sentence
  - Full experiment (6 error rates): ~90 seconds per sentence

### 10.2 Platform Constraints

- **Operating Systems:** Linux, macOS, Windows (WSL recommended)
- **Python Version:** 3.9, 3.10, 3.11, 3.12
- **Disk Space:** ~1GB for models and cache
- **Network:** Internet connection required for API access

### 10.3 External Service Dependencies

- **Anthropic Claude API:** Required for translation
  - Fallback: OpenAI API (requires code modification)

- **Embedding Model:** Sentence-transformers (local) or OpenAI embeddings
  - Preference: Local model (no API dependency)

### 10.4 Scalability Constraints

- **Current Design:** Optimized for 1-100 sentences
- **Batch Processing:** Linear scaling (no parallelization of translation chain)
- **Storage:** File-based storage not suitable for >10,000 sentences
- **Future Scaling:** Would require database, queueing system, distributed agents

---

## 11. Quality Assurance Architecture

### 11.1 Testing Architecture

**Test Pyramid:**
```
        ▲
       ╱ ╲
      ╱   ╲       E2E Tests (5%)
     ╱─────╲      • Full pipeline workflows
    ╱       ╲     • Real API integration
   ╱─────────╲
  ╱           ╲   Integration Tests (20%)
 ╱─────────────╲  • Agent chains
╱               ╲ • Pipeline execution
─────────────────
                  Unit Tests (75%)
                  • Individual functions
                  • Error injection logic
                  • Metrics calculation
```

**Test Organization:**
```
tests/
├── unit/
│   ├── test_error_injector.py    # Error injection strategies
│   ├── test_agents.py             # Agent logic (mocked APIs)
│   ├── test_metrics.py            # Distance calculations
│   ├── test_embeddings.py         # Embedding generation
│   └── test_cost_tracker.py       # Cost tracking logic
├── integration/
│   ├── test_pipeline.py           # Agent chain execution
│   ├── test_experiment_runner.py  # Full experiment flow
│   └── test_data_persistence.py   # File I/O operations
├── e2e/
│   └── test_full_workflow.py      # Complete workflow with real APIs
├── fixtures/
│   ├── sample_sentences.json      # Test data
│   └── mock_responses.json        # Mocked API responses
└── conftest.py                    # Shared fixtures
```

**Coverage Configuration (pytest.ini):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
    --verbose
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

### 11.2 Code Quality Architecture

**Linting Pipeline:**
```
Code Changes
    │
    ▼
┌──────────────┐
│ Black        │  Code formatting
│ (formatter)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ flake8       │  Style guide enforcement
│              │  • PEP 8 compliance
└──────┬───────┘  • Line length (100 chars)
       │          • Complexity checks
       ▼
┌──────────────┐
│ pylint       │  Code analysis
│              │  • Code smells
└──────┬───────┘  • Best practices
       │          • Documentation
       ▼
┌──────────────┐
│ mypy         │  Type checking
│ (optional)   │
└──────┬───────┘
       │
       ▼
   ✅ Pass → Commit
   ❌ Fail → Fix Issues
```

**Quality Gates:**
- Linting: Zero warnings
- Test coverage: ≥70%
- Type hints: All public functions
- Docstrings: All public classes/functions
- Complexity: Max cyclomatic complexity = 10

### 11.3 Git Workflow Architecture

**Branch Strategy:**
```
main (stable)
  │
  ├─ develop (integration)
  │    │
  │    ├─ feature/translation-agents
  │    ├─ feature/error-injection
  │    ├─ feature/metrics-calculation
  │    └─ feature/visualization
  │
  └─ hotfix/critical-bug (if needed)
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, test, refactor, chore
Example:
```
feat(agents): add Hebrew to English translation agent

Implement HebrewToEnglishAgent with Claude API integration.
Includes retry logic and error handling.

Closes #12
```

### 11.4 Documentation Architecture

**Documentation Structure:**
```
docs/
├── PRD.md                          # Product requirements
├── ARCHITECTURE.md                 # This document
├── prompts.md                      # Prompt engineering log
├── ADRs/                          # Architecture decisions
│   ├── 001-use-python.md
│   ├── 002-claude-api.md
│   ├── 003-cosine-distance.md
│   ├── 004-local-storage.md
│   ├── 005-cli-interface.md
│   ├── 006-sentence-transformers.md
│   └── 007-sequential-execution.md
├── api/                           # API documentation
│   ├── agents.md
│   ├── metrics.md
│   └── cli.md
└── guides/                        # User guides
    ├── getting-started.md
    ├── running-experiments.md
    └── interpreting-results.md
```

**ADR Template:**
```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue we're facing?

## Decision
What is the change we're proposing?

## Rationale
Why this decision? What are the benefits?

## Alternatives Considered
What other options did we evaluate?

## Consequences
### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Risks
- Risk 1 (with mitigation)

## Compliance
How does this align with project standards?
```

---

## 12. Extensibility Architecture

### 12.1 Extension Points

**1. Translation Providers**
```python
# Easy to add new translation services
class GoogleTranslateAgent(TranslationAgent):
    """Google Translate implementation."""
    def translate(self, text: str) -> str:
        # Use Google Translate API
        pass

# Register new agent
agent_registry.register("google", GoogleTranslateAgent)
```

**2. Error Injection Strategies**
```python
# Add new error types
class PhoneticErrorStrategy(ErrorStrategy):
    """Errors based on phonetic similarity."""
    def apply(self, word: str) -> str:
        # Replace with phonetically similar misspelling
        pass

error_injector.add_strategy("phonetic", PhoneticErrorStrategy())
```

**3. Distance Metrics**
```python
# Add new similarity measures
class BERTScoreMetric(DistanceMetric):
    """BERTScore-based semantic similarity."""
    def calculate(self, text1: str, text2: str) -> float:
        # Use BERTScore
        pass

metrics_calculator.register("bertscore", BERTScoreMetric())
```

**4. Visualization Formats**
```python
# Add new graph types
class HeatmapVisualizer(Visualizer):
    """Generate heatmap of error rates vs sentences."""
    def generate(self, data: pd.DataFrame) -> Figure:
        # Create heatmap
        pass

viz_factory.register("heatmap", HeatmapVisualizer())
```

### 12.2 Plugin Architecture

**Plugin Interface:**
```python
class Plugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def initialize(self, config: Dict) -> None:
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality."""
        pass
```

**Plugin Discovery:**
```python
# Plugins placed in plugins/ directory
# Auto-discovered and loaded at runtime
plugin_manager = PluginManager()
plugin_manager.discover("plugins/")
plugin_manager.load_all()
```

### 12.3 Configuration-Driven Extensions

**config.yaml:**
```yaml
agents:
  - type: claude
    source: en
    target: fr
    model: claude-3-5-sonnet
  - type: claude
    source: fr
    target: he
    model: claude-3-5-sonnet
  # Easy to add new agent
  - type: google
    source: he
    target: en
    api_key: ${GOOGLE_API_KEY}

error_strategies:
  - substitution
  - deletion
  - transposition
  # Add new strategy
  - phonetic

metrics:
  - cosine
  - euclidean
  # Add new metric
  - bertscore

visualizations:
  - line_plot
  - scatter_plot
  # Add new visualization
  - heatmap
```

---

## 13. Appendix

### 13.1 Technology Alternatives Matrix

| Component | Primary Choice | Alternative 1 | Alternative 2 |
|-----------|---------------|---------------|---------------|
| Translation API | Claude | OpenAI GPT | Google Translate |
| Embeddings | sentence-transformers | OpenAI embeddings | Universal Sentence Encoder |
| CLI Framework | Click | argparse | Typer |
| Visualization | Matplotlib | Plotly | Seaborn |
| Data Format | JSON + CSV | SQLite | Parquet |

### 11.2 System Capacity Planning

| Metric | Small Scale | Medium Scale | Large Scale |
|--------|-------------|--------------|-------------|
| Sentences | 1-10 | 10-100 | 100-1000 |
| Error Rates | 3-5 | 5-10 | 10-20 |
| Total API Calls | 30-50 | 300-1000 | 3000-20000 |
| Execution Time | 5-10 min | 30-60 min | 5-10 hours |
| Storage Required | <10MB | <100MB | <1GB |
| RAM Required | 2GB | 4GB | 8GB |

### 11.3 Future Architecture Considerations

**Potential Enhancements:**
1. **Distributed Execution:** Agent pool with load balancing
2. **Database Backend:** PostgreSQL for structured data
3. **Caching Layer:** Redis for API response caching
4. **Web Interface:** FastAPI + React dashboard
5. **Real-time Monitoring:** Prometheus + Grafana
6. **Containerization:** Docker for reproducible environments
7. **CI/CD Pipeline:** GitHub Actions for testing and deployment

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-23 | Architecture Team | Initial draft |

---

**Approval Signatures**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Architect | | | |
| Lead Developer | | | |
| Product Owner | | | |
