"""
Evaluation Datasets
===================

Dataset contracts and schema definitions for offline evaluation.

!!! WARNING !!!
This is INFRASTRUCTURE ONLY.
No real datasets are stored here.
This file defines CONTRACTS that future datasets must follow.

WHY THIS FILE EXISTS:
- Defines expected schema for evaluation datasets
- Documents required fields for each dataset type
- Provides example structures (not real data)
- Enables dataset validation before evaluation runs

DATASET TYPES:
1. TicketDataset — Labeled tickets with expected classifications
2. DocumentDataset — Documents for RAG testing
3. EndToEndDataset — Full workflow test cases with expected outcomes

WHAT IS INTENTIONALLY MISSING:
- Real ticket data
- Real document content
- Actual expected outcomes
- Ground truth labels

WHEN TO ADD REAL DATA:
- After system is validated end-to-end
- After evaluation metrics are defined
- After labeling guidelines are established
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime


# === Dataset Item Contracts ===

@dataclass
class TicketDatasetItem:
    """
    Schema for a single ticket in an evaluation dataset.
    
    This is a CONTRACT, not data. Real tickets will conform to this schema.
    
    REQUIRED FIELDS:
    - ticket_id: Unique identifier
    - ticket_data: The ticket content (subject, body, metadata)
    - expected_triage: Expected classification output
    
    OPTIONAL FIELDS:
    - expected_action: Expected recommended action
    - notes: Labeler notes explaining the expected outcome
    """
    
    # Unique identifier
    ticket_id: str
    
    # Ticket content (matches workflow state schema)
    ticket_data: Dict[str, Any]
    """
    Expected structure:
    {
        "subject": str,
        "body": str,
        "customer_id": str,
        "created_at": str,
        "metadata": Dict[str, Any]
    }
    """
    
    # Expected triage classification
    expected_triage: Dict[str, Any]
    """
    Expected structure:
    {
        "ticket_type": "bug" | "incident" | "question" | "task",
        "severity": "low" | "medium" | "high" | "critical",
        "keywords": List[str],
        "requires_escalation": bool
    }
    """
    
    # Expected recommended action (optional)
    expected_action: Optional[str] = None
    """One of: "auto_respond", "escalate", "manual_review" """
    
    # Labeler notes
    notes: Optional[str] = None
    
    # Metadata
    labeled_by: Optional[str] = None
    labeled_at: Optional[str] = None


@dataclass
class DocumentDatasetItem:
    """
    Schema for a document in a RAG evaluation dataset.
    
    Used to test retrieval quality.
    
    REQUIRED FIELDS:
    - doc_id: Unique identifier
    - content: Document text
    - relevant_for: List of ticket types this doc is relevant for
    """
    
    doc_id: str
    content: str
    filename: str
    doc_type: str  # "api_docs", "runbooks", etc.
    
    # What kinds of tickets is this document relevant for?
    relevant_for: List[str] = field(default_factory=list)
    """
    Example: ["authentication_errors", "401_issues", "login_problems"]
    Used to compute retrieval precision/recall
    """


@dataclass
class EndToEndTestCase:
    """
    Schema for a full end-to-end workflow test case.
    
    Tests the entire pipeline from ticket to action.
    
    REQUIRED FIELDS:
    - case_id: Unique identifier
    - ticket: Input ticket data
    - expected_workflow_outcome: Expected final state
    """
    
    case_id: str
    
    # Input ticket
    ticket: TicketDatasetItem
    
    # Expected outcome
    expected_workflow_outcome: Dict[str, Any]
    """
    Expected structure:
    {
        "final_status": "completed" | "paused_for_human" | "failed",
        "recommended_action": str,
        "should_retrieve_docs_from": List[str],  # Expected source files
        "human_review_required": bool
    }
    """
    
    # Validation
    expected_risk_flags: List[str] = field(default_factory=list)
    expected_min_confidence: float = 0.0


# === Dataset Container Contracts ===

@dataclass
class EvaluationDataset:
    """
    Container for an evaluation dataset.
    
    This is the top-level structure that evaluation runners expect.
    """
    
    # Metadata
    dataset_id: str
    name: str
    description: str
    version: str
    created_at: str
    
    # Dataset type
    dataset_type: Literal["tickets", "documents", "end_to_end"]
    
    # Items (generic, typed by dataset_type)
    items: List[Any]
    
    # Provenance
    source: str  # Where did this data come from?
    labeling_guidelines_version: Optional[str] = None
    
    def __len__(self) -> int:
        return len(self.items)


# === Example Structures (NOT REAL DATA) ===

EXAMPLE_TICKET_ITEM = {
    "_comment": "This is an EXAMPLE, not real data",
    "ticket_id": "example-001",
    "ticket_data": {
        "subject": "API returns 401 on valid credentials",
        "body": "We are getting authentication errors when...",
        "customer_id": "acme-corp",
        "created_at": "2026-01-25T10:00:00Z",
        "metadata": {"priority_override": None}
    },
    "expected_triage": {
        "ticket_type": "bug",
        "severity": "high",
        "keywords": ["authentication", "401", "API"],
        "requires_escalation": False
    },
    "expected_action": "auto_respond",
    "notes": "Standard auth issue, docs available"
}

EXAMPLE_E2E_CASE = {
    "_comment": "This is an EXAMPLE, not real data",
    "case_id": "e2e-example-001",
    "expected_workflow_outcome": {
        "final_status": "paused_for_human",
        "recommended_action": "auto_respond",
        "should_retrieve_docs_from": ["authentication.md", "troubleshooting_auth_errors.md"],
        "human_review_required": True
    },
    "expected_risk_flags": [],
    "expected_min_confidence": 0.7
}


# === Dataset Loading Stubs ===

def load_dataset(path: str) -> EvaluationDataset:
    """
    Load an evaluation dataset from disk.
    
    TODO: Implement when real datasets exist
    
    Expected format: JSON file matching EvaluationDataset schema
    """
    raise NotImplementedError(
        "Dataset loading not implemented. "
        "This is infrastructure only — no real datasets exist yet."
    )


def validate_dataset(dataset: EvaluationDataset) -> List[str]:
    """
    Validate a dataset against its schema.
    
    TODO: Implement validation logic
    
    Returns list of validation errors (empty if valid)
    """
    errors = []
    
    # TODO: Validate required fields
    # TODO: Validate item schemas based on dataset_type
    # TODO: Validate labeling consistency
    
    return errors
