# Data Directory — Documents

This directory contains internal documentation for RAG.

## Purpose
- Store internal documentation for knowledge retrieval
- Provide context for the knowledge agent
- Maintain the knowledge base for the Operations Copilot

## Document Types
- API documentation
- Troubleshooting guides
- Known issues and solutions
- Operational runbooks
- Historical incident reports

## Structure (when implemented)
- `api_docs/` — REST API documentation
- `troubleshooting/` — Issue resolution guides
- `runbooks/` — Operational procedures
- `incidents/` — Past incident reports

## Ingestion
Documents in this directory should be:
1. Chunked appropriately
2. Embedded using the configured model
3. Indexed in the vector store

See `backend/services/vector_store.py` for the ingestion interface.
