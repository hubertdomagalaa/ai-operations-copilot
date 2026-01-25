# Quality Management System

> ⚠️ **INFRASTRUCTURE ONLY** — This is skeleton code. No quality decisions are made.

## Purpose

This directory contains the **quality management infrastructure** for the AI Operations Copilot. It defines:

- **Quality Signals** — What signals the system produces
- **Threshold Management** — How thresholds would be configured
- **Calibration Pipeline** — How confidence is calibrated
- **Regression Detection** — How quality changes are detected

## Why Quality Management Matters

AI systems are only useful if we can trust their outputs. Quality management enables:

1. **Confidence Calibration** — Make "80% confident" actually mean 80% accuracy
2. **Threshold Setting** — Know when to require human review
3. **Regression Detection** — Catch quality degradations before production
4. **Continuous Improvement** — Track quality over time

## What's Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| `signals.py` | Definitions only | 12 quality signal types |
| `thresholds.py` | Schema only | Threshold configs (all inactive) |
| `calibration.py` | Interface only | Pipeline skeleton |
| `regression.py` | Interface only | Comparison structures |

## What's Intentionally Missing

- ❌ Actual threshold values
- ❌ Calibration curves
- ❌ Comparison results
- ❌ Pass/fail decisions
- ❌ Automated gating

## Why Thresholds Are Dangerous

Setting thresholds without sufficient data is harmful:

| Risk | Consequence |
|------|-------------|
| Too high threshold | Excessive human review, system unusable |
| Too low threshold | Bad outputs slip through, trust eroded |
| Fixed threshold | Doesn't adapt to distribution shifts |
| No calibration | Confidence scores are meaningless |

**Solution:** Collect data first, calibrate, then set thresholds with human review.

## Quality Signals

| Signal | Type | Source | Higher = Better |
|--------|------|--------|-----------------|
| `triage_confidence` | Confidence | Triage Agent | ✓ |
| `retrieval_confidence` | Retrieval | Knowledge Agent | ✓ |
| `retrieval_top_score` | Retrieval | Knowledge Agent | ✓ |
| `decision_confidence` | Confidence | Decision Agent | ✓ |
| `decision_risk_flag_count` | Risk | Decision Agent | ✗ |
| `human_override_occurred` | Override | Human Feedback | ✗ |
| `workflow_latency_ms` | Latency | System | ✗ |

## Calibration Pipeline

When implemented, the calibration pipeline will:

1. **Collect** (confidence, actual_outcome) pairs
2. **Bucket** confidences into ranges (0-0.1, 0.1-0.2, ...)
3. **Calculate** accuracy per bucket
4. **Fit** calibration curve (isotonic regression)
5. **Apply** curve to adjust future scores

**Requirements to activate:**
- N > 500 labeled examples
- Human review of calibration curves
- Explicit configuration to enable

## Regression Detection

When implemented, regression detection will:

1. Run evaluation on current version
2. Compare against stored baseline
3. Flag significant degradations
4. Present to human for review

**No automated rollbacks** — humans always decide.

## Human Judgment

Quality decisions MUST involve humans:

- Thresholds are reviewed before activation
- Calibration curves are validated
- Regressions are investigated, not auto-rolled-back
- Override mechanisms exist for all automated checks

## Required to Activate

1. Collect sufficient labeled data
2. Run offline evaluation
3. Compute and review calibration curves
4. Set thresholds with human approval
5. Store baselines for regression detection
6. Enable with explicit configuration flag
