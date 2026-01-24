"""
Custom Exceptions
=================

Defines application-specific exceptions for consistent error handling.

WHY THIS FILE EXISTS:
- Provides semantic error types for different failure modes
- Enables consistent error responses in API layer
- Supports structured error logging and monitoring

USAGE:
    from backend.core.exceptions import TicketNotFoundError
    
    raise TicketNotFoundError(ticket_id="123")

DESIGN DECISIONS:
- All exceptions inherit from a base CopilotError
- Each exception includes relevant context for debugging
- Error codes map to HTTP status codes in API layer
"""


class CopilotError(Exception):
    """
    Base exception for all AI Operations Copilot errors.
    
    Attributes:
        message: Human-readable error description
        error_code: Machine-readable error identifier
    """
    
    def __init__(self, message: str, error_code: str = "COPILOT_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TicketNotFoundError(CopilotError):
    """Raised when a requested ticket does not exist."""
    
    def __init__(self, ticket_id: str):
        super().__init__(
            message=f"Ticket not found: {ticket_id}",
            error_code="TICKET_NOT_FOUND"
        )
        self.ticket_id = ticket_id


class WorkflowError(CopilotError):
    """Raised when the agent workflow encounters an error."""
    
    def __init__(self, message: str, ticket_id: str = None):
        super().__init__(
            message=message,
            error_code="WORKFLOW_ERROR"
        )
        self.ticket_id = ticket_id


class RAGRetrievalError(CopilotError):
    """Raised when knowledge retrieval fails."""
    
    def __init__(self, message: str, query: str = None):
        super().__init__(
            message=message,
            error_code="RAG_RETRIEVAL_ERROR"
        )
        self.query = query


class LLMError(CopilotError):
    """Raised when LLM invocation fails."""
    
    def __init__(self, message: str, provider: str = None):
        super().__init__(
            message=message,
            error_code="LLM_ERROR"
        )
        self.provider = provider


class ValidationError(CopilotError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR"
        )
        self.field = field
