"""
Agent Schemas
=============

Pydantic models for agent inputs and outputs.

WHY THIS FILE EXISTS:
- Defines the contract between orchestrator and agents
- Ensures consistent agent interfaces
- Enables type-safe agent composition

MODELS:
- AgentInput: Common input structure for all agents
- AgentOutput: Common output structure with confidence
- AgentType: Enum of agent types in the system
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentType(str, Enum):
    """Types of agents in the system."""
    
    TRIAGE = "triage"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    ACTION = "action"
    MONITORING = "monitoring"


class AgentInput:
    """
    Common input structure for all agents.
    
    Each agent receives this base input and may use
    additional fields relevant to its function.
    """
    
    ticket_id: str
    ticket_content: Dict[str, Any]  # Original ticket data
    
    # Context from previous agents
    previous_outputs: Optional[Dict[str, Any]] = None
    
    # Retrieved knowledge (from knowledge agent)
    retrieved_context: Optional[List[str]] = None
    
    # Metadata for tracing
    trace_id: str
    timestamp: datetime


class AgentOutput:
    """
    Common output structure for all agents.
    
    Every agent must return this structure to maintain
    consistency in the workflow.
    """
    
    agent_type: AgentType
    success: bool
    
    # Agent-specific output
    result: Dict[str, Any]
    
    # Confidence and reasoning
    confidence: float  # 0.0 to 1.0
    reasoning: str     # Explanation for debugging/review
    
    # Sources used (for grounding)
    sources: Optional[List[str]] = None
    
    # Human-in-the-loop signals
    requires_human_review: bool = False
    human_review_reason: Optional[str] = None
    
    # Timing
    processing_time_ms: int
    timestamp: datetime


class HumanFeedback:
    """
    Feedback provided by human operator.
    
    Used for evaluation and system improvement.
    """
    
    ticket_id: str
    agent_type: AgentType
    
    # Feedback type
    action: str  # "approve", "reject", "modify"
    
    # Original vs modified
    original_output: Dict[str, Any]
    modified_output: Optional[Dict[str, Any]] = None
    
    # Quality rating
    rating: Optional[int] = None  # 1-5 scale
    comments: Optional[str] = None
    
    # Operator info
    operator_id: str
    timestamp: datetime
