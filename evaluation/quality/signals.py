"""
Quality Signals
===============

Definitions of quality signals produced by the AI Operations Copilot.

!!! WARNING !!!
This is INFRASTRUCTURE ONLY.
Signal definitions exist, but NO interpretation is performed.
NO thresholds are set. NO quality decisions are made.

WHY THIS FILE EXISTS:
- Defines what quality signals the system produces
- Documents where each signal comes from
- Establishes contracts for downstream calibration
- Enables consistent signal collection

WHAT SIGNALS ARE CAPTURED:
1. Confidence Scores — Per-agent output confidence
2. Retrieval Metrics — RAG retrieval quality signals
3. Human Override Rates — How often humans reject AI decisions
4. Evaluation Results — Offline evaluation outputs

WHAT IS INTENTIONALLY MISSING:
- Interpretation of signals
- Thresholds
- Pass/fail decisions
- Calibration curves

WHEN TO INTERPRET SIGNALS:
- After sufficient data is collected
- After calibration is performed
- After thresholds are validated with human judgment
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# === Signal Types ===

class SignalType(str, Enum):
    """Types of quality signals in the system."""
    
    CONFIDENCE = "confidence"
    """Model confidence score (0.0 - 1.0)"""
    
    RETRIEVAL_SCORE = "retrieval_score"
    """RAG retrieval relevance score"""
    
    HUMAN_OVERRIDE = "human_override"
    """Binary: did human override AI decision?"""
    
    HUMAN_EDIT_DISTANCE = "human_edit_distance"
    """How much did human edit the draft?"""
    
    EVALUATION_SCORE = "evaluation_score"
    """Offline evaluation metric"""
    
    LATENCY = "latency"
    """Processing time in milliseconds"""
    
    ERROR_RATE = "error_rate"
    """Rate of failures/exceptions"""


class SignalSource(str, Enum):
    """Where signals originate from."""
    
    TRIAGE_AGENT = "triage_agent"
    KNOWLEDGE_AGENT = "knowledge_agent"
    DECISION_AGENT = "decision_agent"
    ACTION_AGENT = "action_agent"
    HUMAN_FEEDBACK = "human_feedback"
    OFFLINE_EVALUATION = "offline_evaluation"
    SYSTEM_METRICS = "system_metrics"


# === Signal Definitions ===

@dataclass
class SignalDefinition:
    """
    Definition of a single quality signal.
    
    This describes WHAT the signal is, not HOW to interpret it.
    """
    
    name: str
    """Unique identifier for this signal"""
    
    signal_type: SignalType
    """Type of signal"""
    
    source: SignalSource
    """Where this signal comes from"""
    
    description: str
    """Human-readable description"""
    
    value_range: tuple = (0.0, 1.0)
    """Expected value range (min, max)"""
    
    higher_is_better: bool = True
    """True if higher values indicate better quality"""
    
    # NOT SET - will be defined during calibration
    threshold: Optional[float] = None
    """INTENTIONALLY None - no thresholds yet"""
    
    # Metadata
    first_defined: str = ""
    """When this signal was added to the system"""


# === Signal Registry ===

SIGNAL_DEFINITIONS: Dict[str, SignalDefinition] = {
    
    # === Triage Agent Signals ===
    
    "triage_confidence": SignalDefinition(
        name="triage_confidence",
        signal_type=SignalType.CONFIDENCE,
        source=SignalSource.TRIAGE_AGENT,
        description="Confidence in ticket classification (type, severity)",
        value_range=(0.0, 1.0),
        higher_is_better=True,
    ),
    
    # === Knowledge Agent Signals ===
    
    "retrieval_confidence": SignalDefinition(
        name="retrieval_confidence",
        signal_type=SignalType.RETRIEVAL_SCORE,
        source=SignalSource.KNOWLEDGE_AGENT,
        description="Confidence in retrieved documents relevance",
        value_range=(0.0, 1.0),
        higher_is_better=True,
    ),
    
    "retrieval_top_score": SignalDefinition(
        name="retrieval_top_score",
        signal_type=SignalType.RETRIEVAL_SCORE,
        source=SignalSource.KNOWLEDGE_AGENT,
        description="Similarity score of top retrieved document",
        value_range=(0.0, 1.0),
        higher_is_better=True,
    ),
    
    "retrieval_document_count": SignalDefinition(
        name="retrieval_document_count",
        signal_type=SignalType.RETRIEVAL_SCORE,
        source=SignalSource.KNOWLEDGE_AGENT,
        description="Number of documents retrieved above minimum score",
        value_range=(0, 100),
        higher_is_better=True,  # Within reason
    ),
    
    # === Decision Agent Signals ===
    
    "decision_confidence": SignalDefinition(
        name="decision_confidence",
        signal_type=SignalType.CONFIDENCE,
        source=SignalSource.DECISION_AGENT,
        description="Confidence in recommended action",
        value_range=(0.0, 1.0),
        higher_is_better=True,
    ),
    
    "decision_risk_flag_count": SignalDefinition(
        name="decision_risk_flag_count",
        signal_type=SignalType.CONFIDENCE,
        source=SignalSource.DECISION_AGENT,
        description="Number of risk flags identified",
        value_range=(0, 10),
        higher_is_better=False,  # Fewer flags = less risk
    ),
    
    # === Action Agent Signals ===
    
    "action_confidence": SignalDefinition(
        name="action_confidence",
        signal_type=SignalType.CONFIDENCE,
        source=SignalSource.ACTION_AGENT,
        description="Confidence in draft quality",
        value_range=(0.0, 1.0),
        higher_is_better=True,
    ),
    
    # === Human Feedback Signals ===
    
    "human_override_occurred": SignalDefinition(
        name="human_override_occurred",
        signal_type=SignalType.HUMAN_OVERRIDE,
        source=SignalSource.HUMAN_FEEDBACK,
        description="Binary flag: did human override AI recommendation?",
        value_range=(0, 1),
        higher_is_better=False,  # Fewer overrides = better AI
    ),
    
    "human_approval_time_seconds": SignalDefinition(
        name="human_approval_time_seconds",
        signal_type=SignalType.LATENCY,
        source=SignalSource.HUMAN_FEEDBACK,
        description="Time from human review start to decision",
        value_range=(0, 3600),
        higher_is_better=False,  # Faster = better
    ),
    
    # === System Signals ===
    
    "workflow_latency_ms": SignalDefinition(
        name="workflow_latency_ms",
        signal_type=SignalType.LATENCY,
        source=SignalSource.SYSTEM_METRICS,
        description="Total workflow processing time",
        value_range=(0, 60000),
        higher_is_better=False,
    ),
    
    "agent_error_occurred": SignalDefinition(
        name="agent_error_occurred",
        signal_type=SignalType.ERROR_RATE,
        source=SignalSource.SYSTEM_METRICS,
        description="Binary: did any agent fail during workflow?",
        value_range=(0, 1),
        higher_is_better=False,
    ),
}


# === Signal Collection ===

@dataclass
class CollectedSignal:
    """
    A signal value collected from a workflow execution.
    
    This is what gets stored for later analysis.
    """
    
    signal_name: str
    value: float
    
    # Context
    ticket_id: str
    trace_id: str
    workflow_run_id: str
    
    # Timestamp
    collected_at: str
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


def extract_signals_from_state(
    workflow_state: Dict[str, Any],
) -> List[CollectedSignal]:
    """
    Extract quality signals from a completed workflow state.
    
    This function reads agent outputs and produces signal values.
    NO interpretation is performed - just extraction.
    
    TODO: Implement extraction when workflow produces signals
    """
    signals = []
    
    ticket_id = workflow_state.get("ticket_id", "unknown")
    trace_id = workflow_state.get("trace_id", "unknown")
    now = datetime.utcnow().isoformat()
    
    # TODO: Extract triage confidence
    # triage_output = workflow_state.get("triage_output", {})
    # if triage_output:
    #     signals.append(CollectedSignal(
    #         signal_name="triage_confidence",
    #         value=triage_output.get("confidence", 0.0),
    #         ticket_id=ticket_id,
    #         trace_id=trace_id,
    #         workflow_run_id=...,
    #         collected_at=now,
    #     ))
    
    # TODO: Extract knowledge signals
    # TODO: Extract decision signals
    # TODO: Extract action signals
    
    return signals


def get_signal_definition(signal_name: str) -> Optional[SignalDefinition]:
    """Get the definition of a signal by name."""
    return SIGNAL_DEFINITIONS.get(signal_name)


def list_signals_by_source(source: SignalSource) -> List[SignalDefinition]:
    """Get all signals from a specific source."""
    return [s for s in SIGNAL_DEFINITIONS.values() if s.source == source]
