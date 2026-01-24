"""
Vector Store Implementation
===========================

In-memory vector store for RAG retrieval.

WHY THIS FILE EXISTS:
- Provides a working vector store without external dependencies
- Designed to be replaced with production stores (Chroma, Pinecone)
- Supports all required operations: add, search, delete

DESIGN DECISIONS:
- In-memory storage for simplicity
- Cosine similarity for relevance ranking
- Full metadata preservation
- Namespace support for isolation

PRODUCTION REPLACEMENT:
This implementation is suitable for development and testing.
For production, replace with:
- Chroma for local persistent storage
- Pinecone for cloud-native vector search
- Weaviate for hybrid search

The interface is designed to make replacement straightforward.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import math
import uuid
import time

from backend.services.rag.embeddings import EmbeddingService, get_embedding_service
from backend.services.rag.chunking import Chunk


@dataclass
class StoredChunk:
    """
    A chunk stored in the vector store with its embedding.
    """
    
    chunk_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    
    # Source information for citations
    source: str
    filename: str
    doc_type: str


@dataclass
class SearchResult:
    """
    A search result with similarity score.
    
    This is what KnowledgeAgent receives for each retrieved document.
    """
    
    chunk_id: str
    content: str
    score: float  # Cosine similarity (0-1, higher is better)
    
    # Citation information
    source: str
    filename: str
    doc_type: str
    
    # Full metadata for traceability
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for state storage."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "filename": self.filename,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
        }


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Returns value between -1 and 1, where 1 is most similar.
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions don't match: {len(a)} vs {len(b)}")
    
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)


class InMemoryVectorStore:
    """
    Simple in-memory vector store.
    
    Provides all operations needed for RAG without external dependencies.
    
    LIMITATIONS:
    - Data lost on restart (no persistence)
    - Linear search (O(n) query time)
    - Memory-bound (all vectors in RAM)
    
    GOOD FOR:
    - Development and testing
    - Small document collections (<10k chunks)
    - Rapid iteration
    """
    
    def __init__(self, embedding_service: EmbeddingService = None):
        """
        Initialize the vector store.
        
        Args:
            embedding_service: Service for creating embeddings.
                               Defaults to LocalEmbedding.
        """
        if embedding_service is None:
            embedding_service = get_embedding_service("local")
        
        self._embedding_service = embedding_service
        self._chunks: Dict[str, StoredChunk] = {}  # chunk_id -> StoredChunk
        self._namespaces: Dict[str, set] = {"default": set()}  # namespace -> set of chunk_ids
        
        # Stats for observability
        self._stats = {
            "total_chunks": 0,
            "total_searches": 0,
            "avg_search_time_ms": 0,
        }
    
    async def add_chunks(
        self,
        chunks: List[Chunk],
        namespace: str = "default",
    ) -> List[str]:
        """
        Add chunks to the vector store.
        
        Args:
            chunks: Chunks to add (from chunking.py)
            namespace: Namespace for isolation
        
        Returns:
            List of chunk IDs that were added
        """
        if namespace not in self._namespaces:
            self._namespaces[namespace] = set()
        
        added_ids = []
        
        # Batch embed all chunks
        contents = [chunk.content for chunk in chunks]
        embeddings = await self._embedding_service.embed_texts(contents)
        
        for chunk, embedding in zip(chunks, embeddings):
            stored = StoredChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                embedding=embedding,
                metadata=chunk.to_dict(),
                source=chunk.source,
                filename=chunk.filename,
                doc_type=chunk.doc_type,
            )
            
            self._chunks[chunk.chunk_id] = stored
            self._namespaces[namespace].add(chunk.chunk_id)
            added_ids.append(chunk.chunk_id)
        
        self._stats["total_chunks"] = len(self._chunks)
        
        # TODO: Log addition
        # TODO: Emit metrics
        
        return added_ids
    
    async def search(
        self,
        query: str,
        k: int = 5,
        namespace: str = "default",
        min_score: float = 0.0,
    ) -> List[SearchResult]:
        """
        Search for similar chunks.
        
        Args:
            query: Search query text
            k: Maximum number of results
            namespace: Namespace to search
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of SearchResult ordered by similarity (highest first)
        """
        start_time = time.time()
        
        # Get query embedding
        query_embedding = await self._embedding_service.embed_text(query)
        
        # Get chunks in namespace
        namespace_ids = self._namespaces.get(namespace, set())
        
        # Score all chunks
        scored = []
        for chunk_id in namespace_ids:
            chunk = self._chunks.get(chunk_id)
            if chunk:
                score = cosine_similarity(query_embedding, chunk.embedding)
                if score >= min_score:
                    scored.append((chunk, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Take top k
        results = []
        for chunk, score in scored[:k]:
            result = SearchResult(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                score=score,
                source=chunk.source,
                filename=chunk.filename,
                doc_type=chunk.doc_type,
                metadata=chunk.metadata,
            )
            results.append(result)
        
        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._stats["total_searches"] += 1
        total = self._stats["total_searches"]
        avg = self._stats["avg_search_time_ms"]
        self._stats["avg_search_time_ms"] = (avg * (total - 1) + elapsed_ms) / total
        
        # TODO: Log search
        # TODO: Emit metrics (latency, result count)
        
        return results
    
    async def delete_chunks(
        self,
        chunk_ids: List[str],
        namespace: str = "default",
    ) -> int:
        """
        Delete chunks from the store.
        
        Args:
            chunk_ids: IDs of chunks to delete
            namespace: Namespace to delete from
        
        Returns:
            Number of chunks deleted
        """
        deleted = 0
        namespace_ids = self._namespaces.get(namespace, set())
        
        for chunk_id in chunk_ids:
            if chunk_id in self._chunks:
                del self._chunks[chunk_id]
                namespace_ids.discard(chunk_id)
                deleted += 1
        
        self._stats["total_chunks"] = len(self._chunks)
        
        return deleted
    
    async def clear(self, namespace: str = None):
        """
        Clear chunks from store.
        
        Args:
            namespace: If provided, clear only that namespace.
                       If None, clear everything.
        """
        if namespace is None:
            self._chunks.clear()
            self._namespaces = {"default": set()}
        else:
            namespace_ids = self._namespaces.get(namespace, set())
            for chunk_id in list(namespace_ids):
                if chunk_id in self._chunks:
                    del self._chunks[chunk_id]
            self._namespaces[namespace] = set()
        
        self._stats["total_chunks"] = len(self._chunks)
    
    def get_stats(self) -> Dict[str, Any]:
        """Return store statistics."""
        return {
            **self._stats,
            "embedding_model": self._embedding_service.model_name,
            "embedding_dimension": self._embedding_service.dimension,
        }


# Global store instance (for simple usage)
_default_store: Optional[InMemoryVectorStore] = None


def get_vector_store() -> InMemoryVectorStore:
    """
    Get the default vector store instance.
    
    Creates one if it doesn't exist.
    """
    global _default_store
    if _default_store is None:
        _default_store = InMemoryVectorStore()
    return _default_store


def reset_vector_store():
    """
    Reset the default vector store.
    
    Useful for testing.
    """
    global _default_store
    _default_store = None
