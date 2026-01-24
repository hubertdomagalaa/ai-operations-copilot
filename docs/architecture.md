# Architecture

This document describes the technical architecture of the AI Operations Copilot.

## Component Overview

### Backend (`/backend`)

FastAPI-based REST API serving as the system's entry point.

| Directory | Purpose |
|-----------|---------|
| `api/` | FastAPI routers and endpoints |
| `core/` | Configuration, exceptions, logging |
| `schemas/` | Pydantic models for validation |
| `services/` | External service integrations |

Key files:
- `api/main.py` — FastAPI application instance
- `api/routes/tickets.py` — Ticket CRUD endpoints
- `api/routes/agents.py` — Agent workflow endpoints
- `core/config.py` — Environment configuration
- `services/llm.py` — LLM provider abstraction
- `services/vector_store.py` — RAG vector database

### Agents (`/agents`)

AI agents implementing specific capabilities.

| Agent | Responsibility |
|-------|----------------|
| Triage | Classify and prioritize tickets |
| Knowledge | Retrieve relevant documentation via RAG |
| Decision | Recommend actions based on context |
| Action | Draft responses and execute actions |
| Monitoring | Track system health and performance |

All agents inherit from `BaseAgent` and implement a standard interface.

### Orchestration (`/orchestration`)

LangGraph-based workflow management.

| File | Purpose |
|------|---------|
| `state.py` | TypedDict workflow state definition |
| `nodes.py` | Workflow node implementations |
| `edges.py` | Conditional routing logic |
| `workflow.py` | Graph construction and execution |

### Observability (`/observability`)

Monitoring and debugging infrastructure.

- **Tracing**: Distributed tracing for workflow debugging
- **Metrics**: Performance and quality metrics

### Evaluation (`/evaluation`)

AI quality evaluation framework.

- **Evaluators**: Classification, retrieval, and response quality

## Data Flow

See `data_flow.md` for detailed workflow description.

## Technology Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Agent Orchestration | LangGraph |
| LLM Integration | LangChain |
| Vector Store | TBD (Chroma, Pinecone, etc.) |
| Testing | pytest |
| Observability | OpenTelemetry compatible |

## Design Decisions

### Why LangGraph?

- Native support for stateful workflows
- Built-in checkpointing for human-in-the-loop
- Clear separation of nodes and edges
- Easy to visualize and debug

### Why Separate Agents?

- Single responsibility principle
- Easier to test and improve individually
- Clear boundaries for prompt engineering
- Independent scaling if needed

### Why TypedDict for State?

- Type safety in workflow nodes
- Clear contract between components
- IDE support for development
- LangGraph native support

## Security Considerations

- API keys stored in environment variables
- No customer PII in logs
- Audit trail for all AI decisions
- Human approval for sensitive actions

## Extensibility Points

The system is designed for extension:

1. **New Agents**: Add to `/agents`, register in workflow
2. **New Endpoints**: Add routers to `/backend/api/routes`
3. **New Metrics**: Add to `/observability/metrics.py`
4. **New Evaluators**: Add to `/evaluation/evaluators.py`
