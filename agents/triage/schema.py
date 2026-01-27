"""
Triage Agent Schema
===================

Pydantic models for TriageAgent structured output.

These schemas define the contract between the TriageAgent and downstream components.
The LLM must produce output matching these schemas exactly.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ConfidenceFactors(BaseModel):
    """Breakdown of factors affecting classification confidence."""
    
    category_clarity: Literal["clear", "moderate", "ambiguous"] = Field(
        description="How clearly the ticket matches one category"
    )
    symptom_specificity: Literal["specific", "general", "vague"] = Field(
        description="How specific the reported symptoms are"
    )
    technical_detail_level: Literal["high", "medium", "low"] = Field(
        description="Level of technical detail provided in ticket"
    )


class TechnicalSignals(BaseModel):
    """Technical details extracted from the ticket."""
    
    affected_components: List[str] = Field(
        default_factory=list,
        description="Components mentioned in ticket"
    )
    framework_version: Optional[str] = Field(
        default=None,
        description="Framework version if stated, null otherwise"
    )
    python_version: Optional[str] = Field(
        default=None,
        description="Python version if stated, null otherwise"
    )
    environment: Literal["production", "staging", "development", "testing", "unknown"] = Field(
        default="unknown",
        description="Environment where issue occurs"
    )
    has_reproduction_steps: bool = Field(
        default=False,
        description="Whether ticket includes reproduction steps"
    )
    has_error_output: bool = Field(
        default=False,
        description="Whether ticket includes error messages or traces"
    )


class TriageReasoning(BaseModel):
    """Structured reasoning explaining classification decisions."""
    
    category_rationale: str = Field(
        min_length=20,
        max_length=300,
        description="Why this category was selected, citing specific ticket content"
    )
    facts_from_ticket: List[str] = Field(
        min_length=1,
        max_length=10,
        description="Explicit facts stated in the ticket (not inferences)"
    )
    inferences_made: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Inferences or assumptions made beyond stated facts. Empty if none."
    )
    uncertainty_notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Notes about areas of uncertainty in classification. Null if confident."
    )


# Category enum values
CATEGORY_VALUES = Literal[
    "validation",
    "middleware",
    "async_concurrency",
    "response_handling",
    "performance",
    "serialization",
    "openapi",
    "file_handling",
    "authentication",
    "installation",
    "dependency_lifecycle",
    "other"
]

# Issue type enum values
ISSUE_TYPE_VALUES = Literal["bug", "question", "incident", "documentation", "feature_request"]

# Severity enum values
SEVERITY_VALUES = Literal["P1", "P2", "P3", "P4"]


class TriageOutput(BaseModel):
    """
    Structured output from the TriageAgent.
    
    This is the complete schema that the LLM must produce.
    All downstream agents depend on this contract.
    """
    
    ticket_id: str = Field(
        description="Ticket identifier echoed from input"
    )
    
    primary_category: CATEGORY_VALUES = Field(
        description="Single most appropriate category for this ticket"
    )
    
    secondary_category: Optional[CATEGORY_VALUES] = Field(
        default=None,
        description="Second category only if ticket clearly spans two areas with equal weight. Null in most cases."
    )
    
    issue_type: ISSUE_TYPE_VALUES = Field(
        description="Type of issue being reported"
    )
    
    severity: SEVERITY_VALUES = Field(
        description="Severity level based on stated impact"
    )
    
    severity_justification: str = Field(
        min_length=10,
        max_length=200,
        description="Brief justification for severity, citing ticket content"
    )
    
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Classification confidence score. Below 0.70 triggers escalation."
    )
    
    confidence_factors: ConfidenceFactors = Field(
        description="Breakdown of factors affecting confidence"
    )
    
    requires_escalation: bool = Field(
        description="True if any escalation trigger applies or confidence < 0.70"
    )
    
    escalation_reasons: List[str] = Field(
        default_factory=list,
        description="List of applicable escalation triggers. Empty if requires_escalation=false."
    )
    
    technical_signals: TechnicalSignals = Field(
        description="Technical details extracted from the ticket"
    )
    
    keywords: List[str] = Field(
        min_length=3,
        max_length=8,
        description="Key terms for knowledge retrieval (3-8 items)"
    )
    
    one_line_summary: str = Field(
        min_length=20,
        max_length=150,
        description="Single sentence summary for quick scan"
    )
    
    reasoning: TriageReasoning = Field(
        description="Structured reasoning explaining classification decisions"
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for state storage."""
        return self.model_dump()


# Confidence threshold for escalation
CONFIDENCE_THRESHOLD = 0.7

# Escalation keywords to check
ESCALATION_KEYWORDS = [
    "security", "vulnerability", "breach", "cve", "exploit", "attack",
    "data loss", "data corruption", "data deleted", "data missing",
    "outage", "down", "unavailable", "100% failure",
    "all users", "multiple customers", "widespread",
    "500 error", "production error",
    "urgent", "immediate", "asap", "critical"
]
