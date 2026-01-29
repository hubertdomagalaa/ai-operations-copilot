# AiEngineer — Codebase Overview & Architecture

## Executive Summary

AiEngineer is a modular, production-grade multi-agent system for intelligent ticket processing and automation. It leverages human-in-the-loop workflows, retrieval-augmented generation (RAG), and orchestrated agent pipelines. The system is designed for extensibility, observability, and robust integration with internal APIs and documentation.

---

## 1. High-Level Architecture

```
┌───────────────┐
│   FastAPI     │  ← REST API: /tickets, /agents, /health
└──────┬────────┘
       │
┌──────▼────────┐
│ Orchestration │  ← LangGraph: state machine workflow
└──────┬────────┘
       │
┌──────▼────────┐
│   Agents      │  ← Triage, Knowledge, Decision, Action, Monitoring
└──────┬────────┘
       │
┌──────▼────────┐
│   RAG Layer   │  ← Document retrieval, embeddings, vector store
└──────┬────────┘
       │
┌──────▼────────┐
│   Data/Logs   │  ← Tickets, documents, logs
└───────────────┘
```

---

## 2. Main Modules & Components

### `/backend` — FastAPI REST API
- **api/**: Endpoints and routers (`main.py`, `routes/`)
- **core/**: Config, exceptions, logging
- **schemas/**: Pydantic models for validation
- **services/**: Integrations (LLM, RAG, vector store)

### `/agents` — AI Agents
- **triage/**: Ticket classification
- **knowledge/**: RAG retrieval
- **decision/**: Action recommendation
- **action/**: Response drafting
- **monitoring/**: System health
- All agents inherit from `BaseAgent` and follow a single-responsibility principle.

### `/orchestration/langgraph` — Workflow Engine
- **state.py**: TypedDict workflow state
- **nodes.py**: Workflow node implementations
- **edges.py**: Routing logic
- **workflow.py**: Graph construction and execution

### `/data`
- **documents/**: RAG source docs (API docs, runbooks, internal knowledge)
- **tickets/**: Ticket storage (raw/normalized)
- **logs/**: Operational logs (structured JSON)

### `/observability`
- Tracing and metrics (OpenTelemetry compatible)

### `/evaluation`
- AI quality evaluation (classification, retrieval, response quality, regression detection)

### `/tests`
- Unit, integration, and dry-run tests (pytest-based)

### `/docs`
- System, architecture, and workflow documentation

---

## 3. Key Workflows & Data Flow

- **Entry Point**: All requests enter via FastAPI endpoints (`/backend/api/main.py`).
- **Workflow Orchestration**: LangGraph state machine routes tickets through agent nodes.
- **Agent Processing**: Each agent (triage, knowledge, decision, action, monitoring) performs a focused task, passing state forward.
- **RAG Pipeline**: Knowledge agent retrieves context from internal docs using chunking, embeddings, and vector search.
- **Human-in-the-Loop**: Low-confidence or high-risk cases are routed for human review.
- **Observability**: All actions, decisions, and metrics are logged for traceability.

---

## 4. API & Integrations

- **API Endpoints**: `/tickets`, `/agents`, `/health` (internal use only)
- **External Integrations**: LLM providers (OpenAI, local TF-IDF), vector stores (in-memory, Pinecone/Chroma-ready)
- **Security**: API keys in env vars, PII encrypted at rest, audit logs, SOC 2/GDPR compliance

---

## 5. Testing & Evaluation

- **Unit Tests**: Core logic, agent behaviors
- **Integration Tests**: API endpoints, end-to-end workflows, service integrations
- **Evaluation**: Quality signals, calibration, regression detection (infrastructure in place)

---

## 6. Notable Files & Folders

| Path                                 | Purpose                                              |
|-------------------------------------- |------------------------------------------------------|
| backend/api/main.py                   | FastAPI app instance, API entry point                |
| backend/api/routes/tickets.py         | Ticket CRUD endpoints                                |
| backend/services/llm.py               | LLM abstraction layer                                |
| backend/services/rag/ingestion.py     | Document ingestion for RAG                           |
| agents/base.py                        | BaseAgent ABC, agent interface                       |
| orchestration/langgraph/workflow.py   | Workflow graph definition                            |
| orchestration/langgraph/state.py      | Workflow state schema                                |
| data/documents/                       | RAG source documents                                 |
| data/tickets/normalized/              | Normalized ticket data                               |
| data/logs/                            | Structured logs (JSON)                               |
| evaluation/quality/                   | Quality signal and regression infra                  |
| tests/integration/test_api.py         | API integration tests                                |
| docs/architecture.md                  | Technical architecture overview                      |
| docs/data_flow.md                     | Detailed workflow/data flow                          |

---

## 7. Critical Paths & Areas for Attention

- **LangGraph Workflow**: State machine logic in `orchestration/langgraph/` is central; errors here affect all ticket processing.
- **RAG Pipeline**: Document chunking, embedding, and retrieval logic (`backend/services/rag/`) is complex and performance-sensitive.
- **Agent Coordination**: Inter-agent state passing and confidence scoring are critical for correct workflow routing.
- **Human-in-the-Loop**: Escalation and resumption logic must be robust to avoid workflow deadlocks.
- **Security & Compliance**: API key management, PII handling, and audit logging are essential for production use.
- **Testing Coverage**: Ensure all workflow branches and integrations are covered by tests.

---

## 8. Potentially Complex or Unusual Integrations

- **Provider-agnostic Embeddings**: Swappable between local TF-IDF and OpenAI, with a common interface.
- **Pluggable Vector Store**: In-memory by default, but designed for easy replacement with external services.
- **LangGraph State Machine**: Explicit node/edge design for transparency and checkpointing.
- **Quality Evaluation**: Infrastructure for calibration and regression detection, but not yet enforcing thresholds.

---

## 9. Quick Start for New Developers

- Review `README.md`, `docs/architecture.md`, and `docs/data_flow.md`.
- Explore `/backend/api/main.py` for API entry points.
- Study `/orchestration/langgraph/workflow.py` for workflow logic.
- Check `/agents/` for agent implementations and responsibilities.
- Use `/tests/` to understand test coverage and run pytest for validation.

---

## 10. References

- [System Overview](docs/system_overview.md)
- [Architecture](docs/architecture.md)
- [Agents](docs/agents.md)
- [Data Flow](docs/data_flow.md)
- [System Architecture Report](docs/SYSTEM_ARCHITECTURE_REPORT.md)

---

**Areas requiring special attention:**  
- Workflow state transitions and error handling  
- RAG pipeline performance and accuracy  
- Security of API keys and sensitive data  
- Human-in-the-loop escalation/resumption  
- Observability and logging completeness

---

*This summary is intended as a living document for onboarding and architectural reference. For detailed implementation, consult the referenced documentation and code modules.*
