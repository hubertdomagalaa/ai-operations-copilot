"""
RAG (Retrieval-Augmented Generation) Package
=============================================

Production-grade retrieval system for the AI Operations Copilot.

WHY THIS PACKAGE EXISTS:
- RAG is a system, not a prompt
- Separates ingestion, storage, and retrieval concerns
- Enforces grounding: no retrieval = no answer
- Every fact must be traceable to a source

CORE PRINCIPLES:
1. KnowledgeAgent never hallucinates — only returns retrieved content
2. All outputs include source citations
3. Retrieval and reasoning are strictly separated
4. Explainability over cleverness

MODULES:
- ingestion.py: Load and prepare documents from /data/documents
- chunking.py: Split documents into retrievable chunks
- embeddings.py: Provider-agnostic embedding abstraction
- store.py: Vector store implementation
- retrieval.py: Search interface with citations

USAGE:
    from backend.services.rag import RAGPipeline
    
    # Ingest documents
    pipeline = RAGPipeline()
    await pipeline.ingest_documents("/data/documents")
    
    # Retrieve
    results = await pipeline.retrieve("API authentication error")
"""

from backend.services.rag.retrieval import RAGPipeline, RetrievalResult

__all__ = ["RAGPipeline", "RetrievalResult"]
