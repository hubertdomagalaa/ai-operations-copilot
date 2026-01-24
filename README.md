# AI Operations Copilot

An internal AI system that assists human operators in processing support tickets for a B2B SaaS REST API product.

## Overview

This system:
- **Classifies** incoming tickets by category and priority
- **Retrieves** relevant internal documentation via RAG
- **Recommends** actions with supporting evidence
- **Drafts** responses for human review
- **Learns** from operator feedback

Human-in-the-loop is mandatory — AI assists decisions but does not act autonomously.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the API (development)
uvicorn backend.api.main:app --reload

# Run tests
pytest tests/
```

## Project Structure

```
/backend        # FastAPI REST API
  /api          # Endpoints and routers
  /core         # Config, exceptions, logging
  /schemas      # Pydantic models
  /services     # External service integrations

/agents         # AI agents
  /triage       # Ticket classification
  /knowledge    # RAG retrieval
  /decision     # Action recommendation
  /action       # Response drafting
  /monitoring   # System health

/orchestration  # LangGraph workflow
  /langgraph    # State, nodes, edges, workflow

/data           # Data directories
  /tickets      # Ticket storage
  /documents    # RAG documents
  /logs         # Operational logs

/observability  # Tracing and metrics
/evaluation     # AI quality evaluation
/tests          # Unit and integration tests
/docs           # Documentation
```

## Documentation

- [System Overview](docs/system_overview.md)
- [Architecture](docs/architecture.md)
- [Agents](docs/agents.md)
- [Data Flow](docs/data_flow.md)

## Current Status

This is a **skeleton repository**. Core structure and interfaces are defined, but business logic is not yet implemented. See `progress.txt` for current state and next steps.

## Development

See `PROJECT_CONTEXT.md` for detailed project context and development principles.

## License

Internal use only.
