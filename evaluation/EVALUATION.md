# Offline Evaluation System

> ⚠️ **INFRASTRUCTURE ONLY** — This is skeleton code. No real evaluations are performed.

## Purpose

This directory contains the **offline evaluation infrastructure** for the AI Operations Copilot. It defines:

- **Dataset contracts** — Schemas for labeled test data
- **Evaluator interfaces** — How quality will be measured
- **Runner orchestration** — How evaluations will be executed
- **Report formats** — How results will be stored
- **Version tracking** — Reproducibility metadata

## Why Offline Evaluation?

Offline evaluation allows us to:

1. **Measure quality** on labeled historical data
2. **Detect regressions** when code/prompts change
3. **Compare versions** of models and prompts
4. **Calibrate confidence** scores against actual accuracy

## What's Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| `datasets/` | Schema only | Contracts for labeled data |
| `runners/` | Interface only | Evaluator orchestration |
| `reports/` | Format only | JSON/Markdown output |
| `versioning.py` | Stub only | Version capture placeholders |
| `evaluators.py` | Stub only | Legacy evaluator stubs |

## What's Intentionally Missing

- ❌ Real datasets
- ❌ Computed metrics
- ❌ Thresholds
- ❌ Pass/fail logic
- ❌ Scoring decisions

These will be added when:
1. System is validated end-to-end
2. Labeling guidelines are established
3. Ground truth data is collected

## Directory Structure

```
/evaluation
├── __init__.py         # Package exports
├── evaluators.py       # Legacy evaluator stubs
├── versioning.py       # Version tracking
├── EVALUATION.md       # This file
├── datasets/
│   └── __init__.py     # Dataset schemas
├── runners/
│   └── __init__.py     # Evaluation runner
└── reports/
    └── __init__.py     # Report generation
```

## Evaluator Types (Planned)

### TriageAccuracyEvaluator
- Compares predicted vs. expected ticket classification
- Metrics: ticket_type match, severity match, escalation decision

### RetrievalQualityEvaluator
- Measures RAG retrieval quality
- Metrics: precision, recall, MRR

### DecisionQualityEvaluator
- Evaluates recommendation accuracy
- Metrics: action match, risk flag detection

## Dataset Schema

```python
@dataclass
class TicketDatasetItem:
    ticket_id: str
    ticket_data: Dict[str, Any]
    expected_triage: Dict[str, Any]
    expected_action: Optional[str]
    notes: Optional[str]
```

## Report Format

Reports include:
- **Metadata**: run_id, timestamps, versions
- **Summary**: total items, pass rates (when implemented)
- **Details**: per-item results (optional)
- **Errors**: any evaluation failures

## Version Tracking

For reproducibility, we track:
- `code_version` — Git commit hash
- `model_version` — LLM model identifier
- `prompt_version` — Hash of prompt templates
- `dataset_version` — Dataset identifier

## Future Work

1. Create labeled datasets for each agent
2. Implement evaluator scoring logic
3. Define thresholds for pass/fail
4. Set up CI/CD evaluation pipeline
5. Build evaluation dashboard
