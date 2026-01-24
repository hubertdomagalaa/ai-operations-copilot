"""
Knowledge Agent
===============

Retrieves relevant context from internal documentation via RAG.

RESPONSIBILITY:
This agent uses the RAG pipeline to find relevant information. It:
1. Extracts search context from ticket and triage output
2. Queries the RAG pipeline for relevant documents
3. Attaches retrieved documents and citations to state
4. DOES NOT summarize, decide, or generate text

CORE PRINCIPLE:
No retrieval = no answer. This agent only returns grounded facts.

INPUT:
- ticket_data: Original ticket content
- triage_output: Classification, priority, keywords from triage

OUTPUT (attached to state):
- knowledge_output: Agent output with retrieved documents
- retrieved_documents: List of documents with citations

TRIGGERS HUMAN REVIEW WHEN:
- No relevant documents found (confidence = 0)
- Retrieved documents are low relevance
"""

from typing import Dict, Any, List
import time

from agents.base import BaseAgent
from backend.services.rag import RAGPipeline, RetrievalResult
from backend.services.rag.retrieval import get_rag_pipeline


class KnowledgeAgent(BaseAgent):
    """
    Agent responsible for knowledge retrieval via RAG.
    
    This agent is RETRIEVAL ONLY. It never:
    - Summarizes content
    - Makes decisions
    - Generates user-facing text
    - Modifies retrieved content
    """
    
    def __init__(
        self,
        rag_pipeline: RAGPipeline = None,
        max_documents: int = 5,
        min_relevance_score: float = 0.1,
        low_confidence_threshold: float = 0.3,
    ):
        """
        Initialize the Knowledge Agent.
        
        Args:
            rag_pipeline: RAG pipeline instance (uses default if None)
            max_documents: Maximum documents to retrieve
            min_relevance_score: Minimum score to include document
            low_confidence_threshold: Score below which to flag for review
        """
        super().__init__(agent_type="knowledge")
        
        self._rag_pipeline = rag_pipeline or get_rag_pipeline()
        self.max_documents = max_documents
        self.min_relevance_score = min_relevance_score
        self.low_confidence_threshold = low_confidence_threshold
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge for the ticket.
        
        Steps:
        1. Extract ticket content and triage output from state
        2. Query RAG pipeline for relevant documents
        3. Calculate retrieval confidence
        4. Format output with citations
        5. Return output (DO NOT modify state directly)
        """
        start_time = time.time()
        
        # Extract inputs from state
        ticket_data = state.get("ticket_data", {})
        triage_output = state.get("triage_output")
        
        # Retrieve documents using RAG pipeline
        results = await self._rag_pipeline.retrieve_for_ticket(
            ticket_data=ticket_data,
            triage_output=triage_output,
            k=self.max_documents,
        )
        
        # Filter by minimum score
        filtered_results = [r for r in results if r.score >= self.min_relevance_score]
        
        # Calculate confidence based on retrieval quality
        confidence = self._calculate_confidence(filtered_results)
        
        # Determine if human review needed
        needs_human_review = False
        human_review_reason = None
        
        if not filtered_results:
            needs_human_review = True
            human_review_reason = "No relevant documents found for this ticket"
        elif confidence < self.low_confidence_threshold:
            needs_human_review = True
            human_review_reason = f"Low retrieval confidence ({confidence:.2f})"
        
        # Format documents for state
        retrieved_documents = [r.to_dict() for r in filtered_results]
        
        # Build formatted context with citations
        formatted_context = self._format_context(filtered_results)
        
        # Calculate timing
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Create agent output
        output = self._create_output(
            result={
                "documents": retrieved_documents,
                "document_count": len(filtered_results),
                "context": formatted_context,
                "queries_used": self._get_queries_used(ticket_data, triage_output),
            },
            confidence=confidence,
            reasoning=self._build_reasoning(filtered_results),
            requires_human_review=needs_human_review,
            human_review_reason=human_review_reason,
            sources=[r.filename for r in filtered_results],
        )
        
        # Add processing time
        output["processing_time_ms"] = elapsed_ms
        
        # TODO: Log retrieval metrics
        # TODO: Emit observability events
        
        return output
    
    def _calculate_confidence(self, results: List[RetrievalResult]) -> float:
        """
        Calculate confidence score based on retrieval quality.
        
        Confidence is based on:
        - Number of documents retrieved
        - Average relevance score
        - Score of top document
        
        Returns value 0.0 to 1.0
        """
        if not results:
            return 0.0
        
        # Weight factors
        # - 40% based on top score (best match quality)
        # - 40% based on average score (overall relevance)
        # - 20% based on document count (coverage)
        
        top_score = results[0].score
        avg_score = sum(r.score for r in results) / len(results)
        count_factor = min(len(results) / self.max_documents, 1.0)
        
        confidence = (
            0.4 * top_score +
            0.4 * avg_score +
            0.2 * count_factor
        )
        
        return round(confidence, 3)
    
    def _format_context(self, results: List[RetrievalResult]) -> str:
        """
        Format retrieved documents as context string.
        
        Each document is labeled with its citation for grounding.
        This context can be passed to downstream agents.
        """
        if not results:
            return "No relevant documents found."
        
        parts = []
        for i, r in enumerate(results, 1):
            citation = r.to_citation()
            parts.append(f"--- Document {i} {citation} ---\n{r.content}\n")
        
        return "\n".join(parts)
    
    def _build_reasoning(self, results: List[RetrievalResult]) -> str:
        """Build reasoning explanation for the output."""
        if not results:
            return "No documents matched the search queries."
        
        top_score = results[0].score
        sources = list(set(r.filename for r in results))
        
        return (
            f"Retrieved {len(results)} documents from {len(sources)} sources. "
            f"Top relevance score: {top_score:.2f}. "
            f"Sources: {', '.join(sources[:3])}{'...' if len(sources) > 3 else ''}"
        )
    
    def _get_queries_used(
        self,
        ticket_data: Dict[str, Any],
        triage_output: Dict[str, Any] = None,
    ) -> List[str]:
        """Get the queries that were used for retrieval."""
        queries = []
        
        if ticket_data.get("subject"):
            queries.append(f"subject: {ticket_data['subject'][:50]}...")
        if ticket_data.get("body"):
            queries.append(f"body excerpt: {ticket_data['body'][:50]}...")
        if triage_output:
            keywords = triage_output.get("result", {}).get("keywords", [])
            if keywords:
                queries.append(f"keywords: {', '.join(keywords[:5])}")
        
        return queries
