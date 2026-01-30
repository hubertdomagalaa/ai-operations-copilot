# AI Operations Copilot

**Status:** Production-Ready Core | UI Pending  
**Version:** 1.0  
**Date:** January 2026

An internal AI system that assists human operators in processing support tickets for a B2B SaaS company. This system provides intelligent triage, knowledge retrieval, and action recommendations while maintaining mandatory human-in-the-loop oversight.

---

## Problem This System Solves

Support teams face thousands of tickets with varying urgency, technical complexity, and documentation needs. Manual triage is slow, inconsistent, and error-prone. Fully autonomous AI systems are unsafe for production use.

This system provides the middle ground: **AI-assisted decision-making with human oversight**.

---

## What This System Does

1. **Classifies** incoming tickets by category, severity, and technical signals
2. **Retrieves** relevant internal documentation using RAG (Retrieval-Augmented Generation)
3. **Recommends** actions with supporting evidence and confidence scores
4. **Drafts** responses or action checklists for human approval
5. **Escalates** automatically when confidence is low or risk is high

**Human review is mandatory.** The system proposes; humans decide.

---

## What This System Does NOT Do

- ❌ **No auto-execution** — Every action requires human approval
- ❌ **No customer-facing AI** — This is an internal operator tool
- ❌ **No fine-tuning** — Uses prompt engineering + off-the-shelf LLMs
- ❌ **No external integrations** — Ingests normalized JSON, outputs recommendations
- ❌ **No SLA prediction** — Classifies urgency but doesn't estimate resolution time
- ❌ **No multi-ticket analysis** — Each ticket processed independently

See [project_freeze.md](../brain-docs/project_freeze.md) for full scope boundaries.

---

## Architecture Overview

### Multi-Agent State Machine

```
Ticket JSON → TriageAgent → KnowledgeAgent → DecisionAgent → ActionAgent
                    ↓              ↓              ↓              ↓
                Escalation?    RAG Retrieval   Recommend     Draft Response
                    ↓              ↓              ↓              ↓
                Human Review ←───────────────────┴──────────────┘
```

**Orchestration:** LangGraph state machine with checkpointing  
**Agents:** 5 specialized agents with explicit contracts (Pydantic schemas)  
**Storage:** File-based (tickets, documents, logs)  
**LLM Provider:** OpenRouter (configurable via env vars)

### Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **TriageAgent** | Classify tickets (category, severity, confidence) | ✅ Production |
| **KnowledgeAgent** | Retrieve docs via RAG, attach citations | ✅ Production |
| **DecisionAgent** | Recommend actions with evidence | ✅ Production |
| **ActionAgent** | Draft responses (requires approval) | ✅ Production |
| **MonitoringAgent** | Log metrics for evaluation | ✅ Production |
| **LangGraph Workflow** | Orchestrate agents, manage state | ✅ Production |
| **RAG Pipeline** | Index docs, embed, retrieve, rank | ✅ Production |
| **Evaluation Framework** | Measure quality without labels | ✅ Documented |
| **Operator Dashboard** | Human approval UI | ⏸️ Deferred |

---

## Safety Philosophy

### 1. Conservative Classification

"If uncertain, escalate." The system optimizes for **zero false negatives** on critical tickets (P1 severity, security issues, data loss).

**Trade-off:** Higher escalation rate (20-40%) but no silent failures.

### 2. Human-in-the-Loop is Mandatory

No action executes without explicit `human_decision.action = "approve"`. This is enforced in code, not configuration.

### 3. Confidence is Explicit

Every classification includes confidence score (0.0-1.0) based on:
- Category clarity
- Symptom specificity
- Technical detail level

Low confidence (<0.7) triggers automatic escalation.

### 4. Post-LLM Safety Nets

Keyword-based escalation rules run after LLM classification as a safety layer. Example:
- Ticket contains "data loss" → escalate
- Ticket contains "outage" → escalate
- Severity P1 → escalate

### 5. Failures Escalate, Not Crash

JSON parse errors, RAG timeouts, LLM failures → all trigger escalation with error context. No silent ticket drops.

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenRouter API key (or other LLM provider)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd AiEngineer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Configuration

Create `.env` file (do not commit):

```bash
# LLM Provider
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.2

# Shadow Mode (optional)
SHADOW_MODE=false
```

### Running Shadow Mode

Shadow mode enables real LLM calls for testing without downstream execution:

```bash
# 1. Enable shadow mode
echo "SHADOW_MODE=true" >> .env

# 2. Run triage-only test
python tests/shadow_run_triage.py

# 3. Review outputs
cat data/logs/*.jsonl
```

Shadow mode stops workflow after TriageAgent, allowing you to:
- Test prompt changes safely
- Collect confidence calibration data
- Compare prompt versions

### Running Full Workflow (Dry Run)

```bash
# Uses mock LLM, no API calls
python tests/dry_run_workflow.py

# Run specific scenario
python tests/dry_run_workflow.py --scenario clean

# Simulate human approval
python tests/dry_run_workflow.py --auto-approve
```

### Running API Server

```bash
# Development mode
uvicorn backend.api.main:app --reload

# Production mode
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

---

## Project Structure

```
/agents             AI agents (triage, knowledge, decision, action, monitoring)
  /triage              TriageAgent v1.0 (schema.py, prompts.py, __init__.py)
  /knowledge           KnowledgeAgent (RAG retrieval only)
  /decision            DecisionAgent (recommendation synthesis)
  /action              ActionAgent (response drafting)
  /monitoring          MonitoringAgent (metrics collection)

/backend            FastAPI REST API
  /api                 Endpoints (/tickets, /agents, /health)
  /services            LLM service, RAG pipeline, vector store

/orchestration      LangGraph workflow
  /langgraph           State machine (state.py, nodes.py, edges.py, workflow.py)

/data
  /tickets             Ticket storage (raw + normalized JSON)
  /documents           Knowledge base (API docs, runbooks, internal docs)
  /logs                Operational logs (evaluation, metrics)

/tests              Unit, integration, dry run scripts
  /mocks               Mock LLM service for testing
  /fixtures            Test tickets (clean, ambiguous, incident)

/evaluation         Quality evaluation framework
  /quality             Calibration, thresholds, regression detection
  /datasets            Labeled data (not yet collected)

/observability      Metrics and tracing (skeleton)

/docs               System documentation (architecture, agents, data flow)
```

---

## Documentation

### Engineering Documentation (in `/brain-docs/`)

📄 **[audit_report.md](../brain-docs/audit_report.md)** — System audit with PASS/WARNING/FAIL ratings  
📄 **[case_study.md](../brain-docs/case_study.md)** — Technical deep-dive for senior engineers  
📄 **[evaluation_framework.md](../brain-docs/evaluation_framework.md)** — Metrics without ML training data  
📄 **[rag_safety_review.md](../brain-docs/rag_safety_review.md)** — RAG boundaries and safety checklist  
📄 **[hitl_model.md](../brain-docs/hitl_model.md)** — Human-in-the-loop interaction model  
📄 **[project_freeze.md](../brain-docs/project_freeze.md)** — Scope freeze and v2 conditions

### Project Documentation (in `/`)

📄 **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** — Project purpose and philosophy  
📄 **[CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md)** — Architecture and module descriptions  
📄 **[progress.txt](progress.txt)** — Development history and session logs

### Technical Documentation (in `/docs/`)

📄 **[architecture.md](docs/architecture.md)** — System architecture  
📄 **[agents.md](docs/agents.md)** — Agent responsibilities  
📄 **[data_flow.md](docs/data_flow.md)** — Data flow through workflow

---

## Current Status: Production-Ready Core

### ✅ Complete and Production-Ready

- **TriageAgent v1.0** — Schema, prompts, escalation logic finalized
- **LangGraph Workflow** — 8 nodes, conditional routing, checkpointing
- **RAG Pipeline** — Ingestion, chunking, embeddings, retrieval
- **Safety Mechanisms** — Post-LLM escalation, failure containment
- **Evaluation Framework** — 4 core metrics defined
- **Documentation Suite** — 6 engineering docs covering all aspects

### ⏸️ Deferred (Not Blocking Production)

- **Operator Dashboard (UI)** — Human approval interface (functional API exists)
- **Notification Service** — Alert operators to review queue
- **Labeled Datasets** — Evaluation requires 500+ labeled tickets
- **Confidence Calibration** — Empirical tuning of confidence thresholds
- **External Integrations** — Direct Zendesk/Jira API integration

### 🚧 Known Limitations

1. **Shadow mode not implemented** — Flag exists but not enforced in workflow
2. **Resume workflow API broken** — Uses non-existent `aget_state()` method
3. **OpenRouter JSON parsing fragile** — No markdown fence handling
4. **RAG query unbounded** — No length/count limits on retrieval queries

See [audit_report.md](../brain-docs/audit_report.md) for full details.

---

## Ship Decision

**Status:** READY WITH NOTES

The system can ship **with human-in-the-loop enabled for all tickets** while the 4 known limitations are addressed. Timeline to fully production-ready: 1-2 days of targeted fixes.

### Recommended Deployment Strategy

1. **Week 1:** Deploy with 100% human review (shadow mode off)
2. **Week 2-4:** Collect 500+ tickets with human decisions
3. **Month 2:** Analyze metrics, tune thresholds
4. **Month 3:** Enable selective automation for low-risk categories

---

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Dry run (full workflow, mock LLM)
python tests/dry_run_workflow.py

# Shadow run (TriageAgent only, real LLM)
python tests/shadow_run_triage.py
```

### Code Quality

- Type hints: 95%+ coverage
- Pydantic validation: All agent I/O
- Error handling: Explicit escalation paths
- Logging: Structured JSON logs

### Adding a New Agent

See `/agents/base.py` for `BaseAgent` interface. All agents must implement:
- `process(state: Dict[str, Any]) -> Dict[str, Any]`
- Return `{"success": bool, "confidence": float, "result": {...}}`

---

## License

Internal use only.

---

## Acknowledgments

This system represents 11 development sessions focused on production engineering principles:
- Conservative classification over false confidence
- Human oversight over automation
- Explicit reasoning over black-box decisions
- Graceful degradation over silent failures

Designed for long-term maintainability, not short-term demos.
