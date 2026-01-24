"""
Workflow Unit Tests
===================

Unit tests for LangGraph workflow components.

These tests verify:
- State transitions
- Conditional routing
- Node behavior
- Error handling
"""

import pytest
from orchestration.langgraph.edges import (
    route_after_triage,
    route_after_decision,
    route_after_human_review,
)


class TestWorkflowRouting:
    """Tests for workflow routing functions."""
    
    def test_route_after_triage_normal(self, sample_workflow_state):
        """
        Test normal routing after triage (to knowledge).
        """
        sample_workflow_state["triage_output"] = {
            "requires_escalation": False,
        }
        sample_workflow_state["error"] = None
        
        result = route_after_triage(sample_workflow_state)
        assert result == "knowledge"
    
    def test_route_after_triage_escalation(self, sample_workflow_state):
        """
        Test routing to escalation when flagged.
        """
        sample_workflow_state["triage_output"] = {
            "requires_escalation": True,
        }
        
        result = route_after_triage(sample_workflow_state)
        assert result == "escalate"
    
    def test_route_after_triage_error(self, sample_workflow_state):
        """
        Test routing to error node on failure.
        """
        sample_workflow_state["error"] = "Some error occurred"
        
        result = route_after_triage(sample_workflow_state)
        assert result == "error"
    
    def test_route_after_decision_auto_approve(self, sample_workflow_state):
        """
        Test routing directly to action when auto-approved.
        """
        sample_workflow_state["human_decision_required"] = False
        sample_workflow_state["decision_output"] = {
            "requires_human_review": False,
        }
        
        result = route_after_decision(sample_workflow_state)
        assert result == "action"
    
    def test_route_after_decision_human_review(self, sample_workflow_state):
        """
        Test routing to human review when required.
        """
        sample_workflow_state["human_decision_required"] = True
        
        result = route_after_decision(sample_workflow_state)
        assert result == "human_review"
    
    def test_route_after_human_review_approved(self, sample_workflow_state):
        """
        Test routing after human approves.
        """
        sample_workflow_state["human_decision"] = {"action": "approve"}
        
        result = route_after_human_review(sample_workflow_state)
        assert result == "action"
    
    def test_route_after_human_review_manual(self, sample_workflow_state):
        """
        Test routing when human handles manually.
        """
        sample_workflow_state["human_decision"] = {"action": "manual"}
        
        result = route_after_human_review(sample_workflow_state)
        assert result == "complete"
    
    def test_route_after_human_review_cancelled(self, sample_workflow_state):
        """
        Test routing when human cancels.
        """
        sample_workflow_state["human_decision"] = {"action": "cancel"}
        
        result = route_after_human_review(sample_workflow_state)
        assert result == "cancel"


class TestWorkflowState:
    """Tests for workflow state management."""
    
    def test_initial_state_creation(self):
        """
        Test initial state has all required fields.
        """
        from orchestration.langgraph.state import create_initial_state
        
        state = create_initial_state(
            ticket_id="test-123",
            ticket_data={"subject": "Test"},
            trace_id="trace-abc",
        )
        
        assert state["ticket_id"] == "test-123"
        assert state["status"] == "pending"
        assert state["current_step"] == "start"
        assert state["triage_output"] is None
        assert state["error"] is None
