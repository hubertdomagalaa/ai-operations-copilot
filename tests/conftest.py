"""
Pytest Configuration
====================

Shared fixtures and configuration for all tests.

WHY THIS FILE EXISTS:
- Defines fixtures used across test modules
- Configures pytest behavior
- Provides mock services for testing
"""

import pytest
from typing import Dict, Any


# === Fixtures ===

@pytest.fixture
def sample_ticket() -> Dict[str, Any]:
    """
    A sample ticket for testing.
    
    Represents a typical API authentication issue.
    """
    return {
        "ticket_id": "test-ticket-001",
        "subject": "API authentication failing with 401 error",
        "body": """
        Hi Support,
        
        We're getting 401 Unauthorized errors when calling the /users endpoint.
        Our API key was working fine yesterday but started failing this morning.
        
        The error message says "Invalid API key" but we haven't changed anything.
        
        Can you please help? This is blocking our production deployment.
        
        Thanks,
        Customer
        """,
        "source": "email",
        "customer_id": "cust-12345",
        "metadata": {
            "endpoint": "/users",
            "error_code": 401,
        },
    }


@pytest.fixture
def sample_triage_output() -> Dict[str, Any]:
    """
    Sample triage agent output for testing.
    """
    return {
        "agent_type": "triage",
        "success": True,
        "result": {
            "category": "authentication",
            "priority": "high",
            "summary": "API key authentication failure on /users endpoint",
            "keywords": ["api", "authentication", "401", "unauthorized"],
        },
        "confidence": 0.92,
        "reasoning": "Clear authentication error with specific endpoint mentioned",
        "requires_human_review": False,
    }


@pytest.fixture
def sample_workflow_state(sample_ticket, sample_triage_output) -> Dict[str, Any]:
    """
    Sample workflow state for testing.
    """
    return {
        "ticket_id": sample_ticket["ticket_id"],
        "ticket_data": sample_ticket,
        "trace_id": "test-trace-001",
        "started_at": "2024-01-01T12:00:00Z",
        "status": "running",
        "current_step": "knowledge",
        "triage_output": sample_triage_output,
        "knowledge_output": None,
        "decision_output": None,
        "action_output": None,
        "retrieved_documents": None,
        "human_decision_required": False,
        "human_decision": None,
        "error": None,
        "error_step": None,
        "updated_at": "2024-01-01T12:00:05Z",
        "completed_at": None,
    }


@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """
    Mock LLM response for testing.
    """
    return {
        "content": "This is a mock LLM response.",
        "structured_output": None,
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "model": "mock-model",
        "provider": "mock",
        "latency_ms": 100,
    }


@pytest.fixture
def mock_retrieved_documents() -> list:
    """
    Mock RAG retrieval results for testing.
    """
    return [
        {
            "content": "API key authentication requires a valid key in the X-API-Key header.",
            "metadata": {"source": "api_docs/authentication.md", "chunk_id": 1},
            "score": 0.95,
            "document_id": "doc-001",
        },
        {
            "content": "401 errors indicate authentication failure. Check API key validity.",
            "metadata": {"source": "troubleshooting/auth_errors.md", "chunk_id": 3},
            "score": 0.88,
            "document_id": "doc-002",
        },
    ]


# === Markers ===

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "evaluation: marks tests as evaluation tests"
    )
