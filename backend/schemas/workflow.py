"""
Workflow Schemas
================

Pydantic models for workflow state and orchestration.

WHY THIS FILE EXISTS:
- Defines the state shape for LangGraph workflows
- Tracks workflow progress through agents
- Enables workflow state persistence and recovery

MODELS:
- WorkflowState: The full state passed through LangGraph
- WorkflowEvent: Events emitted during processing
- WorkflowStatus: Overall workflow status enum
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Overall status of a workflow execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    PAUSED_FOR_HUMAN = "paused_for_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState:
    """
    The state object passed through the LangGraph workflow.
    
    This is THE canonical state representation. It flows through
    each agent node and accumulates results.
    
    WHY THIS STRUCTURE:
    - ticket_data: Original input, immutable
    - agent_outputs: Results from each agent, builds up
    - current_step: Where we are in the workflow
    - metadata: Tracing and timing information
    
    TODO: Convert to TypedDict for LangGraph compatibility
    """
    
    # Original ticket (immutable through workflow)
    ticket_id: str
    ticket_data: Dict[str, Any]
    
    # Overall status
    status: WorkflowStatus
    current_step: str
    
    # Agent outputs (accumulated)
    triage_output: Optional[Dict[str, Any]] = None
    knowledge_output: Optional[Dict[str, Any]] = None
    decision_output: Optional[Dict[str, Any]] = None
    action_output: Optional[Dict[str, Any]] = None
    
    # Retrieved knowledge
    retrieved_documents: Optional[List[Dict[str, Any]]] = None
    
    # Human-in-the-loop
    human_decision_required: bool = False
    human_decision: Optional[Dict[str, Any]] = None
    
    # Error handling
    error: Optional[str] = None
    error_step: Optional[str] = None
    
    # Metadata
    trace_id: str
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowEvent:
    """
    Events emitted during workflow processing.
    
    Used for:
    - Real-time monitoring dashboards
    - Audit logging
    - Debugging
    """
    
    event_type: str  # "step_started", "step_completed", "error", etc.
    workflow_id: str
    ticket_id: str
    
    # Event details
    step: str
    payload: Dict[str, Any]
    
    # Timing
    timestamp: datetime
