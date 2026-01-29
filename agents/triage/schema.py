"""
TriageAgent Schema — FINAL v1.0
================================

Date: January 28, 2026
Status: Production Ready

Pydantic models for TriageAgent structured output.
This schema is the contract between the LLM and downstream systems.

SCHEMA VERSION: 1.0 (FINAL)
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


# === Category Taxonomy ===

class TicketCategory(str, Enum):
    """
    Exactly one primary category must be assigned.
    Choose the single most appropriate category.
    """
    VALIDATION = "validation"
    MIDDLEWARE = "middleware"
    ASYNC_CONCURRENCY = "async_concurrency"
    RESPONSE_HANDLING = "response_handling"
    PERFORMANCE = "performance"
    SERIALIZATION = "serialization"
    OPENAPI = "openapi"
    FILE_HANDLING = "file_handling"
    AUTHENTICATION = "authentication"
    INSTALLATION = "installation"
    DEPENDENCY_LIFECYCLE = "dependency_lifecycle"
    OTHER = "other"


class IssueType(str, Enum):
    """Type of issue being reported."""
    BUG = "bug"
    QUESTION = "question"
    INCIDENT = "incident"
    DOCUMENTATION = "documentation"
    FEATURE_REQUEST = "feature_request"


class Severity(str, Enum):
    """
    Severity based on STATED impact only.
    Never infer severity beyond what the ticket explicitly describes.
    """
    P1 = "P1"  # Active outage, data loss, security issue, complete feature unavailability
    P2 = "P2"  # Severe breakage, no workaround, significant user impact
    P3 = "P3"  # Partial degradation, confusing behavior, workaround exists
    P4 = "P4"  # Question, documentation gap, enhancement suggestion


class CategoryClarity(str, Enum):
    """How clearly ticket matches one category."""
    CLEAR = "clear"
    MODERATE = "moderate"
    AMBIGUOUS = "ambiguous"


class SymptomSpecificity(str, Enum):
    """How specific the symptoms are."""
    SPECIFIC = "specific"
    GENERAL = "general"
    VAGUE = "vague"


class TechnicalDetailLevel(str, Enum):
    """Level of technical detail provided."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Environment(str, Enum):
    """Environment where issue occurs."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    UNKNOWN = "unknown"


# === Schema Components ===

class ConfidenceFactors(BaseModel):
    """
    Breakdown of factors contributing to confidence score.
    All three factors are required.
    """
    category_clarity: CategoryClarity = Field(
        ...,
        description="How clearly ticket matches one category"
    )
    symptom_specificity: SymptomSpecificity = Field(
        ...,
        description="How specific the symptoms are"
    )
    technical_detail_level: TechnicalDetailLevel = Field(
        ...,
        description="Level of technical detail provided"
    )


class TechnicalSignals(BaseModel):
    """
    Technical context extracted from ticket.
    All fields required; use null/empty/unknown for missing data.
    """
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
    environment: Environment = Field(
        default=Environment.UNKNOWN,
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
    """
    Grounded reasoning for classification.
    Every classification must cite specific ticket content.
    """
    category_rationale: str = Field(
        ...,
        min_length=20,
        max_length=300,
        description="Why this category, citing ticket content"
    )
    facts_from_ticket: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Explicit facts from ticket (not inferences)"
    )
    inferences_made: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Inferences beyond stated facts. Empty if none."
    )
    uncertainty_notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Notes on uncertainty. Null if confident."
    )


# === Main Output Schema ===

class TriageOutput(BaseModel):
    """
    Complete triage classification output.
    
    All 13 fields are required.
    This is the contract between LLM and downstream systems.
    
    SCHEMA VERSION: 1.0 (FINAL)
    """
    
    # Identification
    ticket_id: str = Field(
        ...,
        description="Ticket identifier echoed from input"
    )
    
    # Classification
    primary_category: TicketCategory = Field(
        ...,
        description="Single most appropriate category"
    )
    secondary_category: Optional[TicketCategory] = Field(
        default=None,
        description="Second category only if ticket clearly spans two areas with equal weight. Null in most cases (90%+)."
    )
    issue_type: IssueType = Field(
        ...,
        description="Type of issue being reported"
    )
    
    # Severity
    severity: Severity = Field(
        ...,
        description="Severity based on stated impact"
    )
    severity_justification: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Brief justification citing ticket content"
    )
    
    # Confidence
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence. Below 0.70 triggers escalation."
    )
    confidence_factors: ConfidenceFactors = Field(
        ...,
        description="Breakdown of factors affecting confidence"
    )
    
    # Escalation
    requires_escalation: bool = Field(
        ...,
        description="True if any escalation trigger applies or confidence < 0.70"
    )
    escalation_reasons: List[str] = Field(
        default_factory=list,
        description="List of applicable escalation triggers. Empty array if requires_escalation=false."
    )
    
    # Technical Context
    technical_signals: TechnicalSignals = Field(
        ...,
        description="Extracted technical context"
    )
    
    # Keywords for RAG
    keywords: List[str] = Field(
        ...,
        min_length=3,
        max_length=8,
        description="Terms for knowledge retrieval (3-8 keywords)"
    )
    
    # Summary
    one_line_summary: str = Field(
        ...,
        min_length=20,
        max_length=150,
        description="Single sentence summary for quick scan"
    )
    
    # Reasoning
    reasoning: TriageReasoning = Field(
        ...,
        description="Grounded reasoning with facts from ticket"
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for state storage."""
        return self.model_dump()
    
    class Config:
        use_enum_values = True


# === Constants ===

CONFIDENCE_THRESHOLD = 0.70
"""Confidence below this triggers automatic escalation."""

ESCALATION_KEYWORDS = [
    "security", "vulnerability", "breach", "cve", "exploit", "attack",
    "data loss", "data corruption", "data deleted", "data missing",
    "outage", "service down", "unavailable", "100% failure",
    "500 error", "production error",
    "all users", "multiple customers", "widespread",
    "urgent", "immediate", "critical", "emergency"
]
"""Keywords that trigger escalation when detected in ticket content."""

PROMPT_VERSION = "1.0"
"""Current prompt version for evaluation tracking."""
