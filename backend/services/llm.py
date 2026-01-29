"""
LLM Service Abstraction
=======================

Provides a unified interface for LLM interactions.

WHY THIS FILE EXISTS:
- Abstracts LLM provider differences (OpenAI, Anthropic, OpenRouter, local)
- Enables provider switching without code changes
- Centralizes prompt management and response parsing
- Supports structured output via response schemas

USAGE:
    from backend.services.llm import get_llm_service
    
    llm = get_llm_service()
    response = await llm.generate(prompt="...", schema=OutputSchema)

CONFIGURATION:
    LLM_PROVIDER: mock, openrouter
    OPENROUTER_API_KEY: API key for OpenRouter
    LLM_MODEL: Model identifier
    LLM_TEMPERATURE: Temperature setting
"""

import os
import logging
from typing import Optional, Dict, Any, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class LLMResponse:
    """
    Standardized LLM response wrapper.
    
    Includes content, token usage, and metadata.
    """
    content: str
    structured_output: Optional[Dict[str, Any]] = None
    
    # Token usage for cost tracking
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Model info
    model: str = ""
    provider: str = ""
    
    # Timing
    latency_ms: int = 0


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
        
        Uses prompt engineering or native structured output.
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
        return LLMResponse(
            content="Mock response - no real LLM call made",
            provider="mock",
            model="mock",
        )
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """Return a mock structured response."""
        return LLMResponse(
            content="{}",
            structured_output={},
            provider="mock",
            model="mock",
        )


# === Provider Detection ===

def get_llm_service(provider: Optional[str] = None) -> LLMService:
    """
    Factory function to get the configured LLM service.
    
    Reads provider from env or argument and returns appropriate implementation.
    
    Args:
        provider: Override provider (default: from LLM_PROVIDER env var)
        
    Returns:
        LLMService implementation
    """
    provider = provider or os.getenv("LLM_PROVIDER", "mock")
    provider = provider.lower()
    
    logger.info(f"Getting LLM service for provider: {provider}")
    
    if provider == "openrouter":
        from backend.services.llm.openrouter import OpenRouterLLMService
        return OpenRouterLLMService()
    
    elif provider == "mock":
        return MockLLMService()
    
    else:
        logger.warning(f"Unknown LLM provider '{provider}', using mock")
        return MockLLMService()


def is_shadow_mode() -> bool:
    """
    Check if shadow mode is enabled.
    
    Shadow mode:
    - Enables real LLM calls for TriageAgent
    - Prevents downstream agents from executing
    - For testing/observation only
    """
    return os.getenv("SHADOW_MODE", "false").lower() in ("true", "1", "yes")
