"""
LangGraph State Definitions
===========================

TypedDict-based state for LangGraph workflows.

WHY THIS FILE EXISTS:
- LangGraph requires explicit state typing
- TypedDict enables type-safe state access in nodes
- State shape is the contract between all nodes

THE STATE IS THE SOURCE OF TRUTH:
- All nodes read from state
- All nodes write to state
- State is persisted for workflow recovery
"""

from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class TicketProcessingState(TypedDict):
    """
    State for the ticket processing workflow.
    
    This state flows through all agents in the workflow.
    Each agent reads what it needs and adds its output.
    
    IMMUTABLE FIELDS (set at start):
    - ticket_id: Unique ticket identifier
    - ticket_data: Original ticket content
    - trace_id: For observability
    - started_at: Workflow start time
    
    MUTABLE FIELDS (updated by agents):
    - status: Current workflow status
    - current_step: Which agent is processing
    - triage_output: From triage agent
    - knowledge_output: From knowledge agent
    - decision_output: From decision agent
    - action_output: From action agent
    - human_decision: Human override if any
    - error: Error message if failed
    """
    
    # === Immutable (set at workflow start) ===
    ticket_id: str
    ticket_data: Dict[str, Any]
    trace_id: str
    started_at: str  # ISO format datetime
    
    # === Processing State ===
    status: str  # "pending", "running", "paused_for_human", "completed", "failed"
    current_step: str  # Current node name
    
    # === Agent Outputs ===
    triage_output: Optional[Dict[str, Any]]
    knowledge_output: Optional[Dict[str, Any]]
    decision_output: Optional[Dict[str, Any]]
    action_output: Optional[Dict[str, Any]]
    monitoring_output: Optional[Dict[str, Any]]  # Metrics and evaluation data
    
    # === Retrieved Knowledge ===
    retrieved_documents: Optional[List[Dict[str, Any]]]
    
    # === Human-in-the-Loop ===
    human_decision_required: bool
    human_decision: Optional[Dict[str, Any]]
    human_approval_status: Optional[str]  # "pending", "approved", "rejected", "modified"
    
    # === Error Handling ===
    error: Optional[str]
    error_step: Optional[str]
    
    # === Timing ===
    updated_at: str  # ISO format datetime
    completed_at: Optional[str]


def create_initial_state(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    trace_id: str,
) -> TicketProcessingState:
    """
    Create the initial workflow state for a new ticket.
    
    Use this when starting a new workflow execution.
    """
    now = datetime.utcnow().isoformat()
    
    return TicketProcessingState(
        # Immutable
        ticket_id=ticket_id,
        ticket_data=ticket_data,
        trace_id=trace_id,
        started_at=now,
        
        # Processing state
        status="pending",
        current_step="start",
        
        # Agent outputs (empty)
        triage_output=None,
        knowledge_output=None,
        decision_output=None,
        action_output=None,
        monitoring_output=None,
        
        # Knowledge
        retrieved_documents=None,
        
        # Human-in-the-loop
        human_decision_required=False,
        human_decision=None,
        human_approval_status=None,
        
        # Error
        error=None,
        error_step=None,
        
        # Timing
        updated_at=now,
        completed_at=None,
    )
