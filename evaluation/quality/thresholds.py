"""
Threshold Management
====================

Infrastructure for managing quality thresholds.

!!! WARNING !!!
This is INFRASTRUCTURE ONLY.
NO thresholds are set.
NO pass/fail decisions are made.
NO automated gating is performed.

WHY THIS FILE EXISTS:
- Defines schema for threshold configuration
- Establishes where thresholds would be stored
- Documents how thresholds will be used
- Enables per-agent and per-use-case configuration

WHY THRESHOLDS ARE DANGEROUS:
- Premature thresholds encode assumptions before data exists
- Fixed thresholds don't adapt to distribution shifts
- Thresholds without calibration create false confidence
- Automated gating without human oversight is risky

WHEN TO SET THRESHOLDS:
1. After sufficient data is collected (N > 1000 examples)
2. After calibration curves are computed
3. After human review of proposed thresholds
4. With explicit override mechanisms

WHAT IS INTENTIONALLY MISSING:
- Actual threshold values
- Pass/fail logic
- Automated enforcement
- Quality gates
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ThresholdType(str, Enum):
    """Types of thresholds."""
    
    MINIMUM = "minimum"
    """Value must be >= threshold"""
    
    MAXIMUM = "maximum"
    """Value must be <= threshold"""
    
    RANGE = "range"
    """Value must be within range"""


class ThresholdAction(str, Enum):
    """What happens when threshold is not met."""
    
    WARN = "warn"
    """Log warning, continue processing"""
    
    FLAG_FOR_REVIEW = "flag_for_review"
    """Add to human review queue"""
    
    BLOCK = "block"
    """Prevent progression (DANGEROUS - use sparingly)"""


@dataclass
class ThresholdConfig:
    """
    Configuration for a single threshold.
    
    This defines WHAT threshold would be applied, not the value.
    Actual values are intentionally NOT set.
    """
    
    # Identity
    threshold_id: str
    signal_name: str
    """Must match a signal in signals.py"""
    
    # Configuration
    threshold_type: ThresholdType
    action: ThresholdAction = ThresholdAction.FLAG_FOR_REVIEW
    
    # Threshold values - INTENTIONALLY None
    value: Optional[float] = None
    """The threshold value. NOT SET until calibration."""
    
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    
    # Scope
    agent_type: Optional[str] = None
    """Apply only to this agent (None = all)"""
    
    use_case: Optional[str] = None
    """Apply only to this use case (None = all)"""
    
    # Metadata
    description: str = ""
    rationale: str = ""
    """Why this threshold exists (document before setting)"""
    
    # Calibration info - NOT YET PERFORMED
    calibrated_at: Optional[str] = None
    calibrated_from_n_samples: Optional[int] = None
    calibration_notes: Optional[str] = None
    
    # Status
    is_active: bool = False
    """INTENTIONALLY False - no thresholds are active"""


# === Threshold Registry ===

# IMPORTANT: All thresholds have is_active=False and value=None
# This is intentional - no automated gating without calibration

THRESHOLD_CONFIGS: Dict[str, ThresholdConfig] = {
    
    # === Triage Thresholds (INACTIVE) ===
    
    "triage_confidence_minimum": ThresholdConfig(
        threshold_id="triage_confidence_minimum",
        signal_name="triage_confidence",
        threshold_type=ThresholdType.MINIMUM,
        action=ThresholdAction.FLAG_FOR_REVIEW,
        value=None,  # NOT SET
        agent_type="triage",
        description="Minimum acceptable triage confidence",
        rationale="Low confidence classifications need human review",
        is_active=False,  # NOT ACTIVE
    ),
    
    # === Retrieval Thresholds (INACTIVE) ===
    
    "retrieval_minimum_score": ThresholdConfig(
        threshold_id="retrieval_minimum_score",
        signal_name="retrieval_top_score",
        threshold_type=ThresholdType.MINIMUM,
        action=ThresholdAction.FLAG_FOR_REVIEW,
        value=None,  # NOT SET
        agent_type="knowledge",
        description="Minimum top document relevance score",
        rationale="Low retrieval scores indicate poor grounding",
        is_active=False,  # NOT ACTIVE
    ),
    
    # === Decision Thresholds (INACTIVE) ===
    
    "decision_confidence_minimum": ThresholdConfig(
        threshold_id="decision_confidence_minimum",
        signal_name="decision_confidence",
        threshold_type=ThresholdType.MINIMUM,
        action=ThresholdAction.FLAG_FOR_REVIEW,
        value=None,  # NOT SET
        agent_type="decision",
        description="Minimum decision confidence for auto-proceed",
        rationale="Low confidence decisions always need human review",
        is_active=False,  # NOT ACTIVE
    ),
    
    "decision_max_risk_flags": ThresholdConfig(
        threshold_id="decision_max_risk_flags",
        signal_name="decision_risk_flag_count",
        threshold_type=ThresholdType.MAXIMUM,
        action=ThresholdAction.FLAG_FOR_REVIEW,
        value=None,  # NOT SET
        agent_type="decision",
        description="Maximum risk flags before mandatory review",
        rationale="Multiple risk flags indicate uncertain situation",
        is_active=False,  # NOT ACTIVE
    ),
}


# === Threshold Evaluation ===

@dataclass
class ThresholdCheckResult:
    """
    Result of checking a value against a threshold.
    
    Note: Actual check logic is NOT implemented.
    This is the output structure only.
    """
    
    threshold_id: str
    signal_name: str
    signal_value: float
    threshold_value: Optional[float]
    
    passed: Optional[bool] = None
    """None if threshold is inactive"""
    
    action_required: Optional[ThresholdAction] = None
    message: str = ""


def check_threshold(
    signal_name: str,
    signal_value: float,
    agent_type: str = None,
    use_case: str = None,
) -> List[ThresholdCheckResult]:
    """
    Check a signal value against applicable thresholds.
    
    TODO: Implement when thresholds are calibrated and activated.
    
    Currently returns empty results because no thresholds are active.
    """
    results = []
    
    # Find applicable thresholds
    for config in THRESHOLD_CONFIGS.values():
        if config.signal_name != signal_name:
            continue
        
        if config.agent_type and config.agent_type != agent_type:
            continue
            
        if config.use_case and config.use_case != use_case:
            continue
        
        # Check if active
        if not config.is_active:
            results.append(ThresholdCheckResult(
                threshold_id=config.threshold_id,
                signal_name=signal_name,
                signal_value=signal_value,
                threshold_value=config.value,
                passed=None,  # Cannot evaluate inactive threshold
                action_required=None,
                message="Threshold not active - calibration required",
            ))
            continue
        
        # TODO: Implement threshold checking logic when activated
        # This is intentionally NOT implemented
    
    return results


def get_active_thresholds() -> List[ThresholdConfig]:
    """Get all active thresholds. Currently returns empty list."""
    return [t for t in THRESHOLD_CONFIGS.values() if t.is_active]


def get_threshold_config(threshold_id: str) -> Optional[ThresholdConfig]:
    """Get a threshold configuration by ID."""
    return THRESHOLD_CONFIGS.get(threshold_id)
