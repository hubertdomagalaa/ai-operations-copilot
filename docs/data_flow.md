# Data Flow

This document describes how data flows through the AI Operations Copilot system.

## Ticket Processing Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        TICKET INGESTION                         │
│  POST /tickets → Validate → Store → Trigger Workflow            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TRIAGE PHASE                            │
│  1. Extract ticket content                                      │
│  2. Prompt LLM for classification                               │
│  3. Parse category, priority, keywords                          │
│  4. Check for escalation keywords                               │
│  5. Route: escalate immediately OR continue                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
         [escalate]                          [continue]
              │                                   │
              ▼                                   ▼
   ┌──────────────────┐             ┌─────────────────────────────┐
   │   Human Review   │             │      KNOWLEDGE PHASE        │
   │  (Urgent Case)   │             │  1. Formulate search queries│
   └──────────────────┘             │  2. Query vector store      │
                                    │  3. Filter by relevance     │
                                    │  4. Format context          │
                                    └───────────────┬─────────────┘
                                                    │
                                                    ▼
                                    ┌─────────────────────────────┐
                                    │       DECISION PHASE        │
                                    │  1. Gather all context      │
                                    │  2. Prompt LLM for decision │
                                    │  3. Parse recommendation    │
                                    │  4. Check confidence        │
                                    │  5. Route: human OR action  │
                                    └───────────────┬─────────────┘
                                                    │
                              ┌─────────────────────┴──────────────┐
                              │                                    │
                      [needs_human]                         [auto_approve]
                              │                                    │
                              ▼                                    │
                   ┌──────────────────┐                            │
                   │   Human Review   │                            │
                   │  1. View ticket  │                            │
                   │  2. Review reco  │                            │
                   │  3. Approve/edit │                            │
                   └────────┬─────────┘                            │
                            │                                      │
                            └───────────────┬──────────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────────────────┐
                              │          ACTION PHASE              │
                              │  1. Get approved decision          │
                              │  2. Draft response                 │
                              │  3. Build action checklist         │
                              │  4. Execute safe actions           │
                              └───────────────┬─────────────────────┘
                                              │
                                              ▼
                              ┌─────────────────────────────────────┐
                              │           COMPLETION               │
                              │  1. Update ticket status           │
                              │  2. Record metrics                 │
                              │  3. Emit completion event          │
                              └─────────────────────────────────────┘
```

## State Throughout Workflow

The workflow state evolves as it passes through agents:

| After | State Contains |
|-------|----------------|
| Ingestion | ticket_id, ticket_data, trace_id |
| Triage | + triage_output (category, priority, keywords) |
| Knowledge | + knowledge_output (documents, context) |
| Decision | + decision_output (recommendation, confidence) |
| Human Review | + human_decision (approval, modifications) |
| Action | + action_output (draft, checklist, results) |

## Human-in-the-Loop Points

Workflow pauses for human input at these points:

1. **Immediate Escalation**: Ticket flagged for urgent human attention
2. **Low Confidence**: Agent confidence below threshold
3. **High-Risk Action**: Action requires human approval
4. **Conflicting Information**: Contradictory retrieved documents

### Resuming After Human Input

```
Human submits decision via POST /agents/feedback/{ticket_id}
    │
    ▼
Workflow loads checkpoint from LangGraph
    │
    ▼
State updated with human_decision
    │
    ▼
Workflow resumes from human_review node
```

## Error Handling

```
Any Node Failure
    │
    ▼
Error captured in state.error
    │
    ▼
Workflow routes to error_node
    │
    ▼
Status set to "failed"
    │
    ▼
Alert sent to operators
```

## Observability

At each step:
- Trace span opened and closed
- Metrics recorded (latency, confidence)
- Structured log emitted

## Data Persistence

| Data | Storage | Purpose |
|------|---------|---------|
| Tickets | Database (TBD) | Source of truth |
| Workflow State | LangGraph Checkpoint | Resume after pause |
| Documents | Vector Store | RAG retrieval |
| Logs | File/Cloud | Debugging |
| Metrics | Prometheus (TBD) | Monitoring |
