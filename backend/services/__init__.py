"""
Services Package
================

External service integrations and adapters.

WHY THIS PACKAGE EXISTS:
- Abstracts external dependencies behind interfaces
- Enables testing with mock implementations
- Centralizes integration configuration

Services:
- llm.py — LLM provider abstraction (OpenAI, Anthropic, etc.)
- vector_store.py — Vector database for RAG
- storage.py — Ticket and document persistence
- notification.py — Alerting and notifications
"""
