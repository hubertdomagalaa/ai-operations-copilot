"""
Quality Management Infrastructure
=================================

Quality signals, thresholds, calibration, and regression detection.

!!! WARNING: INFRASTRUCTURE ONLY !!!
This package contains SKELETON CODE for quality management.
NO quality decisions are made.
NO thresholds are enforced.
NO automated gating is performed.

WHY THIS EXISTS:
- Defines quality signal contracts
- Establishes threshold schema
- Documents calibration pipeline
- Prepares for regression detection

PACKAGE STRUCTURE:
    /quality
    ├── __init__.py        # This file - exports and overview
    ├── signals.py         # Quality signal definitions
    ├── thresholds.py      # Threshold management
    ├── calibration.py     # Confidence calibration pipeline
    └── regression.py      # Regression detection

WHAT EACH MODULE PROVIDES:

signals:
    - SignalType, SignalSource: Signal categorization
    - SignalDefinition: Schema for signal metadata
    - SIGNAL_DEFINITIONS: Registry of all signals
    - extract_signals_from_state(): Signal extraction

thresholds:
    - ThresholdConfig: Threshold configuration schema
    - THRESHOLD_CONFIGS: Registry (all inactive)
    - check_threshold(): Threshold evaluation (not implemented)

calibration:
    - CalibrationDataPoint: (confidence, outcome) pairs
    - CalibrationCurve: Calibration curve structure
    - CalibrationPipeline: Pipeline for fitting curves

regression:
    - VersionedResult: Evaluation result with version info
    - RegressionReport: Comparison report
    - RegressionDetector: Regression detection logic

WHAT IS INTENTIONALLY MISSING:
- Actual threshold values
- Calibration curves
- Comparison results
- Pass/fail decisions
- Automated gating

TO ACTIVATE QUALITY MANAGEMENT:
1. Collect sufficient labeled data (N > 500)
2. Run offline evaluation
3. Compute calibration curves
4. Set thresholds with human review
5. Store baselines for regression detection
6. Enable with explicit configuration

HUMAN JUDGMENT IN QUALITY:
- Thresholds need human validation
- Calibration curves need human review
- Regressions need human investigation
- No automated rollbacks
"""

# === Exports ===

from evaluation.quality.signals import (
    SignalType,
    SignalSource,
    SignalDefinition,
    CollectedSignal,
    SIGNAL_DEFINITIONS,
    extract_signals_from_state,
    get_signal_definition,
    list_signals_by_source,
)

from evaluation.quality.thresholds import (
    ThresholdType,
    ThresholdAction,
    ThresholdConfig,
    ThresholdCheckResult,
    THRESHOLD_CONFIGS,
    check_threshold,
    get_active_thresholds,
    get_threshold_config,
)

from evaluation.quality.calibration import (
    CalibrationDataPoint,
    CalibrationBucket,
    CalibrationCurve,
    CalibrationPipeline,
    get_calibration_pipeline,
)

from evaluation.quality.regression import (
    VersionedResult,
    MetricComparison,
    RegressionReport,
    RegressionDetector,
    create_regression_detector,
    get_comparison_status,
)

__all__ = [
    # Signals
    "SignalType",
    "SignalSource", 
    "SignalDefinition",
    "CollectedSignal",
    "SIGNAL_DEFINITIONS",
    "extract_signals_from_state",
    "get_signal_definition",
    "list_signals_by_source",
    # Thresholds
    "ThresholdType",
    "ThresholdAction",
    "ThresholdConfig",
    "ThresholdCheckResult",
    "THRESHOLD_CONFIGS",
    "check_threshold",
    "get_active_thresholds",
    "get_threshold_config",
    # Calibration
    "CalibrationDataPoint",
    "CalibrationBucket",
    "CalibrationCurve",
    "CalibrationPipeline",
    "get_calibration_pipeline",
    # Regression
    "VersionedResult",
    "MetricComparison",
    "RegressionReport",
    "RegressionDetector",
    "create_regression_detector",
    "get_comparison_status",
]

# Package metadata
__version__ = "0.1.0"
__status__ = "infrastructure_only"
