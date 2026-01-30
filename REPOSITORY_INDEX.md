# AI Operations Copilot — Repository Index

**Project Status:** Production-Ready Core | UI Deferred  
**Last Updated:** January 30, 2026

---

## Quick Navigation

### 📋 Project Overview
- **[README.md](README.md)** — Start here: Purpose, architecture, quick start
- **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** — Project philosophy and scope
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** — Current state, frozen scope, timeline
- **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** — TODOs categorized by priority

### 📚 Technical Documentation (in `/docs/`)
- **[architecture.md](docs/architecture.md)** — System architecture details
- **[agents.md](docs/agents.md)** — Agent responsibilities and contracts
- **[data_flow.md](docs/data_flow.md)** — Data flow through workflow
- **[system_overview.md](docs/system_overview.md)** — High-level system overview

### 🔬 Engineering Documentation (Brain Artifacts)
These documents are stored in the conversation artifact directory and linked from README:
- **audit_report.md** — System audit with PASS/WARNING/FAIL ratings
- **case_study.md** — Technical deep-dive for senior engineers
- **evaluation_framework.md** — Operational metrics without labels
- **rag_safety_review.md** — RAG boundaries and safety checklist
- **hitl_model.md** — Human-in-the-loop interaction model
- **project_freeze.md** — Scope freeze declaration

### 📝 Development History
- **[progress.txt](progress.txt)** — Session-by-session development log
- **[CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md)** — Codebase architecture guide

---

## Repository Structure

```
/agents                 AI agent implementations
  /triage                  TriageAgent v1.0 (production-ready)
    schema.py                Pydantic output schema
    prompts.py               System and user prompts
    __init__.py              Agent implementation
  /knowledge               KnowledgeAgent (RAG retrieval)
  /decision                DecisionAgent (recommendation)
  /action                  ActionAgent (response drafting)
  /monitoring              MonitoringAgent (metrics collection)
  base.py                  BaseAgent abstract class

/backend                FastAPI REST API
  /api                     Endpoints and routers
    /routes                  health, tickets, agents routes
    main.py                  FastAPI app initialization
  /core                    Configuration and exceptions
  /schemas                 Pydantic request/response models
  /services                External service integrations
    /llm                     LLM service abstraction
      openrouter.py            OpenRouter implementation
    /rag                     RAG pipeline components
      ingestion.py             Document ingestion
      chunking.py              Text chunking
      embeddings.py            Embedding generation
      retrieval.py             Vector search
      store.py                 Vector store interface

/orchestration          LangGraph workflow
  /langgraph               State machine implementation
    state.py                 TicketProcessingState schema
    nodes.py                 Node implementations (8 nodes)
    edges.py                 Routing logic
    workflow.py              Workflow builder and runner

/data                   Data storage
  /tickets                 Ticket files (raw + normalized JSON)
  /documents               Knowledge base documents
    /api_docs               API documentation
    /internal               Internal docs (runbooks, playbooks)
    /runbooks               Troubleshooting guides
  /logs                    Operational logs

/tests                  Tests and test utilities
  /unit                    Unit tests (skeletons)
  /integration             Integration tests (skeletons)
  /mocks                   Mock services (LLM, RAG)
  /fixtures                Test tickets
  dry_run_workflow.py      Full workflow dry run
  shadow_run_triage.py     TriageAgent with real LLM

/evaluation             Quality evaluation framework
  /quality                 Calibration, thresholds, regression
  /datasets                Labeled data (empty, for future)
  /runners                 Evaluation runners
  /reports                 Report generation

/observability          Observability infrastructure
  metrics.py               Metrics collection (skeleton)
  tracing.py               Distributed tracing (skeleton)

/docs                   Technical documentation
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Local environment variables (DO NOT COMMIT) |
| `.env.example` | Example configuration with all options |
| `.gitignore` | Git ignore rules |
| `requirements.txt` | Python dependencies (if exists) |

---

## Key Files to Review

For senior engineering review, focus on these files:

### Core Implementation (Production-Ready)
1. **`agents/triage/schema.py`** (290 lines) — TriageAgent v1.0 schema
2. **`agents/triage/prompts.py`** (174 lines) — Production prompts
3. **`agents/triage/__init__.py`** (311 lines) — TriageAgent implementation
4. **`orchestration/langgraph/workflow.py`** (343 lines) — Workflow orchestration
5. **`orchestration/langgraph/nodes.py`** (400 lines) — Node implementations
6. **`backend/services/llm/openrouter.py`** (84 lines) — LLM integration

### Documentation (Start Here)
1. **`README.md`** — Project overview and quick start
2. **`PROJECT_STATUS.md`** — Current state and frozen scope
3. **`KNOWN_LIMITATIONS.md`** — TODOs and limitations
4. **Brain artifacts** (linked in README) — Engineering documentation suite

### Test Validation
1. **`tests/dry_run_workflow.py`** — End-to-end workflow validation
2. **`tests/fixtures/incident_ticket.json`** — P1 escalation test case

**Total review time:** 15-20 minutes for core understanding

---

## Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with OPENROUTER_API_KEY

# Test
python tests/dry_run_workflow.py           # Full workflow, mock LLM
python tests/shadow_run_triage.py          # TriageAgent, real LLM

# Run API
uvicorn backend.api.main:app --reload      # Development
uvicorn backend.api.main:app --port 8000   # Production
```

---

## Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| TriageAgent | ✅ Production | v1.0 frozen |
| KnowledgeAgent | ✅ Production | RAG pipeline complete |
| DecisionAgent | ✅ Production | Recommendation logic complete |
| ActionAgent | ✅ Production | Safety gate enforced |
| Workflow | ✅ Production | 8 nodes, checkpointing enabled |
| LLM Integration | ✅ Production | OpenRouter configured |
| Evaluation Framework | ✅ Documented | Awaiting labeled data |
| Operator Dashboard | ⏸️ Deferred | API exists, UI pending |
| Shadow Mode | ⚠️ Needs Fix | Flag exists, not enforced (1h fix) |

**Overall:** Production-ready core with 4 critical fixes needed (6 hours total)

---

## Next Actions

1. **Immediate:** Fix 4 critical issues in KNOWN_LIMITATIONS.md
2. **Week 1:** Deploy with 100% human review enabled
3. **Weeks 2-4:** Collect 500+ labeled tickets
4. **Month 2:** Analyze metrics, tune thresholds
5. **Month 3+:** Consider selective automation

**Project is in maintenance mode. No new features without v2 planning.**
