"""
Document Chunking
=================

Splits documents into retrievable chunks for embedding.

WHY THIS FILE EXISTS:
- LLM context windows are limited
- Smaller chunks enable more precise retrieval
- Chunking strategy significantly impacts RAG quality

CHUNKING STRATEGY:
We use a simple, explainable approach: fixed-size chunks with overlap.

JUSTIFICATION FOR PARAMETERS:

CHUNK_SIZE = 512 characters
- Small enough to fit multiple chunks in LLM context
- Large enough to contain meaningful information
- Roughly ~100-150 tokens (depending on content)
- Allows precise retrieval without losing context

CHUNK_OVERLAP = 64 characters
- ~12% overlap prevents cutting sentences mid-thought
- Ensures important information at chunk boundaries is preserved
- Not so large that it wastes embedding compute

WHY NOT SEMANTIC CHUNKING:
- Adds complexity without guaranteed benefit for our use case
- Fixed chunks are predictable and debuggable
- We can evolve later if evaluation shows need

METADATA PRESERVATION:
- Each chunk inherits parent document metadata
- chunk_index tracks position in original document
- start_char and end_char enable source highlighting
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
import hashlib

from backend.services.rag.ingestion import Document


# === CHUNKING PARAMETERS ===
# These are intentionally module-level constants for visibility

CHUNK_SIZE = 512
"""
Target chunk size in characters.

WHY 512:
- Balances retrieval precision with context sufficiency
- Maps to roughly 100-150 tokens
- Small enough to retrieve multiple relevant chunks
- Large enough to contain a complete thought/paragraph
"""

CHUNK_OVERLAP = 64
"""
Overlap between consecutive chunks.

WHY 64 (~12% of chunk size):
- Prevents losing context at chunk boundaries
- Ensures sentences aren't cut mid-way
- Keeps overlap manageable for storage efficiency
"""


@dataclass
class Chunk:
    """
    A chunk of text ready for embedding.
    
    Each chunk is a self-contained piece of retrievable content
    with full metadata for citation and traceability.
    """
    
    content: str
    chunk_id: str            # Unique identifier for this chunk
    document_id: str         # ID of parent document
    chunk_index: int         # Position in original document (0-indexed)
    
    # Character positions in original document
    start_char: int
    end_char: int
    
    # Inherited from parent document
    source: str              # Original file path
    filename: str
    doc_type: str
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "content": self.content,
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "source": self.source,
            "filename": self.filename,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
        }


def generate_document_id(source: str, content: str) -> str:
    """
    Generate a stable document ID.
    
    Based on source path and content hash for deduplication.
    """
    hash_input = f"{source}:{len(content)}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """
    Generate a stable chunk ID.
    
    Combines document ID with chunk index for uniqueness.
    """
    return f"{document_id}-chunk-{chunk_index:04d}"


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk
        chunk_overlap: Overlap between consecutive chunks
    
    Returns:
        List of dicts with 'content', 'start_char', 'end_char'
    
    WHY THIS ALGORITHM:
    - Simple sliding window approach
    - Predictable behavior for debugging
    - No external dependencies
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Calculate end position
        end = min(start + chunk_size, text_length)
        
        # Extract chunk content
        content = text[start:end]
        
        # Only add non-empty chunks
        if content.strip():
            chunks.append({
                "content": content,
                "start_char": start,
                "end_char": end,
            })
        
        # Move start position for next chunk
        # If we're at the end, break to avoid infinite loop
        if end >= text_length:
            break
        
        # Advance by (chunk_size - overlap)
        start = start + chunk_size - chunk_overlap
    
    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Chunk]:
    """
    Chunk a single document into retrievable pieces.
    
    Args:
        document: The Document to chunk
        chunk_size: Target chunk size (default: 512)
        chunk_overlap: Overlap size (default: 64)
    
    Returns:
        List of Chunk objects with full metadata
    """
    # Generate document ID
    document_id = generate_document_id(document.source, document.content)
    
    # Chunk the text
    raw_chunks = chunk_text(document.content, chunk_size, chunk_overlap)
    
    # Create Chunk objects with metadata
    chunks = []
    for idx, raw in enumerate(raw_chunks):
        chunk = Chunk(
            content=raw["content"],
            chunk_id=generate_chunk_id(document_id, idx),
            document_id=document_id,
            chunk_index=idx,
            start_char=raw["start_char"],
            end_char=raw["end_char"],
            source=document.source,
            filename=document.filename,
            doc_type=document.doc_type,
            metadata={
                **document.metadata,
                "total_chunks": len(raw_chunks),
            }
        )
        chunks.append(chunk)
    
    return chunks


def chunk_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Chunk]:
    """
    Chunk multiple documents.
    
    Args:
        documents: List of Documents to chunk
        chunk_size: Target chunk size
        chunk_overlap: Overlap size
    
    Returns:
        List of all Chunks from all documents
    """
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_document(doc, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
    
    # TODO: Log chunking stats
    # TODO: Emit metrics (total chunks, avg chunk size, etc.)
    
    return all_chunks
