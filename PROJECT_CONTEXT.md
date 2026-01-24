# AI Operations Copilot — Project Context

## Purpose
This repository contains an internal AI Operations Copilot designed for a B2B SaaS company providing a REST API for user management and authentication.

The system supports operational decision-making by ingesting support tickets, retrieving internal knowledge, orchestrating AI agents, and assisting human operators with classification, prioritization, and recommended actions.

This is a production-minded AI Engineering project, not a demo or prototype.

## Target Company Profile
- B2B SaaS
- REST API product
- Microservice-based backend
- Typical issues: API errors, authentication problems, incidents, operational questions

## Core Use Case
A support ticket related to an API issue enters the system. The AI Operations Copilot:
1. Classifies and prioritizes the ticket
2. Retrieves relevant internal documentation and historical context
3. Assists in deciding whether to escalate, automate, or route the issue
4. Generates a draft response or action checklist
5. Records feedback and operational metrics

## System Philosophy
- Human-in-the-loop is mandatory
- AI assists decisions; it does not act autonomously in production
- All AI outputs must be grounded in retrieved sources
- Observability, evaluation, and feedback loops are first-class concerns

## Out of Scope
- Customer-facing chatbots
- Autonomous system changes
- External integrations beyond mock interfaces
- Advanced UI (simple dashboard at most)

## Development Principles
- Incremental development
- Clear ownership of responsibilities
- Avoid overengineering
- No speculative features
- Every component must justify its existence

## Intended Audience
- AI Engineers
- Backend Engineers
- Technical Recruiters and Hiring Managers

This file should be read at the beginning of each new development session.
