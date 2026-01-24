# System Overview

The AI Operations Copilot is an internal tool that assists human operators in processing support tickets for a B2B SaaS REST API product.

## The Problem

Support teams handling API-related tickets face challenges:
- High volume of tickets with varying complexity
- Need for quick classification and prioritization
- Finding relevant documentation across multiple sources
- Ensuring consistent, accurate responses
- Maintaining quality under time pressure

## The Solution

An AI-assisted workflow that:
1. **Classifies** incoming tickets by category and priority
2. **Retrieves** relevant internal documentation
3. **Recommends** actions with supporting evidence
4. **Drafts** responses for human review
5. **Learns** from operator feedback

## Key Principles

### Human-in-the-Loop
- AI assists but does not act autonomously
- All significant decisions require human approval
- Operators can override any AI recommendation

### Grounded Responses
- All AI outputs cite sources
- Recommendations are based on retrieved documentation
- Confidence scores are provided for transparency

### Observable System
- Full tracing of every workflow
- Metrics for performance and quality
- Audit trail for compliance

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                     │
│  /tickets  /agents  /health                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  ORCHESTRATION (LangGraph)                  │
│  Workflow management, state persistence, routing            │
└───────┬─────────┬─────────┬─────────┬─────────┬─────────────┘
        │         │         │         │         │
   ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼───┐ ┌───▼────┐
   │ Triage │ │Knowledge│ │Decide│ │Action │ │Monitor │
   │  Agent │ │  Agent  │ │Agent │ │ Agent │ │  Agent │
   └────────┘ └────┬────┘ └──────┘ └───────┘ └────────┘
                   │
           ┌───────▼───────┐
           │  Vector Store │
           │    (RAG)      │
           └───────────────┘
```

## For Developers

- **Backend**: FastAPI application in `/backend`
- **Agents**: LangChain-based agents in `/agents`
- **Workflow**: LangGraph definitions in `/orchestration`
- **Tests**: pytest-based in `/tests`
- **Docs**: This directory

## Getting Started

See `architecture.md` for technical details and `data_flow.md` for workflow specifics.
