"""
Triage Agent
============

Classifies and prioritizes incoming support tickets.

RESPONSIBILITY:
This agent is the FIRST to process a ticket. It must:
1. Classify the ticket into a category (authentication, API error, etc.)
2. Assign priority level (critical, high, medium, low)
3. Extract key information and keywords
4. Detect if immediate escalation is needed

INPUT:
- Raw ticket content (subject, body, metadata)

OUTPUT:
- Category with confidence
- Priority with confidence
- Summary and keywords
- Escalation flag if needed

TRIGGERS HUMAN REVIEW WHEN:
- Classification confidence is below threshold
- Ticket mentions critical keywords (outage, security, etc.)
- Ambiguous ticket that could be multiple categories
"""

from typing import Dict, Any
from agents.base import BaseAgent


class TriageAgent(BaseAgent):
    """
    Agent responsible for ticket classification and prioritization.
    """
    
    def __init__(self):
        super().__init__(agent_type="triage")
        
        # Classification confidence threshold
        self.confidence_threshold = 0.7
        
        # Keywords that trigger immediate escalation
        self.escalation_keywords = [
            "outage", "down", "security", "breach", "critical",
            "production", "data loss", "urgent"
        ]
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify and prioritize the ticket.
        
        TODO: Implement classification logic using LLM
        
        Steps:
        1. Extract ticket content from state
        2. Prompt LLM for classification
        3. Parse structured output
        4. Check for escalation keywords
        5. Return classification result
        """
        # TODO: Get ticket content from state
        # ticket_data = state.get("ticket_data", {})
        
        # TODO: Build classification prompt
        # prompt = self._build_classification_prompt(ticket_data)
        
        # TODO: Call LLM service
        # from backend.services.llm import get_llm_service
        # llm = get_llm_service()
        # response = await llm.generate_structured(prompt, ClassificationSchema)
        
        # TODO: Check for escalation keywords
        # requires_escalation = self._check_escalation(ticket_data)
        
        # TODO: Return formatted output
        # return self._create_output(
        #     result={
        #         "category": response.category,
        #         "priority": response.priority,
        #         "summary": response.summary,
        #         "keywords": response.keywords,
        #     },
        #     confidence=response.confidence,
        #     reasoning="Classified based on ticket content analysis",
        #     requires_human_review=response.confidence < self.confidence_threshold,
        # )
        
        raise NotImplementedError("Triage agent not implemented")
    
    def _build_classification_prompt(self, ticket_data: Dict[str, Any]) -> str:
        """
        Build the prompt for ticket classification.
        
        TODO: Design the classification prompt
        """
        # TODO: Implement prompt construction
        pass
    
    def _check_escalation(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Check if ticket contains escalation keywords.
        
        TODO: Implement keyword detection
        """
        # TODO: Check subject and body for keywords
        pass
