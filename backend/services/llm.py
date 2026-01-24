"""
LLM Service Abstraction
=======================

Provides a unified interface for LLM interactions.

WHY THIS FILE EXISTS:
- Abstracts LLM provider differences (OpenAI, Anthropic, local)
- Enables provider switching without code changes
- Centralizes prompt management and response parsing
- Supports structured output via response schemas

USAGE:
    from backend.services.llm import get_llm_service
    
    llm = get_llm_service()
    response = await llm.generate(prompt="...", schema=OutputSchema)

DESIGN DECISIONS:
- Provider is configured via environment variable
- All prompts are logged for observability
- Responses include token usage for cost tracking
- Structured outputs preferred via LangChain
"""

from typing import Optional, Dict, Any, Protocol, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')


class LLMResponse:
    """
    Standardized LLM response wrapper.
    
    Includes content, token usage, and metadata.
    """
    
    content: str
    structured_output: Optional[Dict[str, Any]] = None
    
    # Token usage for cost tracking
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    # Model info
    model: str
    provider: str
    
    # Timing
    latency_ms: int


class LLMService(ABC):
    """
    Abstract base class for LLM services.
    
    Implementations must provide these methods.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        Generate a text response from the LLM.
        
        TODO: Implement in provider-specific subclass
        """
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate a structured response matching the schema.
        
        Uses LangChain's structured output capabilities.
        
        TODO: Implement in provider-specific subclass
        """
        pass


class MockLLMService(LLMService):
    """
    Mock LLM service for testing.
    
    Returns predictable responses without making API calls.
    """
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Return a mock response."""
        # TODO: Implement mock logic
        raise NotImplementedError("Mock not implemented")
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """Return a mock structured response."""
        # TODO: Implement mock logic
        raise NotImplementedError("Mock not implemented")


def get_llm_service() -> LLMService:
    """
    Factory function to get the configured LLM service.
    
    Reads provider from config and returns appropriate implementation.
    
    TODO: Implement provider detection and instantiation
    """
    # TODO: Read from config.settings.llm_provider
    # TODO: Return appropriate implementation
    return MockLLMService()
