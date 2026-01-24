"""
Agents Package
==============

Contains AI agent definitions for the Operations Copilot.

Each agent has a specific responsibility in the ticket processing workflow:

- triage: Classifies and prioritizes incoming tickets
- knowledge: Retrieves relevant context from internal documentation
- decision: Evaluates options and recommends actions
- action: Drafts responses and executes approved actions
- monitoring: Tracks system health and agent performance

DESIGN PRINCIPLES:
- Each agent is focused on ONE responsibility
- Agents communicate via the shared WorkflowState
- All agents can signal the need for human review
- Outputs include confidence scores and reasoning
"""
