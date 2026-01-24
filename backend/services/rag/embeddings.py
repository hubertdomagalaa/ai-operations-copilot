"""
Embedding Abstraction
=====================

Provider-agnostic interface for text embeddings.

WHY THIS FILE EXISTS:
- Decouples embedding logic from specific providers
- Enables switching providers via config
- Supports local, OpenAI, and other embedding models
- Provides consistent interface for the RAG pipeline

SUPPORTED PROVIDERS (via configuration):
- "local": Simple TF-IDF based embedding (no external API)
- "openai": OpenAI text-embedding-ada-002 or text-embedding-3-small
- Future: "sentence-transformers", "cohere", etc.

DESIGN DECISIONS:
- Abstract base class with simple interface
- Batch embedding for efficiency
- Dimension exposed for vector store configuration
- Default to local embeddings for development

NO EXTERNAL DEPENDENCIES BY DEFAULT:
The LocalEmbedding class uses simple TF-IDF to avoid requiring
API keys or external services for development and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import math
import re
from collections import Counter


class EmbeddingService(ABC):
    """
    Abstract base class for embedding services.
    
    All embedding providers must implement this interface.
    """
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Return the embedding dimension.
        
        Vector stores need to know this for index configuration.
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier for logging."""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: The text to embed
        
        Returns:
            Embedding vector as list of floats
        """
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts in a batch.
        
        More efficient than calling embed_text repeatedly.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        pass


class LocalEmbedding(EmbeddingService):
    """
    Simple local embedding using TF-IDF-like vectors.
    
    WHY THIS EXISTS:
    - No external API dependencies for development
    - Fast execution for testing
    - Deterministic results for debugging
    
    LIMITATIONS:
    - Not as semantically rich as neural embeddings
    - Fixed vocabulary from training corpus
    - Should be replaced with real embeddings in production
    
    HOW IT WORKS:
    - Each dimension represents a word or n-gram
    - Values are normalized term frequencies
    - Similarity is approximated via cosine distance
    """
    
    # Fixed dimension for consistent behavior
    EMBEDDING_DIMENSION = 256
    
    def __init__(self):
        self._vocabulary: dict = {}
        self._idf: dict = {}
        self._initialized = False
    
    @property
    def dimension(self) -> int:
        return self.EMBEDDING_DIMENSION
    
    @property
    def model_name(self) -> str:
        return "local-tfidf-256"
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase and split on non-alphanumeric."""
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _compute_tf(self, tokens: List[str]) -> dict:
        """Compute term frequency."""
        counts = Counter(tokens)
        total = len(tokens) if tokens else 1
        return {term: count / total for term, count in counts.items()}
    
    def _hash_to_dimension(self, term: str) -> int:
        """Hash term to a fixed dimension index."""
        # Simple hash function for reproducibility
        h = 0
        for c in term:
            h = (h * 31 + ord(c)) % self.EMBEDDING_DIMENSION
        return h
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Create a simple embedding vector.
        
        Uses term frequency with hashing trick for fixed dimensions.
        """
        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)
        
        # Initialize embedding with zeros
        embedding = [0.0] * self.EMBEDDING_DIMENSION
        
        # Add term frequencies to hashed positions
        for term, freq in tf.items():
            idx = self._hash_to_dimension(term)
            embedding[idx] += freq
        
        # Normalize to unit vector
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [await self.embed_text(text) for text in texts]


class OpenAIEmbedding(EmbeddingService):
    """
    OpenAI embedding service.
    
    Uses text-embedding-3-small by default for cost efficiency.
    
    TODO: Implement when OpenAI integration is needed
    """
    
    # text-embedding-3-small has 1536 dimensions
    EMBEDDING_DIMENSION = 1536
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        self._model = model
        self._api_key = api_key
        # TODO: Initialize OpenAI client
    
    @property
    def dimension(self) -> int:
        return self.EMBEDDING_DIMENSION
    
    @property
    def model_name(self) -> str:
        return self._model
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed text using OpenAI API.
        
        TODO: Implement OpenAI API call
        """
        # TODO: Call OpenAI embeddings API
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI(api_key=self._api_key)
        # response = await client.embeddings.create(
        #     model=self._model,
        #     input=text,
        # )
        # return response.data[0].embedding
        
        raise NotImplementedError("OpenAI embedding not implemented")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embed texts using OpenAI API.
        
        TODO: Implement with batching for efficiency
        """
        # TODO: Implement batch embedding
        raise NotImplementedError("OpenAI embedding not implemented")


def get_embedding_service(provider: str = "local") -> EmbeddingService:
    """
    Factory function to get the configured embedding service.
    
    Args:
        provider: "local" or "openai"
    
    Returns:
        Configured EmbeddingService instance
    
    WHY FACTORY PATTERN:
    - Centralizes provider selection
    - Easy to add new providers
    - Configuration-driven switching
    """
    if provider == "local":
        return LocalEmbedding()
    elif provider == "openai":
        # TODO: Read API key from config
        return OpenAIEmbedding()
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
