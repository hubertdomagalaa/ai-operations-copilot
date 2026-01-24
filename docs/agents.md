# Agents

This document describes the AI agents in the Operations Copilot system.

## Agent Overview

The system uses a pipeline of specialized agents, each with a focused responsibility:

```
Ticket → [Triage] → [Knowledge] → [Decision] → [Action] → Response
                         ↓              ↓
                   Vector Store    Human Review
```

## Triage Agent

**Location**: `/agents/triage/`

**Purpose**: First agent to process a ticket. Classifies and prioritizes.

**Inputs**:
- Raw ticket content (subject, body, metadata)

**Outputs**:
- Category (authentication, api_error, performance, etc.)
- Priority (critical, high, medium, low)
- Summary
- Keywords
- Escalation flag

**Key Behaviors**:
- Detects escalation keywords ("outage", "security", "critical")
- Provides confidence score for classification
- Flags for human review if confidence is low

**Confidence Threshold**: 0.7 (configurable)

---

## Knowledge Agent

**Location**: `/agents/knowledge/`

**Purpose**: Retrieves relevant internal documentation via RAG.

**Inputs**:
- Ticket content
- Triage output (category, keywords)

**Outputs**:
- Retrieved documents with relevance scores
- Formatted context for downstream agents
- Source citations

**Key Behaviors**:
- Formulates multiple search queries
- Filters by relevance threshold
- Re-ranks results for quality
- Flags if no relevant documents found

**Relevance Threshold**: 0.5 (configurable)

---

## Decision Agent

**Location**: `/agents/decision/`

**Purpose**: Synthesizes information and recommends actions.

**Inputs**:
- Ticket content
- Triage output
- Knowledge output (documents, context)

**Outputs**:
- Recommended action
- Reasoning
- Alternative actions
- Human review requirement

**Key Behaviors**:
- Considers ticket priority in decision
- Identifies high-risk actions requiring human review
- Provides confidence score
- Always cites sources for recommendations

**Auto-Approve Threshold**: 0.85 (configurable)

**High-Risk Actions** (always require human review):
- `escalate_to_engineering`
- `issue_refund`
- `reset_credentials`

---

## Action Agent

**Location**: `/agents/action/`

**Purpose**: Executes approved actions and drafts responses.

**Inputs**:
- Approved decision (possibly modified by human)
- Ticket content
- Knowledge context

**Outputs**:
- Draft response text
- Action checklist
- Execution results (for safe actions)

**Key Behaviors**:
- Only executes pre-approved safe actions
- Drafts responses matching company tone
- Includes documentation references in response
- Creates operator checklist for manual steps

---

## Monitoring Agent

**Location**: `/agents/monitoring/`

**Purpose**: Observes system health (not part of ticket workflow).

**Inputs**:
- Recent workflow executions
- Agent performance data

**Outputs**:
- Health metrics
- Anomaly alerts
- Performance recommendations

**Key Behaviors**:
- Runs periodically or on-demand
- Detects latency anomalies
- Tracks confidence distributions
- Monitors human override rate

---

## Agent Interface

All agents implement the same interface:

```python
class BaseAgent:
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process workflow state and return updated state."""
        pass
```

**Common Output Fields**:
- `agent_type`: Agent identifier
- `success`: Whether processing succeeded
- `result`: Agent-specific output
- `confidence`: 0.0 to 1.0 confidence score
- `reasoning`: Explanation of decision
- `requires_human_review`: Flag for human attention
- `sources`: Document citations

## Adding New Agents

1. Create directory in `/agents/{agent_name}/`
2. Implement `__init__.py` with agent class
3. Inherit from `BaseAgent`
4. Add node in `/orchestration/langgraph/nodes.py`
5. Update workflow in `/orchestration/langgraph/workflow.py`
6. Add tests in `/tests/unit/test_agents.py`
