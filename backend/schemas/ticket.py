"""
Ticket Schemas
==============

Pydantic models for support ticket data.

WHY THIS FILE EXISTS:
- Validates incoming ticket data from API
- Defines the canonical ticket representation
- Ensures consistent ticket format across the system

MODELS:
- TicketInput: What operators submit when creating a ticket
- TicketStatus: Enum of possible ticket states
- TicketClassification: Output from triage agent
- TicketResponse: Full ticket data returned by API
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

# TODO: Uncomment when pydantic is installed
# from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    """Possible states of a support ticket in the system."""
    
    PENDING = "pending"          # Newly ingested, not yet processed
    TRIAGING = "triaging"        # Being classified by triage agent
    RESEARCHING = "researching"  # Knowledge agent retrieving context
    DECIDING = "deciding"        # Decision agent evaluating options
    AWAITING_HUMAN = "awaiting_human"  # Needs human operator decision
    RESOLVED = "resolved"        # Processing complete
    ESCALATED = "escalated"      # Escalated to human without AI action
    FAILED = "failed"            # Processing failed, needs manual review


class TicketPriority(str, Enum):
    """Priority levels assigned by triage agent."""
    
    CRITICAL = "critical"  # System down, immediate action required
    HIGH = "high"          # Significant impact, urgent
    MEDIUM = "medium"      # Moderate impact, normal queue
    LOW = "low"            # Minor issue, can wait


class TicketCategory(str, Enum):
    """
    Categories for ticket classification.
    
    These map to the B2B SaaS REST API context:
    - Authentication issues
    - API errors
    - Performance problems
    - Feature questions
    - Billing/account issues
    """
    
    AUTHENTICATION = "authentication"
    API_ERROR = "api_error"
    PERFORMANCE = "performance"
    FEATURE_QUESTION = "feature_question"
    BILLING = "billing"
    OTHER = "other"


# TODO: Convert to Pydantic models when dependencies are installed

class TicketInput:
    """
    Schema for ticket ingestion request.
    
    This is what an operator submits when creating a new ticket.
    The system generates an ID and timestamps automatically.
    """
    
    # Required fields
    subject: str              # Ticket subject line
    body: str                 # Full ticket content
    source: str               # Where ticket came from (email, portal, api)
    
    # Optional fields
    customer_id: Optional[str] = None
    external_ticket_id: Optional[str] = None  # ID from external system
    metadata: Optional[dict] = None           # Additional context


class TicketClassification:
    """
    Output from the triage agent.
    
    Contains the AI's initial assessment of the ticket.
    All fields include confidence scores for transparency.
    """
    
    category: TicketCategory
    category_confidence: float  # 0.0 to 1.0
    
    priority: TicketPriority
    priority_confidence: float
    
    summary: str                # AI-generated summary
    keywords: List[str]         # Extracted keywords for search
    
    requires_escalation: bool   # Whether human must handle
    escalation_reason: Optional[str] = None


class TicketResponse:
    """
    Full ticket representation returned by API.
    
    Includes original input, AI processing results,
    and current status.
    """
    
    # Identifiers
    ticket_id: str
    external_ticket_id: Optional[str]
    
    # Original content
    subject: str
    body: str
    source: str
    customer_id: Optional[str]
    
    # Processing state
    status: TicketStatus
    classification: Optional[TicketClassification]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    
    # Recommendations (from decision agent)
    recommendations: Optional[List[str]]
    draft_response: Optional[str]
