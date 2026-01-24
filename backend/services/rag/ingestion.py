"""
Document Ingestion
==================

Loads documents from the filesystem and prepares them for chunking.

WHY THIS FILE EXISTS:
- Centralizes document loading logic
- Preserves metadata for citation tracking
- Handles different document formats
- Enforces consistent document structure

SUPPORTED FORMATS:
- Markdown (.md)
- Plain text (.txt)
- JSON (.json) — for structured data like incident logs

METADATA PRESERVED:
- source: Original file path
- filename: File name without path
- doc_type: Inferred from path (api_docs, runbooks, incidents, etc.)
- ingested_at: Timestamp of ingestion

DESIGN DECISIONS:
- Documents are loaded as-is, no transformation
- Metadata is attached for traceability
- Invalid files are skipped with warnings, not errors
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Document:
    """
    A document loaded from the filesystem.
    
    This is the raw document before chunking.
    All fields are preserved through the pipeline.
    """
    
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # These are always set by the ingestion pipeline
    source: str = ""          # Full file path
    filename: str = ""        # Just the filename
    doc_type: str = "unknown" # Inferred category
    
    def __post_init__(self):
        """Ensure metadata includes standard fields."""
        self.metadata["source"] = self.source
        self.metadata["filename"] = self.filename
        self.metadata["doc_type"] = self.doc_type


def infer_doc_type(file_path: str) -> str:
    """
    Infer document type from file path.
    
    Categories are based on expected directory structure:
    - api_docs/  → "api_documentation"
    - runbooks/  → "runbook"
    - incidents/ → "incident"
    - tickets/   → "historical_ticket"
    - troubleshooting/ → "troubleshooting"
    
    WHY: Document type helps downstream agents understand context.
    """
    path_lower = file_path.lower()
    
    if "api_doc" in path_lower or "api-doc" in path_lower:
        return "api_documentation"
    elif "runbook" in path_lower:
        return "runbook"
    elif "incident" in path_lower:
        return "incident"
    elif "ticket" in path_lower:
        return "historical_ticket"
    elif "troubleshoot" in path_lower:
        return "troubleshooting"
    else:
        return "general"


def load_document(file_path: str) -> Optional[Document]:
    """
    Load a single document from the filesystem.
    
    Returns None if file cannot be loaded (with warning logged).
    """
    path = Path(file_path)
    
    if not path.exists():
        # TODO: Log warning
        print(f"Warning: File not found: {file_path}")
        return None
    
    try:
        suffix = path.suffix.lower()
        
        if suffix in [".md", ".txt"]:
            content = path.read_text(encoding="utf-8")
        elif suffix == ".json":
            # For JSON, extract text content
            data = json.loads(path.read_text(encoding="utf-8"))
            # Assume JSON has a "content" or "text" field, or stringify it
            if isinstance(data, dict):
                content = data.get("content") or data.get("text") or json.dumps(data, indent=2)
            else:
                content = json.dumps(data, indent=2)
        else:
            # Skip unsupported formats
            # TODO: Log warning
            print(f"Warning: Unsupported format: {file_path}")
            return None
        
        # Skip empty files
        if not content.strip():
            return None
        
        return Document(
            content=content,
            source=str(path.absolute()),
            filename=path.name,
            doc_type=infer_doc_type(str(path)),
            metadata={
                "ingested_at": datetime.utcnow().isoformat(),
                "file_size_bytes": path.stat().st_size,
            }
        )
        
    except Exception as e:
        # TODO: Log error properly
        print(f"Error loading {file_path}: {e}")
        return None


def load_documents_from_directory(
    directory: str,
    recursive: bool = True,
    extensions: List[str] = None,
) -> List[Document]:
    """
    Load all documents from a directory.
    
    Args:
        directory: Path to the documents directory
        recursive: Whether to search subdirectories
        extensions: File extensions to include (default: .md, .txt, .json)
    
    Returns:
        List of loaded documents with metadata
    
    WHY RECURSIVE BY DEFAULT:
    - Documents are organized in subdirectories by type
    - api_docs/, runbooks/, etc. should all be included
    """
    if extensions is None:
        extensions = [".md", ".txt", ".json"]
    
    documents = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise ValueError(f"Documents directory not found: {directory}")
    
    # Find all matching files
    pattern = "**/*" if recursive else "*"
    for path in dir_path.glob(pattern):
        if path.is_file() and path.suffix.lower() in extensions:
            doc = load_document(str(path))
            if doc:
                documents.append(doc)
    
    return documents


class DocumentIngestionPipeline:
    """
    Pipeline for ingesting documents into the RAG system.
    
    RESPONSIBILITIES:
    - Load documents from filesystem
    - Validate document content
    - Track ingestion metrics
    
    DOES NOT:
    - Chunk documents (see chunking.py)
    - Embed documents (see embeddings.py)
    - Store documents (see store.py)
    """
    
    def __init__(self, documents_dir: str = None):
        """
        Initialize the ingestion pipeline.
        
        Args:
            documents_dir: Path to documents. Defaults to /data/documents
        """
        if documents_dir is None:
            # Default to project's data/documents directory
            documents_dir = str(Path(__file__).parent.parent.parent.parent / "data" / "documents")
        
        self.documents_dir = documents_dir
        self.ingestion_stats = {
            "total_files": 0,
            "loaded_files": 0,
            "skipped_files": 0,
            "total_characters": 0,
        }
    
    def ingest(self, extensions: List[str] = None) -> List[Document]:
        """
        Load all documents from the configured directory.
        
        Returns:
            List of Document objects ready for chunking
        """
        documents = load_documents_from_directory(
            self.documents_dir,
            recursive=True,
            extensions=extensions,
        )
        
        # Update stats
        self.ingestion_stats["loaded_files"] = len(documents)
        self.ingestion_stats["total_characters"] = sum(len(d.content) for d in documents)
        
        # TODO: Log ingestion stats
        # TODO: Emit metrics for observability
        
        return documents
    
    def get_stats(self) -> Dict[str, Any]:
        """Return ingestion statistics."""
        return self.ingestion_stats.copy()
