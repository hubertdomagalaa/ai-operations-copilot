"""
Application Configuration
=========================

Centralized configuration management using Pydantic Settings.

WHY THIS FILE EXISTS:
- Single source of truth for all configuration
- Environment variable parsing with validation
- Secrets management through environment variables

USAGE:
    from backend.core.config import settings
    
    db_url = settings.database_url
    llm_api_key = settings.llm_api_key

DESIGN DECISIONS:
- All secrets loaded from environment variables
- Sensible defaults for development
- Validation at startup to fail fast
"""

from typing import Optional

# TODO: Uncomment when pydantic is installed
# from pydantic_settings import BaseSettings


# TODO: Replace with actual Pydantic Settings class
class Settings:
    """
    Application settings loaded from environment variables.
    
    TODO: Convert to Pydantic BaseSettings for validation
    """
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Database Configuration
    # TODO: Define actual database connection settings
    database_url: Optional[str] = None
    
    # Vector Store Configuration (RAG)
    # TODO: Define vector store connection settings
    vector_store_url: Optional[str] = None
    
    # LLM Configuration
    # TODO: Define LLM provider settings
    llm_provider: str = "openai"  # or "anthropic", "local", etc.
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    
    # Observability
    # TODO: Define observability settings
    enable_tracing: bool = True
    log_level: str = "INFO"


# Global settings instance
settings = Settings()
