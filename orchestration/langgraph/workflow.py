"""
Main Workflow Definition
========================

Builds the LangGraph workflow for ticket processing.

WHY THIS FILE EXISTS:
- Single source of truth for workflow structure
- Compiles the graph for execution
- Provides entry point for workflow execution

THE WORKFLOW (State Machine):
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │   ┌─────────┐                                                       │
    │   │  START  │                                                       │
    │   └────┬────┘                                                       │
    │        │                                                            │
    │   ┌────▼────┐                                                       │
    │   │ TRIAGE  │  ← Classifies and prioritizes ticket                  │
    │   └────┬────┘                                                       │
    │        │                                                            │
    │        ▼                                                            │
    │   [route_after_triage]                                              │
    │        │                                                            │
    │        ├── "knowledge" ──► ┌───────────┐                            │
    │        │                   │ KNOWLEDGE │ ← RAG retrieval            │
    │        │                   └─────┬─────┘                            │
    │        │                         │                                  │
    │        │                    ┌────▼────┐                             │
    │        │                    │DECISION │ ← Recommends action         │
    │        │                    └────┬────┘                             │
    │        │                         │                                  │
    │        │                         ▼                                  │
    │        │                [route_after_decision]                      │
    │        │                         │                                  │
    │        │          ┌──────────────┴──────────────┐                   │
    │        │          │                             │                   │
    │        │     "action"                    "human_review"             │
    │        │          │                             │                   │
    │        │     ┌────▼────┐               ┌────────▼────────┐          │
    │        │     │ ACTION  │               │  HUMAN_REVIEW   │          │
    │        │     └────┬────┘               │ (checkpoint)    │          │
    │        │          │                    └────────┬────────┘          │
    │        │          │                             │                   │
    │        │          │                    [route_after_human]          │
    │        │          │                             │                   │
    │        │          │              ┌──────────────┼──────────────┐    │
    │        │          │              │              │              │    │
    │        │          │         "action"       "complete"     "cancel"  │
    │        │          │              │              │              │    │
    │        │          │         ┌────▼────┐        │              ▼     │
    │        │          │         │ ACTION  │        │            [END]   │
    │        │          │         └────┬────┘        │                    │
    │        │          │              │             │                    │
    │        │          └──────────────┼─────────────┘                    │
    │        │                         │                                  │
    │        │                    ┌────▼─────┐                            │
    │        │                    │MONITORING│ ← Logs metrics, feedback   │
    │        │                    └────┬─────┘                            │
    │        │                         │                                  │
    │        │                    ┌────▼────┐                             │
    │        ├── "escalate" ────► │COMPLETE │                             │
    │        │                    └────┬────┘                             │
    │        │                         │                                  │
    │        ├── "error" ──────► ┌─────▼─────┐                            │
    │        │                   │   ERROR   │ ──────► [END]              │
    │        │                   └───────────┘                            │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

DESIGN DECISIONS:
- Linear flow by default (triage → knowledge → decision → action)
- Branching only where business logic requires it
- Human-in-the-loop is a checkpoint, not a separate branch
- Monitoring node runs before completion for every successful path
- Error node is a terminal state
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from orchestration.langgraph.state import TicketProcessingState, create_initial_state
from orchestration.langgraph.nodes import (
    triage_node,
    knowledge_node,
    decision_node,
    action_node,
    human_review_node,
    monitoring_node,
    complete_node,
    error_node,
)
from orchestration.langgraph.edges import (
    route_after_triage,
    route_after_decision,
    route_after_human_review,
)


def build_workflow(checkpointer: Optional[MemorySaver] = None) -> StateGraph:
    """
    Build and compile the ticket processing workflow.
    
    This function constructs the LangGraph state machine that orchestrates
    all agents in the ticket processing pipeline.
    
    Args:
        checkpointer: Optional checkpointer for state persistence.
                      If None, uses MemorySaver for in-memory checkpointing.
    
    Returns:
        Compiled StateGraph ready for execution.
    
    WHY THIS STRUCTURE:
    - StateGraph provides explicit state machine semantics
    - Conditional edges enable routing based on agent outputs
    - Checkpointing enables human-in-the-loop pausing and resumption
    """
    # Create the state graph with our typed state
    workflow = StateGraph(TicketProcessingState)
    
    # === ADD NODES ===
    # Each node corresponds to an agent or system function
    
    workflow.add_node("triage", triage_node)
    # WHY: First agent to process ticket. Classifies, prioritizes, extracts keywords.
    
    workflow.add_node("knowledge", knowledge_node)
    # WHY: Retrieves relevant documents via RAG to provide context for decisions.
    
    workflow.add_node("decision", decision_node)
    # WHY: Synthesizes information and recommends action (escalate/automate/manual).
    
    workflow.add_node("action", action_node)
    # WHY: Drafts response and executes approved actions.
    
    workflow.add_node("human_review", human_review_node)
    # WHY: Checkpoint for human operator to review and approve/modify AI decisions.
    
    workflow.add_node("monitoring", monitoring_node)
    # WHY: Records metrics, logs, and evaluation data before completing.
    
    workflow.add_node("complete", complete_node)
    # WHY: Terminal node that marks workflow as successfully completed.
    
    workflow.add_node("error", error_node)
    # WHY: Terminal node for failed workflows. Logs error and alerts operators.
    
    # === SET ENTRY POINT ===
    workflow.set_entry_point("triage")
    # WHY: Every ticket starts with triage for classification.
    
    # === ADD EDGES ===
    
    # After triage: route based on urgency and errors
    workflow.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "knowledge": "knowledge",    # Normal flow: continue to RAG
            "escalate": "human_review",  # Urgent: skip to human immediately
            "error": "error",            # Triage failed: go to error handler
        }
    )
    # WHY: Triage may detect urgent tickets that need immediate human attention,
    #      or may fail due to invalid input, requiring different routing.
    
    # After knowledge: always proceed to decision
    workflow.add_edge("knowledge", "decision")
    # WHY: Knowledge retrieval always precedes decision-making.
    #      No branching here because retrieval can return empty results gracefully.
    
    # After decision: route based on confidence and risk
    workflow.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "action": "action",           # High confidence: proceed directly
            "human_review": "human_review", # Low confidence or high risk: require human
        }
    )
    # WHY: High-confidence, low-risk decisions can proceed automatically.
    #      Uncertain or risky decisions require human approval.
    
    # After human review: route based on human's decision
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "action": "action",     # Human approved: proceed with action
            "complete": "complete", # Human handled manually: mark complete
            "cancel": END,          # Human cancelled: end workflow
            "wait": END,            # Waiting for human: pause (will resume later)
        }
    )
    # WHY: Human can approve AI recommendation, handle ticket manually,
    #      or cancel the workflow entirely.
    
    # After action: proceed to monitoring
    workflow.add_edge("action", "monitoring")
    # WHY: Every completed action should be logged for evaluation.
    
    # After monitoring: proceed to complete
    workflow.add_edge("monitoring", "complete")
    # WHY: Monitoring is the last step before marking workflow done.
    
    # Terminal edges
    workflow.add_edge("complete", END)
    workflow.add_edge("error", END)
    
    # === COMPILE WITH CHECKPOINTING ===
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    compiled = workflow.compile(checkpointer=checkpointer)
    
    return compiled


async def run_workflow(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute the workflow for a new ticket.
    
    This is the main entry point for ticket processing.
    
    Args:
        ticket_id: Unique ticket identifier
        ticket_data: Raw ticket content from ingestion
        config: Optional LangGraph config (for thread_id, etc.)
    
    Returns:
        Final workflow state after completion or pause
    
    USAGE:
        result = await run_workflow(
            ticket_id="ticket-123",
            ticket_data={"subject": "...", "body": "..."},
        )
    """
    import uuid
    
    # Create initial state
    trace_id = str(uuid.uuid4())
    initial_state = create_initial_state(ticket_id, ticket_data, trace_id)
    
    # Build workflow
    workflow = build_workflow()
    
    # Set up config for checkpointing
    if config is None:
        config = {"configurable": {"thread_id": ticket_id}}
    
    # Execute workflow
    # TODO: Add error handling for workflow execution
    final_state = await workflow.ainvoke(initial_state, config)
    
    return final_state


async def resume_workflow(
    ticket_id: str,
    human_decision: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Resume a paused workflow after human input.
    
    Called when a human operator provides their decision
    for a workflow that was paused at human_review node.
    
    Args:
        ticket_id: Ticket with paused workflow
        human_decision: Human's decision, e.g.:
            {"action": "approve", "modified_response": "..."}
            {"action": "manual", "notes": "Handled via phone"}
            {"action": "cancel", "reason": "Duplicate ticket"}
    
    Returns:
        Final workflow state after resumption
    
    USAGE:
        result = await resume_workflow(
            ticket_id="ticket-123",
            human_decision={"action": "approve"},
        )
    """
    # Build workflow with same checkpointer
    workflow = build_workflow()
    
    # Set up config for resumption
    if config is None:
        config = {"configurable": {"thread_id": ticket_id}}
    
    # Get current state from checkpoint
    # TODO: Load actual checkpoint state
    current_state = await workflow.aget_state(config)
    
    if current_state is None:
        raise ValueError(f"No paused workflow found for ticket: {ticket_id}")
    
    # Update state with human decision
    updated_values = {
        "human_decision": human_decision,
    }
    
    # Resume from checkpoint with updated state
    await workflow.aupdate_state(config, updated_values)
    
    # Continue execution
    final_state = await workflow.ainvoke(None, config)
    
    return final_state


def get_workflow_status(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the current status of a workflow.
    
    Useful for checking if a workflow is paused, completed, or failed.
    
    Args:
        ticket_id: Ticket to check
    
    Returns:
        Current state if workflow exists, None otherwise
    """
    workflow = build_workflow()
    config = {"configurable": {"thread_id": ticket_id}}
    
    # TODO: This is synchronous; may need async version
    try:
        state = workflow.get_state(config)
        return state.values if state else None
    except Exception:
        return None
