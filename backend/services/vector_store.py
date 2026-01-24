"""
Vector Store Service
====================

Provides vector database operations for RAG.

WHY THIS FILE EXISTS:
- Abstracts vector store implementation (Chroma, Pinecone, etc.)
- Handles document embedding and retrieval
- Supports different embedding models

USAGE:
    from backend.services.vector_store import get_vector_store
    
    vs = get_vector_store()
    docs = await vs.search(query="api authentication error", k=5)

DESIGN DECISIONS:
- Documents are chunked before embedding
- Embeddings are cached to reduce API calls
- Search returns documents with scores for transparency
"""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod


class RetrievedDocument:
    """
    A document retrieved from the vector store.
    
    Includes content, metadata, and relevance score.
    """
    
    content: str
    metadata: Dict[str, Any]  # Source, date, category, etc.
    score: float              # Relevance score (0-1)
    document_id: str


class VectorStoreService(ABC):
    """
    Abstract base class for vector store services.
    """
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        namespace: str = "default",
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Documents are embedded and indexed.
        Returns list of document IDs.
        
        TODO: Implement in provider-specific subclass
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        k: int = 5,
        namespace: str = "default",
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedDocument]:
        """
        Search for relevant documents.
        
        Returns top-k documents by similarity.
        
        TODO: Implement in provider-specific subclass
        """
        pass
    
    @abstractmethod
    async def delete_documents(
        self,
        document_ids: List[str],
        namespace: str = "default",
    ) -> int:
        """
        Delete documents from the vector store.
        
        Returns count of deleted documents.
        
        TODO: Implement in provider-specific subclass
        """
        pass


class MockVectorStore(VectorStoreService):
    """
    Mock vector store for testing.
    
    Stores documents in memory, uses simple text matching.
    """
    
    def __init__(self):
        self._documents: Dict[str, List[Dict[str, Any]]] = {}
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        namespace: str = "default",
    ) -> List[str]:
        """Store documents in memory."""
        # TODO: Implement mock storage
        raise NotImplementedError("Mock not implemented")
    
    async def search(
        self,
        query: str,
        k: int = 5,
        namespace: str = "default",
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedDocument]:
        """Return mock search results."""
        # TODO: Implement mock search
        raise NotImplementedError("Mock not implemented")
    
    async def delete_documents(
        self,
        document_ids: List[str],
        namespace: str = "default",
    ) -> int:
        """Delete from mock storage."""
        # TODO: Implement mock deletion
        raise NotImplementedError("Mock not implemented")


def get_vector_store() -> VectorStoreService:
    """
    Factory function to get the configured vector store.
    
    TODO: Implement provider detection and instantiation
    """
    # TODO: Read from config.settings.vector_store_url
    # TODO: Return appropriate implementation
    return MockVectorStore()
