# AI Operations Copilot — System Architecture Report

> A production-grade AI system for intelligent ticket processing with human-in-the-loop workflows.
> 
> **Author:** Hubert Domagała | **Last Updated:** January 2026

---

## Executive Summary

The AI Operations Copilot is an internal decision-support system designed for B2B SaaS companies. It processes support tickets through a multi-agent pipeline that:

1. **Classifies** incoming tickets by type and severity
2. **Retrieves** relevant documentation via RAG (Retrieval-Augmented Generation)
3. **Recommends** actions with grounded reasoning
4. **Drafts** responses for human review
5. **Enforces** human approval before any execution

**Core Principle:** AI assists; humans decide. No autonomous execution.

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         AI OPERATIONS COPILOT                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐        ┌─────────────────────────────────────────────┐   │
│   │   FastAPI   │◄──────►│              LangGraph Workflow             │   │
│   │  REST API   │        │                                             │   │
│   └─────────────┘        │  ┌────────┐   ┌───────────┐   ┌──────────┐  │   │
│                          │  │ TRIAGE │──►│ KNOWLEDGE │──►│ DECISION │  │   │
│   ┌─────────────┐        │  └────────┘   └───────────┘   └────┬─────┘  │   │
│   │   Vector    │◄───────│                                    │        │   │
│   │    Store    │        │              ┌─────────────────────▼──────┐ │   │
│   └─────────────┘        │              │      HUMAN REVIEW          │ │   │
│                          │              │      (checkpoint)          │ │   │
│   ┌─────────────┐        │              └─────────────────────┬──────┘ │   │
│   │  Documents  │        │                                    │        │   │
│   │  (/data)    │        │              ┌─────────────────────▼──────┐ │   │
│   └─────────────┘        │              │        ACTION              │ │   │
│                          │              │    (draft only)            │ │   │
│                          │              └────────────────────────────┘ │   │
│                          └─────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestration** | LangGraph | State machine workflow with checkpointing |
| **API** | FastAPI | REST endpoints for ticket ingestion |
| **RAG** | Custom pipeline | Document retrieval with citations |
| **Embeddings** | TF-IDF (local) / OpenAI (production) | Provider-agnostic abstraction |
| **State** | TypedDict | Type-safe workflow state management |
| **Testing** | pytest | Unit and integration tests |

---

## Multi-Agent Architecture

### Overview

The system uses a **multi-agent pipeline** where each agent has a single, well-defined responsibility. Agents communicate through a shared state object and never call each other directly.

```
Ticket → TriageAgent → KnowledgeAgent → DecisionAgent → [Human] → ActionAgent → Response
```

### Agent Responsibilities

#### 1. TriageAgent
**Purpose:** First contact with ticket. Classification and prioritization.

| Responsibility | Details |
|---------------|---------|
| Classify ticket type | `bug`, `incident`, `question`, `task` |
| Assign severity | `low`, `medium`, `high`, `critical` |
| Extract keywords | For RAG query formulation |
| Detect escalation | Keywords like "outage", "security", "data loss" |

**Output Schema:**
```python
{
    "ticket_type": "bug",
    "severity": "medium", 
    "confidence": 0.85,
    "keywords": ["authentication", "401", "API"],
    "requires_escalation": False
}
```

**Human Review Triggers:**
- Confidence < 0.7
- Critical keywords detected
- Ambiguous classification

---

#### 2. KnowledgeAgent
**Purpose:** Retrieve relevant documentation via RAG. No summarization, no decisions.

| Responsibility | Details |
|---------------|---------|
| Query RAG pipeline | Using ticket content + triage keywords |
| Return citations | Full traceability to source documents |
| Calculate confidence | Based on retrieval quality |
| Flag low relevance | Trigger human review if no docs found |

**Core Principle:** `No retrieval = no answer`

**Output Schema:**
```python
{
    "documents": [...],
    "document_count": 3,
    "context": "--- Document 1 [auth.md] ---\n...",
    "confidence": 0.72,
    "sources": ["authentication.md", "troubleshooting.md"]
}
```

**Human Review Triggers:**
- No relevant documents found
- Low retrieval confidence < 0.3

---

#### 3. DecisionAgent
**Purpose:** Synthesize signals from Triage + Knowledge. Recommend action. NEVER execute.

| Responsibility | Details |
|---------------|---------|
| Combine upstream signals | Triage confidence + retrieval quality |
| Identify risk flags | Low confidence, missing docs, high severity |
| Recommend action | `auto_respond`, `escalate`, `manual_review` |
| Require human approval | Always True (safety first) |

**Decision Logic:**
```
IF severity in [critical, high] → escalate
IF no documents retrieved → manual_review
IF risk_flags >= 2 → manual_review
IF confidence >= 0.7 AND docs found → auto_respond candidate
ELSE → manual_review
```

**Output Schema:**
```python
{
    "recommended_action": "auto_respond",
    "reasoning_summary": "Medium question. Found 3 relevant documents...",
    "confidence": 0.65,
    "risk_flags": ["low_triage_confidence"],
    "requires_human_approval": True,
    "sources_used": ["authentication.md"]
}
```

**Guarantee:** `requires_human_approval` is **always True** in current implementation.

---

#### 4. ActionAgent
**Purpose:** Prepare drafts ONLY after human approval. Never executes external calls.

| Responsibility | Details |
|---------------|---------|
| Validate approval | RuntimeError if approval missing |
| Generate draft response | Polite, factual, non-committal |
| Generate engineer checklist | Step-by-step, actionable |
| Cite sources | All content grounded in retrieved docs |

**Precondition Check:**
```python
def _is_approved(self, state):
    human_decision = state.get("human_decision") or {}
    if human_decision.get("action") == "approve":
        return True
    return False  # Raises RuntimeError
```

**Output Schema:**
```python
{
    "action_type": "draft_response",
    "content": "Thank you for contacting support...\n[DRAFT]",
    "grounding_sources": ["authentication.md"],
    "confidence": 0.75,
    "disclaimers": ["No specific runbook found"],
    "is_draft": True
}
```

**Guarantee:** All outputs marked as `is_draft: True` requiring human review.

---

## LangGraph Workflow

### State Machine Design

The workflow is a **compiled state machine** with explicit nodes and conditional edges:

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     TRIAGE      │ → classify ticket
                    └────────┬────────┘
                             │
               [route_after_triage]
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         "escalate"     "knowledge"      "error"
              │              │              │
              │     ┌────────▼────────┐     │
              │     │    KNOWLEDGE    │     │
              │     └────────┬────────┘     │
              │              │              │
              │     ┌────────▼────────┐     │
              │     │    DECISION     │     │
              │     └────────┬────────┘     │
              │              │              │
              │    [route_after_decision]   │
              │              │              │
              │    ┌─────────┴─────────┐    │
              │    │                   │    │
              │ "action"        "human_review"
              │    │                   │    │
              │    │        ┌──────────▼────────┐
              │    │        │   HUMAN_REVIEW    │ ← CHECKPOINT
              │    │        │ (paused_for_human)│
              │    │        └──────────┬────────┘
              │    │                   │
              │    │      [route_after_human]
              │    │                   │
              │    │    ┌──────────────┼──────────────┐
              │    │    │              │              │
              │    │ "action"     "complete"      "cancel"
              │    │    │              │              │
              │    │    ▼              │              ▼
              │    └──►ACTION ─────────┼─────────► END
              │           │            │
              │    ┌──────▼──────┐     │
              │    │  MONITORING │     │
              │    └──────┬──────┘     │
              │           │            │
              │    ┌──────▼──────┐     │
              └───►│  COMPLETE   │◄────┘
                   └──────┬──────┘
                          │
                        [END]
```

### Workflow State

The `TicketProcessingState` is a TypedDict that flows through all nodes:

```python
class TicketProcessingState(TypedDict):
    # Immutable (set at start)
    ticket_id: str
    ticket_data: Dict[str, Any]
    trace_id: str
    started_at: str
    
    # Processing
    status: str  # "pending", "running", "paused_for_human", "completed", "failed"
    current_step: str
    
    # Agent outputs
    triage_output: Optional[Dict]
    knowledge_output: Optional[Dict]
    decision_output: Optional[Dict]
    action_output: Optional[Dict]
    
    # RAG results
    retrieved_documents: Optional[List[Dict]]
    
    # Human-in-the-loop
    human_decision_required: bool
    human_decision: Optional[Dict]  # {"action": "approve"} or {"action": "cancel"}
    human_approval_status: Optional[str]  # "approved", "rejected", "modified"
```

### Checkpointing

LangGraph's `MemorySaver` enables:
- **Pause** at human_review_node (status = "paused_for_human")
- **Resume** via `resume_workflow()` API after human provides decision
- **Recovery** from failures with checkpoint state

---

## RAG Pipeline

### Architecture

```
Documents → Ingestion → Chunking → Embedding → Storage → Retrieval → Citations
   │            │           │          │          │           │
   ▼            ▼           ▼          ▼          ▼           ▼
/data/      Load +     512 chars   TF-IDF    In-memory    Cosine
documents   metadata    64 overlap  vectors   store       similarity
```

### Components

#### Document Ingestion (`ingestion.py`)
- Loads `.md` and `.txt` files from `/data/documents`
- Preserves metadata: filename, path, document type
- Supports multiple document categories: `api_docs/`, `runbooks/`

#### Chunking (`chunking.py`)
- **Chunk size:** 512 characters
- **Overlap:** 64 characters
- **Rationale:** Balances precision with context sufficiency

#### Embeddings (`embeddings.py`)
- **Provider-agnostic interface** via `EmbeddingService` ABC
- **Local:** TF-IDF vectorizer (no external dependencies)
- **Production:** OpenAI embeddings (stub ready)

#### Vector Store (`store.py`)
- **In-memory implementation** for development
- **Cosine similarity** search
- **Replaceable** with Pinecone, Chroma, etc.

#### Retrieval (`retrieval.py`)
- **RAGPipeline** orchestrates full flow
- **Citation tracking** via `RetrievalResult` dataclass
- **Multi-query retrieval** from ticket content + keywords

### Example Retrieval

```python
from backend.services.rag import RAGPipeline

pipeline = RAGPipeline()
await pipeline.ingest_documents()

results = await pipeline.retrieve_for_ticket(
    ticket_data={"subject": "401 error on login", "body": "..."},
    triage_output={"result": {"keywords": ["authentication", "401"]}},
    k=5
)

for r in results:
    print(f"{r.to_citation()}: {r.content[:50]}...")
# [authentication.md] (chunk 2, score: 0.87): ## 401 Unauthorized...
```

---

## Human-in-the-Loop Enforcement

### Why It Matters

This system is designed for **decision support**, not **decision making**. Every action requires explicit human approval because:

1. **Safety:** AI can be confidently wrong
2. **Accountability:** Humans own the decision
3. **Trust:** Operators must validate AI recommendations
4. **Compliance:** Audit trail for all decisions

### Implementation

#### 1. DecisionAgent Always Requires Approval
```python
def _requires_human_approval(self, ...) -> bool:
    # SAFETY: Even if all checks pass, we still require approval
    # This is a human-in-the-loop system by design
    return True
```

#### 2. Human Review Node Pauses Workflow
```python
async def human_review_node(state):
    state["status"] = "paused_for_human"
    # Workflow stops here until human provides decision
    return state
```

#### 3. ActionAgent Validates Approval
```python
async def process(self, state):
    if not self._is_approved(state):
        raise RuntimeError(
            "ActionAgent cannot run without human approval."
        )
```

#### 4. Resume After Approval
```python
result = await resume_workflow(
    ticket_id="ticket-123",
    human_decision={"action": "approve"}
)
```

### Approval Flow

```
1. Workflow reaches HUMAN_REVIEW node
2. Status set to "paused_for_human"
3. Operator reviews:
   - Ticket content
   - Triage classification
   - Retrieved documents (with citations)
   - AI recommendation with reasoning
   - Risk flags
4. Operator decides:
   - "approve" → ActionAgent runs
   - "modify" → ActionAgent uses modified recommendation
   - "manual" → Operator handles directly
   - "cancel" → Workflow ends
5. Workflow resumes via API
```

---

## Project Structure

```
/ai-operations-copilot
├── agents/                      # Multi-agent system
│   ├── base.py                  # BaseAgent ABC
│   ├── triage/                  # Ticket classification
│   ├── knowledge/               # RAG retrieval (implemented)
│   ├── decision/                # Recommendation logic (implemented)
│   ├── action/                  # Draft generation (implemented)
│   └── monitoring/              # System health
│
├── backend/                     # FastAPI application
│   ├── api/                     # REST endpoints
│   ├── core/                    # Config, logging, exceptions
│   ├── schemas/                 # Pydantic models
│   └── services/                # External services
│       ├── llm.py               # LLM abstraction
│       └── rag/                 # RAG pipeline
│           ├── ingestion.py     # Document loading
│           ├── chunking.py      # Text splitting
│           ├── embeddings.py    # Vector encoding
│           ├── store.py         # Vector storage
│           └── retrieval.py     # Search interface
│
├── orchestration/               # Workflow engine
│   └── langgraph/
│       ├── state.py             # TicketProcessingState
│       ├── nodes.py             # Workflow nodes
│       ├── edges.py             # Routing logic
│       └── workflow.py          # Graph compilation
│
├── data/                        # Data storage
│   ├── documents/               # RAG source documents
│   │   ├── api_docs/            # API documentation
│   │   └── runbooks/            # Troubleshooting guides
│   ├── tickets/                 # Ticket storage
│   └── logs/                    # Operational logs
│
├── observability/               # Tracing and metrics
├── evaluation/                  # AI quality evaluation
├── tests/                       # Test suite
└── docs/                        # Documentation
```

---

## Key Design Decisions

### 1. Separation of Concerns
Each agent has ONE responsibility:
- Triage: Classify only
- Knowledge: Retrieve only
- Decision: Recommend only
- Action: Draft only

### 2. No Autonomous Execution
The system **never** takes actions without human approval. Even high-confidence decisions require operator sign-off.

### 3. Grounded Responses
All AI outputs must cite retrieved documents. If no relevant documents are found, the system flags for human review rather than hallucinating.

### 4. Explicit Uncertainty
Every agent output includes:
- `confidence` score (0.0 - 1.0)
- `risk_flags` for decision agent
- `disclaimers` for action agent

### 5. Observable by Design
- Every workflow has a `trace_id`
- All agents log processing time
- State is checkpointed for recovery

---

## API Usage

### Start Workflow
```python
from orchestration.langgraph.workflow import run_workflow

result = await run_workflow(
    ticket_id="ticket-123",
    ticket_data={
        "subject": "API returns 401 on valid credentials",
        "body": "We're getting authentication errors...",
        "customer_id": "acme-corp",
    }
)
# result["status"] == "paused_for_human"
```

### Check Status
```python
from orchestration.langgraph.workflow import get_workflow_status

status = get_workflow_status("ticket-123")
# status["current_step"] == "human_review"
# status["decision_output"]["result"]["recommended_action"] == "auto_respond"
```

### Resume After Approval
```python
from orchestration.langgraph.workflow import resume_workflow

result = await resume_workflow(
    ticket_id="ticket-123",
    human_decision={"action": "approve"}
)
# result["status"] == "completed"
# result["action_output"]["result"]["content"] == "Draft response..."
```

---

## Current Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Repository structure | ✅ Complete | Full scaffolding |
| LangGraph workflow | ✅ Complete | 8 nodes, 3 conditional edges |
| RAG pipeline | ✅ Complete | 5 modules, local TF-IDF |
| KnowledgeAgent | ✅ Complete | Full RAG integration |
| DecisionAgent | ✅ Complete | Risk flags, human approval |
| ActionAgent | ✅ Complete | Draft generation, approval validation |
| TriageAgent | 🔲 Skeleton | Needs LLM integration |
| LLM service | 🔲 Stub | OpenAI integration pending |
| Notification service | 🔲 TODO | Human review alerts |
| Evaluation pipeline | 🔲 TODO | Quality metrics |

---

## Future Enhancements

1. **LLM Integration** — Connect TriageAgent to OpenAI for classification
2. **Persistent Vector Store** — Replace in-memory with Pinecone/Chroma
3. **Notification Service** — Alert operators when approval needed
4. **Evaluation Pipeline** — Track classification accuracy and retrieval quality
5. **Feedback Loop** — Learn from operator corrections

---

## Why This Architecture?

This system demonstrates production-grade AI engineering practices:

1. **Multi-Agent Design** — Specialized agents with clear responsibilities
2. **RAG Pipeline** — Grounded generation with citations
3. **State Machine Orchestration** — Explicit workflows with LangGraph
4. **Human-in-the-Loop** — AI assists, humans decide
5. **Observable System** — Tracing, metrics, and audit trails
6. **Type Safety** — TypedDict state, Pydantic schemas, dataclasses

It's designed to be:
- **Maintainable** — Clear separation of concerns
- **Testable** — Mocked dependencies, unit tests
- **Observable** — Full traceability
- **Safe** — No autonomous execution
- **Extensible** — Provider-agnostic abstractions

---

*This report was generated from the AI Operations Copilot codebase.*
*Repository: https://github.com/hubertdomagalaa/ai-operations-copilot*
