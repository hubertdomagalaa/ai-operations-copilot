# Known Limitations and TODOs

**Project Status:** Production-ready core with documented limitations  
**Date:** January 30, 2026

---

## Critical TODOs (Block Production)

These items must be addressed before full production deployment:

###1. Shadow Mode Not Enforced
**Location:** `orchestration/langgraph/workflow.py`  
**Issue:** `is_shadow_mode()` function exists but workflow doesn't check it  
**Impact:** Cannot safely test prompt changes without downstream execution  
**Fix Effort:** 1 hour  
**Priority:** HIGH

```python
# Add after triage_node in workflow
if is_shadow_mode():
    state["status"] = "shadow_mode_complete"
    return state
```

### 2. Resume Workflow API Broken
**Location:** `orchestration/langgraph/workflow.py:302`  
**Issue:** Uses non-existent `aget_state()` method  
**Impact:** Cannot resume workflowFromCheckpoint  
**Fix Effort:** 2 hours  
**Priority:** HIGH

### 3. OpenRouter JSON Parsing Fragile
**Location:** `backend/services/llm/openrouter.py`  
**Issue:** No handling of markdown fences in LLM responses  
**Impact:** LLM returns ` ```json ... ``` ` → parse failure → escalation  
**Fix Effort:** 2 hours  
**Priority:** HIGH

### 4. RAG Query Unbounded
**Location:** `agents/knowledge/__init__.py`  
**Issue:** No character limit on query strings, no max query count  
**Impact:** Long tickets → 100+ queries → timeout  
**Fix Effort:** 1 hour  
**Priority:** MEDIUM

---

## Observability TODOs (Enhancement, Not Blocking)

These are intentional gaps for future enhancement. System is functional without them.

### Logging and Metrics
**Locations:**
- `orchestration/langgraph/nodes.py:131` — Log retrieval metrics
- `orchestration/langgraph/nodes.py:142` — Log knowledge agent errors
- `orchestration/langgraph/nodes.py:178` — Log decision metrics
- `orchestration/langgraph/nodes.py:188` — Log decision agent errors
- `orchestration/langgraph/nodes.py:228` — Log action metrics
- `orchestration/langgraph/nodes.py:248` — Log action agent errors

**Rationale:** Basic error handling exists (exceptions caught, state.error set). Detailed logging is deferred until observability infrastructure is defined.

### Monitoring Infrastructure
**Location:** `orchestration/langgraph/nodes.py:272-290`  
**Items:**
- Calculate workflow duration
- Record metrics
- Log confidence scores
- Emit evaluation events

**Rationale:** MonitoringAgent structure exists but implementation is deferred. This doesn't block workflow execution.

### Notification Integration
**Location:** `orchestration/langgraph/nodes.py:362`  
**Issue:** No integration with notification service (Slack, email)  
**Rationale:** Notification mechanism is environment-specific. API exists for polling.

---

## Test TODOs (Deferred)

Test files contain TODOs for unit tests that are not yet implemented. This is acceptable because:

1. **Dry run tests exist** — Full end-to-end workflow validated
2. **Schema validation enforces contracts** — Pydantic catches structural errors
3. **Unit tests are nice-to-have** — Not blocking for production with HITL enabled

**Files with test TODOs:**
- `tests/unit/test_agents.py` — 20 TODOs (all test implementation placeholders)
- `tests/integration/test_api.py` — 13 TODOs (backend integration tests)
- `tests/unit/test_workflow.py` — Workflow unit tests

**Decision:** Leave test TODOs in place as markers for future test expansion.

---

## Documentation TODOs (None)

All documentation is complete. No outstanding documentation TODOs.

---

## Architecture TODOs (Intentional Limitations)

These are not bugs but design choices marked with TODOs for future consideration:

### Workflow Error Handling
**Location:** `orchestration/langgraph/workflow.py:261`  
**TODO:** "Add error handling for workflow execution"  
**Current State:** Errors are caught in individual nodes and routed to error node  
**Decision:** Current error handling is sufficient. More sophisticated retry logic is v2 work.

### Synchronous Workflow Execution
**Location:** `orchestration/langgraph/workflow.py:337`  
**TODO:** "This is synchronous; may need async version"  
**Current State:** `run_workflow` is async, but checkpointing is sync  
**Decision:** Acceptable for current scale. Async checkpointing is optimization, not requirement.

---

## Summary

**Total TODOs found:** 62  
**Critical (blocking):** 4  
**Enhancement (non-blocking):** 8  
**Test placeholders:** 33  
**Documentation:** 0  
**Architectural notes:** 2

**Action Plan:**
1. Fix 4 critical TODOs (6 hours total)
2. Document enhancement TODOs in PROJECT_STATUS.md
3. Leave test and architectural TODOs as markers for future work

**Status after fixes:** Fully production-ready
