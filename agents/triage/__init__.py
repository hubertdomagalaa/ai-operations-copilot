"""
Triage Agent
============

Classifies and prioritizes incoming support tickets.

RESPONSIBILITY:
This agent is the FIRST to process a ticket. It must:
1. Classify the ticket into a category
2. Assign severity level (P1-P4)
3. Extract technical signals and keywords
4. Detect if escalation is needed
5. Provide grounded reasoning for all decisions

INPUT:
- Normalized ticket data from state["ticket_data"]

OUTPUT:
- TriageOutput schema (category, severity, confidence, reasoning, etc.)

TRIGGERS HUMAN REVIEW WHEN:
- Confidence is below 0.7
- Any escalation trigger applies
- Ticket mentions security, data loss, production outage
"""

import json
from typing import Dict, Any, List

from agents.base import BaseAgent
from agents.triage.schema import (
    TriageOutput,
    CONFIDENCE_THRESHOLD,
    ESCALATION_KEYWORDS,
)
from agents.triage.prompts import SYSTEM_PROMPT, build_user_prompt, PROMPT_VERSION


class TriageAgent(BaseAgent):
    """
    Agent responsible for ticket classification and prioritization.
    
    This is the first intelligence step in the workflow.
    Its outputs directly influence KnowledgeAgent, DecisionAgent, and ActionAgent.
    """
    
    def __init__(self, llm_service=None):
        """
        Initialize the TriageAgent.
        
        Args:
            llm_service: LLM service instance. If None, will be fetched on first use.
        """
        super().__init__(agent_type="triage")
        
        self._llm_service = llm_service
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.escalation_keywords = ESCALATION_KEYWORDS
        self.prompt_version = PROMPT_VERSION
    
    @property
    def llm_service(self):
        """Lazy-load LLM service."""
        if self._llm_service is None:
            from backend.services.llm import get_llm_service
            self._llm_service = get_llm_service()
        return self._llm_service
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify and prioritize the ticket.
        
        Args:
            state: Workflow state containing ticket_data
            
        Returns:
            Agent output dictionary with triage results
        """
        # Extract ticket data from state
        ticket_data = state.get("ticket_data", {})
        if not ticket_data:
            return self._create_error_output("No ticket data provided in state")
        
        ticket_id = ticket_data.get("ticket_id", "unknown")
        
        # Build the user prompt with ticket data
        user_prompt = build_user_prompt(ticket_data)
        
        try:
            # Call LLM with structured output
            response = await self.llm_service.generate_structured(
                prompt=user_prompt,
                output_schema=TriageOutput,
                system_prompt=SYSTEM_PROMPT,
            )
            
            # Parse the structured output
            triage_output = self._parse_llm_response(response, ticket_id)
            
            # Apply post-processing rules
            triage_output = self._apply_escalation_rules(triage_output, ticket_data)
            
            # Determine if human review is required
            requires_human_review = self._requires_human_review(triage_output)
            human_review_reason = self._get_human_review_reason(triage_output)
            
            # Create the agent output
            # Include metadata in result since BaseAgent doesn't support metadata param
            result_with_meta = triage_output.to_dict()
            result_with_meta["_metadata"] = {
                "prompt_version": self.prompt_version,
                "ticket_id": ticket_id,
            }
            
            return self._create_output(
                result=result_with_meta,
                confidence=triage_output.confidence,
                reasoning=triage_output.reasoning.category_rationale,
                requires_human_review=requires_human_review,
                human_review_reason=human_review_reason,
                sources=[],  # Triage has no external sources
            )
            
        except json.JSONDecodeError as e:
            return self._create_error_output(
                f"LLM produced invalid JSON: {str(e)}",
                ticket_id=ticket_id,
                requires_escalation=True,
            )
        except Exception as e:
            return self._create_error_output(
                f"Triage processing failed: {str(e)}",
                ticket_id=ticket_id,
                requires_escalation=True,
            )
    
    def _parse_llm_response(self, response, ticket_id: str) -> TriageOutput:
        """
        Parse LLM response into TriageOutput.
        
        Args:
            response: LLM response object
            ticket_id: Ticket identifier for validation
            
        Returns:
            Validated TriageOutput instance
        """
        # If response already has structured_output, use it
        if hasattr(response, 'structured_output') and response.structured_output:
            output = TriageOutput.model_validate(response.structured_output)
        else:
            # Parse from content string
            content = response.content if hasattr(response, 'content') else str(response)
            data = json.loads(content)
            output = TriageOutput.model_validate(data)
        
        # Verify ticket_id matches
        if output.ticket_id != ticket_id:
            output.ticket_id = ticket_id
        
        return output
    
    def _apply_escalation_rules(
        self, 
        triage_output: TriageOutput, 
        ticket_data: Dict[str, Any]
    ) -> TriageOutput:
        """
        Apply additional escalation rules post-LLM.
        
        This ensures safety rules are enforced even if LLM misses them.
        
        Args:
            triage_output: Parsed triage output
            ticket_data: Original ticket data
            
        Returns:
            Updated triage output with escalation rules applied
        """
        escalation_reasons = list(triage_output.escalation_reasons)
        requires_escalation = triage_output.requires_escalation
        
        # Rule: Confidence below threshold triggers escalation
        if triage_output.confidence < self.confidence_threshold:
            if "Low confidence score" not in escalation_reasons:
                escalation_reasons.append("Low confidence score")
            requires_escalation = True
        
        # Rule: P1 severity triggers escalation
        if triage_output.severity == "P1":
            if "Severity P1" not in escalation_reasons:
                escalation_reasons.append("Severity P1")
            requires_escalation = True
        
        # Rule: Check ticket text for escalation keywords
        ticket_text = self._get_ticket_text(ticket_data).lower()
        for keyword in self.escalation_keywords:
            if keyword.lower() in ticket_text:
                reason = f"Contains keyword: {keyword}"
                if reason not in escalation_reasons:
                    escalation_reasons.append(reason)
                requires_escalation = True
                break  # Only add one keyword-based reason
        
        # Update output if changes needed
        if requires_escalation != triage_output.requires_escalation or \
           escalation_reasons != list(triage_output.escalation_reasons):
            # Create updated output
            data = triage_output.model_dump()
            data["requires_escalation"] = requires_escalation
            data["escalation_reasons"] = escalation_reasons
            return TriageOutput.model_validate(data)
        
        return triage_output
    
    def _get_ticket_text(self, ticket_data: Dict[str, Any]) -> str:
        """
        Extract searchable text from ticket data.
        
        Args:
            ticket_data: Normalized ticket dictionary
            
        Returns:
            Combined text from relevant fields
        """
        parts = [
            ticket_data.get("summary", ""),
            " ".join(ticket_data.get("symptoms", [])),
            ticket_data.get("suspected_root_cause", ""),
            " ".join(ticket_data.get("affected_components", [])),
        ]
        return " ".join(str(p) for p in parts if p)
    
    def _requires_human_review(self, triage_output: TriageOutput) -> bool:
        """
        Determine if human review is required.
        
        Args:
            triage_output: Processed triage output
            
        Returns:
            True if human review is required
        """
        # Escalation always means human review
        if triage_output.requires_escalation:
            return True
        
        # Low confidence means human review
        if triage_output.confidence < self.confidence_threshold:
            return True
        
        # Incident type always gets reviewed
        if triage_output.issue_type == "incident":
            return True
        
        return False
    
    def _get_human_review_reason(self, triage_output: TriageOutput) -> str:
        """
        Get the reason for human review.
        
        Args:
            triage_output: Processed triage output
            
        Returns:
            Human-readable reason string, or None if no review needed
        """
        if triage_output.requires_escalation and triage_output.escalation_reasons:
            return f"Escalation triggered: {', '.join(triage_output.escalation_reasons[:3])}"
        
        if triage_output.confidence < self.confidence_threshold:
            return f"Low confidence ({triage_output.confidence:.2f})"
        
        if triage_output.issue_type == "incident":
            return "Issue type is incident"
        
        return None
    
    def _create_error_output(
        self, 
        error_message: str, 
        ticket_id: str = "unknown",
        requires_escalation: bool = True,
    ) -> Dict[str, Any]:
        """
        Create an error output when processing fails.
        
        Args:
            error_message: Description of the error
            ticket_id: Ticket identifier
            requires_escalation: Whether to escalate (default True for errors)
            
        Returns:
            Agent output dictionary indicating failure
        """
        return self._create_output(
            result={
                "error": error_message,
                "ticket_id": ticket_id,
                "_metadata": {
                    "prompt_version": self.prompt_version,
                    "requires_escalation": requires_escalation,
                }
            },
            confidence=0.0,
            reasoning=f"Processing failed: {error_message}",
            requires_human_review=True,
            human_review_reason=f"Error: {error_message}",
            sources=[],
        )
