"""
Evaluation Infrastructure
=========================

Offline evaluation system for AI Operations Copilot.

!!! WARNING: INFRASTRUCTURE ONLY !!!
This package contains SKELETON CODE for offline evaluation.
NO real evaluations are performed.
NO real metrics are computed.

WHY THIS EXISTS:
- Defines contracts for future evaluation
- Establishes folder structure
- Documents evaluation boundaries
- Enables version tracking for reproducibility

PACKAGE STRUCTURE:
    /evaluation
    ├── __init__.py        # This file - exports and overview
    ├── evaluators.py      # Legacy evaluator stubs (existing)
    ├── versioning.py      # Version tracking for reproducibility
    ├── datasets/          # Dataset schema contracts
    │   └── __init__.py
    ├── runners/           # Evaluation orchestration
    │   └── __init__.py
    └── reports/           # Report generation
        └── __init__.py

WHAT EACH MODULE PROVIDES:

datasets:
    - TicketDatasetItem: Schema for labeled tickets
    - DocumentDatasetItem: Schema for RAG documents
    - EndToEndTestCase: Schema for workflow test cases
    - EvaluationDataset: Container for datasets

runners:
    - Evaluator: Base class for all evaluators
    - EvaluatorResult: Result from single evaluation
    - EvaluationRunner: Orchestrates multiple evaluators
    - Placeholder evaluators: TriageAccuracyEvaluator, etc.

reports:
    - EvaluationReport: Complete report structure
    - ReportMetadata: Version and provenance info
    - ReportGenerator: JSON and Markdown output

versioning:
    - VersionInfo: Captures code/model/prompt versions
    - capture_version_info(): Get current versions

WHAT IS INTENTIONALLY MISSING:
- Real datasets
- Real evaluation logic
- Computed metrics
- Thresholds
- Pass/fail decisions

TO ACTIVATE REAL EVALUATION:
1. Create labeled datasets in /evaluation/datasets/
2. Implement evaluator logic in runners/
3. Define thresholds and pass criteria
4. Run evaluations and generate reports

USAGE (when ready):
    from evaluation.runners import EvaluationRunner, create_default_runner
    from evaluation.datasets import load_dataset
    from evaluation.reports import ReportGenerator
    from evaluation.versioning import capture_version_info
    
    # Load dataset
    dataset = load_dataset("path/to/dataset.json")
    
    # Capture versions
    versions = capture_version_info()
    
    # Run evaluation
    runner = create_default_runner()
    results = runner.run(workflow_states, expected_outcomes)
    
    # Generate report
    generator = ReportGenerator()
    report_md = generator.generate_markdown(report)
"""

# === Exports ===

from evaluation.evaluators import (
    EvaluationResult,
    BaseEvaluator,
    ClassificationEvaluator,
    ResponseQualityEvaluator,
    RetrievalEvaluator,
)

from evaluation.versioning import (
    VersionInfo,
    capture_version_info,
    get_code_version,
    format_version_string,
)

# Note: Submodule imports should be done explicitly:
# from evaluation.datasets import TicketDatasetItem
# from evaluation.runners import EvaluationRunner
# from evaluation.reports import ReportGenerator

__all__ = [
    # Legacy evaluators
    "EvaluationResult",
    "BaseEvaluator",
    "ClassificationEvaluator",
    "ResponseQualityEvaluator",
    "RetrievalEvaluator",
    # Versioning
    "VersionInfo",
    "capture_version_info",
    "get_code_version",
    "format_version_string",
]

# Package metadata
__version__ = "0.1.0"
__status__ = "infrastructure_only"
