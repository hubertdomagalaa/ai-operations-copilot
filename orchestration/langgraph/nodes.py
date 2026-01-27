"""
Workflow Node Definitions
=========================

Node functions for the LangGraph workflow.

WHY THIS FILE EXISTS:
- Each node wraps an agent's process() method
- Nodes handle state updates consistently
- Separates graph structure from agent logic

NODES IN THE WORKFLOW:
1. triage_node — Classifies ticket
2. knowledge_node — Retrieves context
3. decision_node — Recommends action
4. action_node — Drafts response
5. human_review_node — Pauses for human input

Each node:
1. Reads from state
2. Calls the appropriate agent
3. Updates state with results
4. Returns updated state
"""

from typing import Dict, Any
from datetime import datetime

from orchestration.langgraph.state import TicketProcessingState


async def triage_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Node that invokes the triage agent.
    
    Classifies and prioritizes the ticket.
    Updates state with triage output.
    
    WHY THIS NODE EXISTS:
    - First intelligence step in the workflow
    - Determines routing (normal vs escalation)
    - Extracts keywords for RAG retrieval
    """
    from agents.triage import TriageAgent
    
    state["current_step"] = "triage"
    state["status"] = "running"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    try:
        # Get LLM service (uses mock in dry run, real in production)
        llm_service = _get_llm_service()
        
        # Instantiate and run triage agent
        agent = TriageAgent(llm_service=llm_service)
        result = await agent.process(state)
        
        # Update state with agent output
        state["triage_output"] = result
        
        # Check for errors that should route to error node
        if not result.get("success", True):
            state["error"] = result.get("result", {}).get("error", "Triage failed")
            state["error_step"] = "triage"
        
    except Exception as e:
        # Triage failed - record error and continue to error handling
        state["triage_output"] = {
            "success": False,
            "agent_type": "triage",
            "error": str(e),
        }
        state["error"] = str(e)
        state["error_step"] = "triage"
        print(f"Triage agent error: {e}")
    
    return state


# Module-level LLM service for dependency injection
_llm_service_override = None


def set_llm_service(service):
    """Set LLM service for testing/dry run."""
    global _llm_service_override
    _llm_service_override = service


def _get_llm_service():
    """Get LLM service (allows override for testing)."""
    global _llm_service_override
    if _llm_service_override is not None:
        return _llm_service_override
    # Default: return None, let agent use its default
    return None



async def knowledge_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Node that invokes the knowledge agent.
    
    Retrieves relevant documents via RAG.
    
    WHY THIS NODE EXISTS:
    - Provides grounded context for downstream agents
    - All facts must be traceable to sources
    - No retrieval = no answer principle
    """
    from agents.knowledge import KnowledgeAgent
    
    state["current_step"] = "knowledge"
    state["status"] = "running"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    try:
        # Instantiate and run knowledge agent
        agent = KnowledgeAgent()
        result = await agent.process(state)
        
        # Update state with agent output
        state["knowledge_output"] = result
        
        # Extract retrieved documents for easy access
        if result.get("success") and result.get("result"):
            state["retrieved_documents"] = result["result"].get("documents", [])
        else:
            state["retrieved_documents"] = []
        
        # TODO: Log retrieval metrics for observability
        
    except Exception as e:
        # Log error but don't fail workflow
        # Knowledge retrieval is important but not blocking
        state["knowledge_output"] = {
            "success": False,
            "agent_type": "knowledge",
            "error": str(e),
        }
        state["retrieved_documents"] = []
        # TODO: Log error properly
        print(f"Knowledge agent error: {e}")
    
    return state


async def decision_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Node that invokes the decision agent.
    
    Synthesizes triage + knowledge signals to produce a recommendation.
    
    WHY THIS NODE EXISTS:
    - Combines upstream signals into actionable recommendation
    - Determines if human approval is required
    - Sets human_decision_required flag for routing
    """
    from agents.decision import DecisionAgent
    
    state["current_step"] = "decision"
    state["status"] = "running"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    try:
        # Instantiate and run decision agent
        agent = DecisionAgent()
        result = await agent.process(state)
        
        # Update state with decision output
        state["decision_output"] = result
        
        # Set human_decision_required based on agent output
        # This flag drives the route_after_decision routing
        requires_approval = result.get("requires_human_review", True)
        state["human_decision_required"] = requires_approval
        
        # TODO: Log decision metrics for observability
        
    except Exception as e:
        # Decision failed — require human review as fallback
        state["decision_output"] = {
            "success": False,
            "agent_type": "decision",
            "error": str(e),
        }
        state["human_decision_required"] = True
        # TODO: Log error properly
        print(f"Decision agent error: {e}")
    
    return state


async def action_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Node that invokes the action agent.
    
    Prepares draft responses or action checklists.
    
    WHY THIS NODE EXISTS:
    - Generates grounded, reviewable artifacts
    - Operates ONLY after human approval
    - Never executes actions — only prepares drafts
    
    PRECONDITION:
    This node should only be reached if human approval was given.
    The workflow routing ensures this via route_after_human_review.
    """
    from agents.action import ActionAgent
    
    state["current_step"] = "action"
    state["status"] = "running"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    # Mark approval status for audit trail
    human_decision = state.get("human_decision") or {}
    if human_decision.get("action") == "approve":
        state["human_approval_status"] = "approved"
    
    try:
        # Instantiate and run action agent
        agent = ActionAgent()
        result = await agent.process(state)
        
        # Update state with action output
        state["action_output"] = result
        
        # TODO: Log action metrics for observability
        
    except RuntimeError as e:
        # Safety violation — approval missing
        state["action_output"] = {
            "success": False,
            "agent_type": "action",
            "error": str(e),
        }
        state["error"] = str(e)
        # TODO: Alert on safety violation
        print(f"ACTION AGENT SAFETY VIOLATION: {e}")
        
    except Exception as e:
        # Other errors
        state["action_output"] = {
            "success": False,
            "agent_type": "action",
            "error": str(e),
        }
        # TODO: Log error properly
        print(f"Action agent error: {e}")
    
    return state


async def monitoring_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Node that records metrics, logs, and evaluation hooks.
    
    This node runs after action and before completion.
    It captures data for observability and system improvement.
    
    RESPONSIBILITIES:
    - Record workflow timing metrics
    - Log agent confidence scores
    - Capture data for evaluation pipeline
    - Emit events for dashboards
    
    WHY THIS NODE EXISTS:
    - Observability is a first-class concern
    - Need to measure and improve AI quality
    - Compliance and audit trail requirements
    
    TODO: Implement monitoring logic
    """
    state["current_step"] = "monitoring"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    # TODO: Calculate workflow duration
    # started = datetime.fromisoformat(state["started_at"])
    # duration_ms = (datetime.utcnow() - started).total_seconds() * 1000
    
    # TODO: Record metrics
    # from observability.metrics import workflow_duration, agent_confidence
    # workflow_duration.observe(duration_ms / 1000, {"status": state["status"]})
    
    # TODO: Log confidence scores from each agent
    # if state.get("triage_output"):
    #     confidence = state["triage_output"].get("confidence", 0)
    #     agent_confidence.observe(confidence, {"agent_type": "triage"})
    
    # TODO: Emit evaluation event
    # This data will be used for quality monitoring
    # evaluation_event = {
    #     "ticket_id": state["ticket_id"],
    #     "trace_id": state["trace_id"],
    #     "triage_confidence": state.get("triage_output", {}).get("confidence"),
    #     "decision_confidence": state.get("decision_output", {}).get("confidence"),
    #     "human_override": state.get("human_decision") is not None,
    # }
    
    return state


async def human_review_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Human-in-the-loop checkpoint node.
    
    WHY THIS NODE EXISTS:
    - AI assists decisions; it does not replace human judgment
    - Human approval is MANDATORY before any action execution
    - This is not optional — it's a core system principle
    
    WORKFLOW BEHAVIOR:
    - This node sets status to 'paused_for_human'
    - LangGraph checkpointing preserves state
    - Workflow resumes when human provides decision via API
    - Human can: approve, modify, handle manually, or cancel
    
    WHAT GETS EXPOSED TO HUMAN:
    - Ticket content
    - Triage classification
    - Retrieved documents (with citations)
    - Decision recommendation with reasoning
    - Risk flags
    
    NOTE: This node may be reached via:
    - Normal flow (after decision) - decision_output present
    - Escalation path (after triage) - decision_output is None
    """
    state["current_step"] = "human_review"
    state["status"] = "paused_for_human"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    # Build summary for human operator
    # Handle both normal path (has decision) and escalation path (no decision)
    decision_output = state.get("decision_output") or {}
    decision_result = decision_output.get("result", {}) if decision_output else {}
    
    # For escalation path, use triage info
    triage_output = state.get("triage_output") or {}
    triage_result = triage_output.get("result", {}) if triage_output else {}
    
    # Determine what to show
    if decision_result:
        recommended_action = decision_result.get("recommended_action", "unknown")
        confidence = decision_output.get("confidence", 0)
        risk_flags = decision_result.get("risk_flags", [])
        reasoning = decision_result.get("reasoning_summary", "No reasoning")
    else:
        # Escalation path - use triage info
        recommended_action = "escalate" if triage_result.get("requires_escalation") else "review"
        confidence = triage_output.get("confidence", 0)
        risk_flags = triage_result.get("escalation_reasons", [])
        reasoning = f"Escalated from triage: {', '.join(risk_flags)}" if risk_flags else "Immediate escalation required"
    
    # Log checkpoint event for observability
    print(f"[HUMAN REVIEW REQUIRED] Ticket: {state.get('ticket_id')}")
    print(f"  Recommended action: {recommended_action}")
    print(f"  Confidence: {confidence:.2f}" if isinstance(confidence, (int, float)) else f"  Confidence: {confidence}")
    print(f"  Risk flags: {risk_flags}")
    print(f"  Reasoning: {reasoning}")
    
    # TODO: Integrate with notification service
    # from observability.events import emit_human_review_required
    # await emit_human_review_required(
    #     ticket_id=state["ticket_id"],
    #     decision=decision_result,
    # )
    
    return state


async def complete_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Terminal node marking workflow completion.
    """
    state["current_step"] = "complete"
    state["status"] = "completed"
    state["updated_at"] = datetime.utcnow().isoformat()
    state["completed_at"] = datetime.utcnow().isoformat()
    
    # TODO: Emit completion event
    # TODO: Update ticket in storage
    
    return state


async def error_node(state: TicketProcessingState) -> TicketProcessingState:
    """
    Error handling node.
    
    Called when an agent fails or unexpected error occurs.
    """
    state["status"] = "failed"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    # TODO: Log error details
    # TODO: Emit error event for alerting
    
    return state
