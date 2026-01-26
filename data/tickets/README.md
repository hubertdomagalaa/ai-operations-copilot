# Ticket Dataset

This directory contains a production-style dataset of support tickets.

## Structure
- raw/        – immutable source tickets (public GitHub issues)
- normalized/ – structured representations used by the AI system

## Data quality
- All tickets have been audited for schema correctness
- No hallucinated fields
- Conservative normalization strategy

## Status
LOCKED – no further modifications expected.

Downstream usage:
- RAG ingestion
- Agent workflows
- Offline evaluation
