"""
RAG Retrieval Interface
=======================

High-level retrieval interface for the KnowledgeAgent.

WHY THIS FILE EXISTS:
- Provides a clean interface for the agent layer
- Orchestrates ingestion → chunking → embedding → retrieval
- Enforces citation tracking
- Centralizes retrieval configuration

CORE PRINCIPLE:
No retrieval = no answer.
This module never generates content, only retrieves grounded facts.

USAGE:
    from backend.services.rag import RAGPipeline
    
    # Initialize and ingest documents
    pipeline = RAGPipeline()
    await pipeline.ingest_documents()
    
    # Retrieve relevant context
    results = await pipeline.retrieve(
        query="API authentication error 401",
        k=5,
    )
    
    # Each result has content with full citation
    for r in results:
        print(f"[{r.filename}] {r.content[:100]}...")
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time

from backend.services.rag.ingestion import DocumentIngestionPipeline, Document
from backend.services.rag.chunking import chunk_documents, Chunk, CHUNK_SIZE, CHUNK_OVERLAP
from backend.services.rag.embeddings import EmbeddingService, get_embedding_service
from backend.services.rag.store import InMemoryVectorStore, SearchResult


@dataclass
class RetrievalResult:
    """
    A retrieval result with full citation.
    
    This is what KnowledgeAgent attaches to the workflow state.
    All fields support traceability and grounding.
    """
    
    content: str           # The retrieved text
    score: float           # Similarity score (0-1)
    
    # Citation information (REQUIRED)
    source: str            # Full file path
    filename: str          # Just the filename
    doc_type: str          # Document category
    chunk_id: str          # Unique chunk identifier
    
    # Additional context
    metadata: Dict[str, Any]
    
    def to_citation(self) -> str:
        """
        Format as a human-readable citation.
        
        Example: "[api_authentication.md] (chunk 3, score: 0.87)"
        """
        chunk_num = self.metadata.get("chunk_index", "?")
        return f"[{self.filename}] (chunk {chunk_num}, score: {self.score:.2f})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for workflow state storage."""
        return {
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "filename": self.filename,
            "doc_type": self.doc_type,
            "chunk_id": self.chunk_id,
            "citation": self.to_citation(),
            "metadata": self.metadata,
        }


class RAGPipeline:
    """
    Complete RAG pipeline for document retrieval.
    
    Orchestrates:
    1. Document ingestion from /data/documents
    2. Chunking with consistent parameters
    3. Embedding and storage
    4. Retrieval with citations
    
    KnowledgeAgent uses this class exclusively for retrieval.
    
    DOES NOT:
    - Generate summaries or answers
    - Make decisions
    - Modify content
    """
    
    def __init__(
        self,
        documents_dir: str = None,
        embedding_provider: str = "local",
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            documents_dir: Path to documents (default: /data/documents)
            embedding_provider: "local" or "openai"
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self._ingestion = DocumentIngestionPipeline(documents_dir)
        self._embedding_service = get_embedding_service(embedding_provider)
        self._store = InMemoryVectorStore(self._embedding_service)
        
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        
        # Track pipeline state
        self._is_initialized = False
        self._stats = {
            "documents_ingested": 0,
            "chunks_stored": 0,
            "total_retrievals": 0,
            "avg_retrieval_time_ms": 0,
        }
    
    async def ingest_documents(
        self,
        extensions: List[str] = None,
        namespace: str = "default",
    ) -> Dict[str, Any]:
        """
        Ingest all documents from the documents directory.
        
        This should be called once at startup or when documents change.
        
        Args:
            extensions: File extensions to include
            namespace: Namespace for isolation
        
        Returns:
            Ingestion statistics
        """
        # Load documents
        documents = self._ingestion.ingest(extensions)
        
        if not documents:
            return {
                "status": "no_documents",
                "documents_loaded": 0,
                "chunks_created": 0,
            }
        
        # Chunk documents
        chunks = chunk_documents(
            documents,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        
        # Store chunks with embeddings
        chunk_ids = await self._store.add_chunks(chunks, namespace)
        
        # Update stats
        self._stats["documents_ingested"] = len(documents)
        self._stats["chunks_stored"] = len(chunk_ids)
        self._is_initialized = True
        
        # TODO: Log ingestion completion
        # TODO: Emit metrics
        
        return {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "chunks_stored": len(chunk_ids),
        }
    
    async def retrieve(
        self,
        query: str,
        k: int = 5,
        min_score: float = 0.0,
        namespace: str = "default",
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.
        
        This is the main interface for KnowledgeAgent.
        
        Args:
            query: Search query (can be ticket text or keywords)
            k: Maximum number of results
            min_score: Minimum similarity score
            namespace: Namespace to search
        
        Returns:
            List of RetrievalResult with citations
        
        GUARANTEES:
        - Results are ordered by relevance (highest first)
        - Each result has full citation information
        - Empty list if nothing relevant found (not an error)
        """
        start_time = time.time()
        
        # Search vector store
        search_results = await self._store.search(
            query=query,
            k=k,
            min_score=min_score,
            namespace=namespace,
        )
        
        # Convert to RetrievalResult with citations
        results = []
        for sr in search_results:
            result = RetrievalResult(
                content=sr.content,
                score=sr.score,
                source=sr.source,
                filename=sr.filename,
                doc_type=sr.doc_type,
                chunk_id=sr.chunk_id,
                metadata=sr.metadata,
            )
            results.append(result)
        
        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._stats["total_retrievals"] += 1
        total = self._stats["total_retrievals"]
        avg = self._stats["avg_retrieval_time_ms"]
        self._stats["avg_retrieval_time_ms"] = (avg * (total - 1) + elapsed_ms) / total
        
        # TODO: Log retrieval
        # TODO: Emit metrics (latency, result count, confidence)
        
        return results
    
    async def retrieve_for_ticket(
        self,
        ticket_data: Dict[str, Any],
        triage_output: Dict[str, Any] = None,
        k: int = 5,
    ) -> List[RetrievalResult]:
        """
        Retrieve documents relevant to a ticket.
        
        Builds multiple queries from ticket content and triage output.
        This is the preferred method for KnowledgeAgent.
        
        Args:
            ticket_data: The ticket from workflow state
            triage_output: Triage agent output (optional, for keywords)
            k: Maximum results
        
        Returns:
            Deduplicated, ranked results from all queries
        """
        queries = []
        
        # Query from ticket subject
        subject = ticket_data.get("subject", "")
        if subject:
            queries.append(subject)
        
        # Query from ticket body (first 200 chars)
        body = ticket_data.get("body", "")
        if body:
            queries.append(body[:200])
        
        # Query from triage keywords
        if triage_output:
            keywords = triage_output.get("result", {}).get("keywords", [])
            if keywords:
                queries.append(" ".join(keywords))
            
            # Query from triage summary if available
            summary = triage_output.get("result", {}).get("summary", "")
            if summary:
                queries.append(summary)
        
        # Retrieve for each query
        all_results: Dict[str, RetrievalResult] = {}  # chunk_id -> result
        
        for query in queries:
            if not query.strip():
                continue
            
            results = await self.retrieve(query, k=k)
            
            for r in results:
                # Keep highest score for duplicates
                if r.chunk_id not in all_results or r.score > all_results[r.chunk_id].score:
                    all_results[r.chunk_id] = r
        
        # Sort by score and limit
        sorted_results = sorted(all_results.values(), key=lambda x: x.score, reverse=True)
        
        return sorted_results[:k]
    
    def is_ready(self) -> bool:
        """Check if pipeline has been initialized."""
        return self._is_initialized
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics for observability."""
        return {
            **self._stats,
            "is_initialized": self._is_initialized,
            "store_stats": self._store.get_stats(),
        }
    
    async def clear(self, namespace: str = None):
        """
        Clear stored documents.
        
        Args:
            namespace: Clear specific namespace, or all if None
        """
        await self._store.clear(namespace)
        self._is_initialized = False
        self._stats["chunks_stored"] = 0


# Global pipeline instance
_default_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get the default RAG pipeline instance.
    
    Use for simple cases where configuration isn't needed.
    """
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = RAGPipeline()
    return _default_pipeline


def reset_rag_pipeline():
    """Reset the global pipeline. Useful for testing."""
    global _default_pipeline
    _default_pipeline = None
