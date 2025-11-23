# Architecture Document
## Multi-Step Agent System for Translation Analysis

### Document Information
- **Version:** 2.0
- **Date:** 2025-11-23
- **System Name:** Translation Quality Analysis System
- **Architecture Status:** Implemented

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Component Architecture](#3-component-architecture)
4. [Data Architecture](#4-data-architecture)
5. [Execution Modes](#5-execution-modes)
6. [Results Organization](#6-results-organization)
7. [Technology Stack](#7-technology-stack)
8. [Architecture Decision Records](#8-architecture-decision-records)

---

## 1. System Overview

### 1.1 Purpose
The Translation Quality Analysis System measures how spelling errors affect translation quality through a 3-stage translation chain (EN→FR→HE→EN), demonstrating the remarkable robustness of modern LLMs in error correction and semantic preservation.

### 1.2 Key Architectural Principles

1. **Hybrid Architecture**: SKILL files for translation + Python for automation/analysis
2. **Simplicity**: Pre-corrupted inputs eliminate error injection complexity
3. **Flexibility**: Two execution modes (API or Claude Code)
4. **Organization**: Results organized by date and input type
5. **Automation**: Single-command execution with full setup

### 1.3 System Goals

✅ Demonstrate perfect AI error correction (0-50% error rates)
✅ Provide publication-quality research results
✅ Enable reproducible experiments
✅ Minimize manual intervention
✅ Comprehensive documentation

---

## 2. High-Level Architecture

### 2.1 System Context Diagram

```
┌────────────────────────────────────────────────────────────┐
│                        USER                                 │
│                                                            │
│  - M.Sc. Student                                          │
│  - Researcher                                             │
│  - Educator                                               │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  │ ./run_experiment.sh
                  ↓
┌────────────────────────────────────────────────────────────┐
│         Translation Quality Analysis System                 │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Automation   │  │ Translation  │  │ Analysis     │   │
│  │ Layer        │  │ Agents       │  │ Layer        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  │ Results
                  ↓
┌────────────────────────────────────────────────────────────┐
│           results/YYYY-MM-DD/input_name/                    │
│  - JSON results                                            │
│  - CSV metrics                                             │
│  - PNG visualizations                                      │
└────────────────────────────────────────────────────────────┘

External Systems:
┌────────────────┐        ┌────────────────┐
│ Anthropic API  │        │ Sentence       │
│ (optional)     │        │ Transformers   │
└────────────────┘        └────────────────┘
```

### 2.2 Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Host System (Mac/Linux/WSL)                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Python Virtual Environment                  │   │
│  │                                                         │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐         │   │
│  │  │ CLI       │  │ Metrics   │  │ Visual    │         │   │
│  │  │ (Click)   │  │ Engine    │  │ Engine    │         │   │
│  │  └───────────┘  └───────────┘  └───────────┘         │   │
│  │        │              │                 │              │   │
│  │        │              │                 │              │   │
│  │  ┌──────────────────────────────────────────┐         │   │
│  │  │        Pipeline Orchestrator            │         │   │
│  │  └──────────────────────────────────────────┘         │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              SKILL-Based Agents                         │   │
│  │  (Markdown files executed by Claude)                    │   │
│  │                                                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐               │   │
│  │  │ EN→FR   │→│ FR→HE   │→│ HE→EN   │               │   │
│  │  │ Agent   │  │ Agent   │  │ Agent   │               │   │
│  │  └─────────┘  └─────────┘  └─────────┘               │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Data Storage                               │   │
│  │                                                         │   │
│  │  • Input Files (JSON)                                   │   │
│  │  • Results (JSON, CSV, PNG)                             │   │
│  │  • Configuration (.env)                                 │   │
│  │  • Logs                                                 │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Architecture

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Automation Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  run_experiment.sh                                    │  │
│  │  - Environment setup                                  │  │
│  │  - Dependency management                              │  │
│  │  - Mode detection (API/Claude Code)                   │  │
│  │  - Orchestration                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Translation Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SKILL Agents (agents/*.md)                           │  │
│  │  - agent-en-to-fr: Error correction + translation     │  │
│  │  - agent-fr-to-he: Semantic translation               │  │
│  │  - agent-he-to-en: Back translation                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Execution Modules                                    │  │
│  │  - run_with_agents.py (API mode)                      │  │
│  │  - run_with_claude_code.py (Claude Code mode)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py (CLI)                                        │  │
│  │  - Analyze command                                    │  │
│  │  - Info command                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Metrics Engine                                       │  │
│  │  - Embedder: Generate 384-dim vectors                 │  │
│  │  - VectorMetrics: Calculate distances                 │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Visualization Engine                                 │  │
│  │  - GraphPlotter: Generate PNG graphs                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Details

#### 3.2.1 Automation Layer

**run_experiment.sh**
- Entry point for entire system
- Handles environment setup automatically
- Detects execution mode (API vs Claude Code)
- Orchestrates complete workflow
- User-friendly progress indicators

**Responsibilities**:
- Create `.env` from `example.env` if needed
- Create Python venv if needed
- Install dependencies
- Detect API key presence
- Run appropriate execution mode
- Invoke analysis automatically

#### 3.2.2 Translation Layer

**SKILL Agents** (`agents/*/SKILL.md`)

1. **agent-en-to-fr**
   - Input: English with spelling errors
   - Process: Context-aware error correction + translation
   - Output: Grammatically correct French
   - Key feature: Infers correct words from misspellings

2. **agent-fr-to-he**
   - Input: French text
   - Process: Semantic (not literal) translation
   - Output: Proper Hebrew grammar and syntax
   - Key feature: Maintains semantic meaning

3. **agent-he-to-en**
   - Input: Hebrew text
   - Process: Back translation to English
   - Output: Final English for comparison
   - Key feature: Completes the chain

**Execution Modules**

1. **run_with_agents.py** (API Mode)
   - Loads SKILL agent instructions
   - Calls Anthropic API for each translation
   - Fully automated execution
   - Saves results to new directory structure

2. **run_with_claude_code.py** (Claude Code Mode)
   - Generates formatted requests
   - User copies to Claude Code conversation
   - I (Claude) execute translations manually
   - Results saved automatically

#### 3.2.3 Analysis Layer

**main.py (CLI)**
- Command: `analyze` - Calculate metrics and generate graphs
- Command: `info` - System information
- Built with Click framework
- Comprehensive logging

**Metrics Engine** (`src/metrics/`)

1. **Embedder**
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - Dimension: 384
   - Backend: PyTorch (MPS on Mac, CUDA on GPU, CPU fallback)
   - Caching: Disabled for accuracy

2. **VectorMetrics**
   - Cosine Distance: `1 - cosine_similarity`
   - Cosine Similarity: `1.0 = perfect match`
   - Euclidean Distance: L2 norm
   - Manhattan Distance: L1 norm

**Visualization Engine** (`src/visualization/`)

1. **GraphPlotter**
   - X-axis: Error rate (0-50%)
   - Y-axis: Semantic distance
   - Format: PNG, 300 DPI
   - Styling: matplotlib + seaborn
   - Publication quality

---

## 4. Data Architecture

### 4.1 Data Flow

```
┌──────────────────────┐
│  Input JSON Files    │
│                      │
│  • sanity_check      │
│  • same_sentence     │
│  • different_sent    │
└──────┬───────────────┘
       │
       │ Read
       ↓
┌──────────────────────┐
│  Translation         │
│  Process             │
│                      │
│  Original → FR       │
│  FR → HE             │
│  HE → Final          │
└──────┬───────────────┘
       │
       │ Store
       ↓
┌──────────────────────┐
│  Results JSON        │
│                      │
│  • experiment_id     │
│  • timestamp         │
│  • results[]         │
└──────┬───────────────┘
       │
       │ Analyze
       ↓
┌──────────────────────┐
│  Metrics CSV         │
│                      │
│  • error_rate        │
│  • distances         │
│  • texts             │
└──────┬───────────────┘
       │
       │ Visualize
       ↓
┌──────────────────────┐
│  Graph PNG           │
│                      │
│  • error vs distance │
└──────────────────────┘
```

### 4.2 Data Formats

#### Input JSON
```json
{
  "sentences": [
    {
      "id": "test_case_id",
      "original": "Clean sentence",
      "misspelled": "Sentence with errors",
      "error_rate": 0.15,
      "word_count": 19
    }
  ],
  "metadata": {
    "version": "1.0",
    "type": "input_type",
    "total_sentences": 11
  }
}
```

#### Results JSON
```json
{
  "experiment_id": "unique_id",
  "timestamp": "2025-11-23T21:41:45",
  "mode": "claude_code_execution",
  "input_file": "input_name.json",
  "results": [
    {
      "id": "test_case_id",
      "original": "Original text",
      "misspelled": "Text with errors",
      "error_rate": 0.15,
      "french": "French translation",
      "hebrew": "Hebrew translation",
      "final": "Final English",
      "word_count": 19
    }
  ]
}
```

#### Metrics CSV
```csv
error_rate,cosine_distance,cosine_similarity,euclidean_distance,manhattan_distance,original,final,word_count
0.0,0.0,1.0,0.0,0.0,"Original text","Final text",19
```

### 4.3 File Organization

```
HW3/
├── data/
│   └── input/
│       ├── sanity_check.json
│       ├── same_sentence_progressive.json
│       └── different_sentences_progressive.json
│
├── results/
│   └── YYYY-MM-DD/
│       ├── sanity_check/
│       │   ├── request_HHMMSS.txt
│       │   ├── results_HHMMSS.json
│       │   ├── metrics_output.csv
│       │   └── error_vs_distance.png
│       ├── same_sentence_progressive/
│       └── different_sentences_progressive/
│
├── agents/
│   ├── agent-en-to-fr/SKILL.md
│   ├── agent-fr-to-he/SKILL.md
│   └── agent-he-to-en/SKILL.md
│
└── src/
    ├── main.py
    ├── run_with_agents.py
    ├── run_with_claude_code.py
    ├── metrics/
    ├── visualization/
    └── utils/
```

---

## 5. Execution Modes

### 5.1 Mode 1: API-Based (Automated)

**When**: User has `ANTHROPIC_API_KEY` in `.env`

**Flow**:
```
run_experiment.sh
    ↓
Detect API key ✓
    ↓
run_with_agents.py
    ↓
Load SKILL instructions
    ↓
For each test case:
  - Call Anthropic API (Agent 1: EN→FR)
  - Call Anthropic API (Agent 2: FR→HE)
  - Call Anthropic API (Agent 3: HE→EN)
    ↓
Save results JSON
    ↓
main.py analyze
    ↓
Generate metrics CSV + graph PNG
```

**Advantages**:
- Fully automated
- Fast execution (~2-3 minutes for 11 cases)
- No manual intervention

**Cost**: ~$0.02-0.05 per experiment

### 5.2 Mode 2: Claude Code (Manual)

**When**: No API key in `.env`

**Flow**:
```
run_experiment.sh
    ↓
Detect no API key
    ↓
run_with_claude_code.py
    ↓
Generate formatted request
    ↓
Display to user (copy/paste)
    ↓
User pastes to Claude Code
    ↓
I (Claude) execute:
  - Agent 1: EN→FR (error correction)
  - Agent 2: FR→HE (semantic translation)
  - Agent 3: HE→EN (back translation)
    ↓
I provide complete JSON
    ↓
Save results JSON
    ↓
main.py analyze (automatic)
    ↓
Generate metrics CSV + graph PNG
```

**Advantages**:
- No API key required
- Completely free
- Identical quality to API mode

**Effort**: User pastes one request, I do the rest

---

## 6. Results Organization

### 6.1 Directory Structure Rationale

**Problem**: Old structure (`results/api_run/`, `results/claude_code_run/`) made it hard to:
- Find results by date
- Compare same inputs across runs
- Organize multiple experiments

**Solution**: `results/YYYY-MM-DD/input_name/`

**Benefits**:
- ✅ Chronological organization
- ✅ Clear input separation
- ✅ Multiple runs per day (different timestamps)
- ✅ Easy to find and compare
- ✅ Scales well

### 6.2 Example Structure

```
results/
├── 2025-11-23/
│   ├── sanity_check/
│   │   ├── request_150000.txt
│   │   ├── results_150000.json
│   │   ├── metrics_output.csv
│   │   └── error_vs_distance.png
│   ├── same_sentence_progressive/
│   │   ├── request_160000.txt
│   │   ├── results_160000.json
│   │   ├── metrics_output.csv
│   │   └── error_vs_distance.png
│   └── different_sentences_progressive/
│       ├── request_214145.txt
│       ├── results_214145.json
│       ├── metrics_output.csv
│       └── error_vs_distance.png
└── 2025-11-24/
    └── ...
```

### 6.3 File Purposes

1. **request_HHMMSS.txt**: Reference of what was requested from Claude
2. **results_HHMMSS.json**: Complete translation chain outputs
3. **metrics_output.csv**: Calculated distances for analysis
4. **error_vs_distance.png**: Visual representation of results

---

## 7. Technology Stack

### 7.1 Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Translation** | SKILL (Markdown) | Agent definitions |
| **Execution** | Anthropic Claude API | Translation (API mode) |
| **Execution** | Claude Code | Translation (manual mode) |
| **Automation** | Bash | Workflow orchestration |
| **CLI** | Python 3.9+ + Click | Command-line interface |
| **Embeddings** | sentence-transformers | Vector representations |
| **ML Backend** | PyTorch 2.6+ | Embedding model backend |
| **Data** | Pandas 2.2+ | Data manipulation |
| **Visualization** | Matplotlib + Seaborn | Graph generation |
| **Config** | python-dotenv | Environment management |

### 7.2 Dependencies

```
anthropic>=0.40.0         # Claude API client
sentence-transformers     # Embedding models
torch>=2.6.0             # PyTorch backend
pandas>=2.2.0            # Data manipulation
matplotlib>=3.9.0        # Plotting
seaborn>=0.13.0          # Enhanced plots
click>=8.0.0             # CLI framework
python-dotenv>=1.0.0     # .env support
```

### 7.3 System Requirements

- **Python**: 3.9 or higher
- **OS**: macOS, Linux, Windows (WSL)
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 500MB for dependencies + embeddings
- **Network**: Required for API mode, optional for Claude Code mode

---

## 8. Architecture Decision Records

### ADR-001: SKILL-Based Agents vs Python Agents

**Status**: ACCEPTED

**Context**: Initial design used Python agents. User discovered SKILL-based agents in Claude Code examples.

**Decision**: Use SKILL-based agents (Markdown files)

**Rationale**:
- Native to Claude Code
- Simpler maintenance
- Better separation of concerns
- Easier to understand and modify
- No Python boilerplate

**Consequences**:
- ✅ Cleaner agent definitions
- ✅ Better documentation
- ✅ Easier debugging
- ❌ Requires Claude Code or API

### ADR-002: Remove Error Injection Module

**Status**: ACCEPTED

**Context**: Original design included dynamic error injection. User provides pre-corrupted sentences.

**Decision**: Remove error injection module entirely

**Rationale**:
- User controls error rates precisely
- Simpler architecture
- Eliminates complexity
- More reproducible (deterministic)

**Consequences**:
- ✅ Simpler codebase
- ✅ Faster execution
- ✅ More reproducible
- ❌ User must create input files

### ADR-003: Two Execution Modes

**Status**: ACCEPTED

**Context**: Not all users have Anthropic API keys

**Decision**: Support both API and Claude Code execution

**Rationale**:
- API mode: Fast, automated
- Claude Code mode: Free, accessible
- Both produce identical results
- Automatic mode detection

**Consequences**:
- ✅ No API key required
- ✅ Free option available
- ✅ Flexible execution
- ⚠️ Two code paths to maintain

### ADR-004: Results Directory Structure

**Status**: ACCEPTED

**Context**: Old structure (`results/api_run/`) hard to navigate

**Decision**: Use `results/YYYY-MM-DD/input_name/` structure

**Rationale**:
- Chronological organization
- Input-based grouping
- Easy to find experiments
- Scales well
- Clear separation

**Consequences**:
- ✅ Better organization
- ✅ Easy navigation
- ✅ Chronological order
- ✅ No naming conflicts

### ADR-005: Remove Demo Mode

**Status**: ACCEPTED

**Context**: Initial demo used word-by-word mapping. User found it unrealistic.

**Decision**: Remove demo mode, use only real AI agents

**Rationale**:
- Demo mode gave misleading results
- Word-by-word not representative
- Real agents demonstrate true capabilities
- Simplifies codebase

**Consequences**:
- ✅ Only real results
- ✅ Cleaner codebase
- ✅ More accurate
- ✅ Better research findings

### ADR-006: Hybrid Architecture (SKILL + Python)

**Status**: ACCEPTED

**Context**: Need agent intelligence + automation

**Decision**: SKILL for translation, Python for automation/analysis

**Rationale**:
- SKILL: Best for translation logic
- Python: Best for automation, metrics, visualization
- Clean separation of concerns
- Leverages strengths of each

**Consequences**:
- ✅ Best of both worlds
- ✅ Clear boundaries
- ✅ Maintainable
- ⚠️ Two languages

---

## 9. Security Architecture

### 9.1 Credential Management

- API keys stored in `.env` (gitignored)
- Never logged or printed
- Environment-based configuration
- No hardcoded secrets

### 9.2 Input Validation

- JSON schema validation
- File existence checks
- Path sanitization
- Error rate bounds (0-1)

### 9.3 Output Safety

- Results written atomically
- Directory permissions checked
- No arbitrary code execution
- Sandboxed Python environment

---

## 10. Performance Considerations

### 10.1 Bottlenecks

1. **Translation**: 2-4 seconds per agent call (API mode)
2. **Embeddings**: 0.5 seconds per text (CPU)
3. **I/O**: Minimal (JSON/CSV writes)

### 10.2 Optimizations

- Virtual environment for isolation
- Efficient embedding model (MiniLM)
- MPS/CUDA acceleration when available
- Minimal dependencies

### 10.3 Scalability

Current system handles:
- 1-23 test cases per run
- Multiple runs per day
- Historical results indefinitely
- Scales to hundreds of experiments

---

## 11. Extensibility

### 11.1 Adding New Languages

1. Create new SKILL agent in `agents/`
2. Update chain in execution scripts
3. No other changes needed

### 11.2 Adding New Metrics

1. Add metric calculation in `src/metrics/vector_metrics.py`
2. Update CSV output in `main.py`
3. Optionally update visualization

### 11.3 Adding New Input Types

1. Create JSON file in `data/input/`
2. No code changes needed
3. Automatic detection

---

## 12. Operational Architecture

### 12.1 Deployment

- No deployment needed (local execution)
- Virtual environment isolation
- One-command setup: `./run_experiment.sh`

### 12.2 Monitoring

- Console progress indicators
- Logging to `logs/` directory
- Error messages to stderr
- Success metrics in output

### 12.3 Backup

- Results in version control (optional)
- Input files in git
- SKILL agents in git
- Easy to backup `results/` directory

---

**Document Version:** 2.0
**Status:** Complete - System Fully Implemented
**Last Updated:** November 23, 2025
