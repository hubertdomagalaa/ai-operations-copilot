"""
Action Agent
=============

Prepares draft responses and action checklists after human approval.

WHY THIS AGENT EXISTS:
- Separates decision-making from drafting
- Ensures human approval gates all action preparation
- Provides grounded, reviewable artifacts for operators
- Never executes anything — only prepares drafts

CORE PRINCIPLE:
This agent PREPARES actions, it does NOT EXECUTE them.
It operates ONLY after explicit human approval.

STRICT BOUNDARIES:
- DOES NOT execute external API calls
- DOES NOT modify any systems
- DOES NOT perform autonomous actions
- ONLY produces draft responses
- ONLY produces action checklists
- ONLY prepares execution-ready artifacts for humans

PRECONDITIONS (checked before running):
- DecisionAgent requires_human_approval == False
  OR
- Human approval status == "approved"
If approval is missing or denied, this agent MUST NOT run.

INPUT (from workflow state):
- ticket_data: Original ticket content
- decision_output: Recommendation from DecisionAgent
- human_decision: Human's approval/modifications
- knowledge_output: Retrieved documents with citations
- retrieved_documents: Document list for grounding

OUTPUT:
- action_type: draft_response | engineer_checklist
- content: The draft text or checklist items
- grounding_sources: Document references used
- confidence: Quality score 0.0 - 1.0
- disclaimers: Limitations or assumptions
"""

from typing import Dict, Any, List, Literal, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time

from agents.base import BaseAgent


# === Output Schema ===

@dataclass
class ActionOutput:
    """
    Structured output from the ActionAgent.
    
    This is what human operators see as the prepared artifact.
    """
    
    action_type: Literal["draft_response", "engineer_checklist"]
    """
    Type of prepared action:
    - draft_response: Customer-facing response draft
    - engineer_checklist: Step-by-step checklist for specialists
    """
    
    content: str
    """
    The prepared content:
    - For draft_response: Polite, factual, non-committal text
    - For engineer_checklist: Numbered actionable steps
    """
    
    grounding_sources: List[str] = field(default_factory=list)
    """
    Document references that informed this draft.
    Enables traceability and fact-checking.
    """
    
    confidence: float = 0.0
    """
    Quality confidence 0.0 - 1.0.
    Based on retrieval quality and template coverage.
    """
    
    disclaimers: List[str] = field(default_factory=list)
    """
    Limitations or assumptions made during drafting.
    Examples:
    - "No specific runbook found for this error"
    - "Response based on general authentication docs"
    """
    
    is_draft: bool = True
    """Always True - marks content as requiring human review."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for state storage."""
        return {
            "action_type": self.action_type,
            "content": self.content,
            "grounding_sources": self.grounding_sources,
            "confidence": self.confidence,
            "disclaimers": self.disclaimers,
            "is_draft": self.is_draft,
        }


class ActionAgent(BaseAgent):
    """
    Agent that prepares draft responses and action checklists.
    
    This agent operates ONLY after human approval.
    It NEVER executes actions — only prepares drafts.
    
    WHY DRAFTING IS SEPARATE FROM DECISION-MAKING:
    1. Clear separation of concerns
    2. Decision can be approved before drafting begins
    3. Human can review and modify recommendation before content is generated
    4. Drafting quality metrics are separate from decision quality
    """
    
    def __init__(self):
        super().__init__(agent_type="action")
        
        # Draft templates (simple, no LLM for now)
        self.response_template = self._get_response_template()
        self.checklist_template = self._get_checklist_template()
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare draft response or action checklist.
        
        PRECONDITION: Human approval must be present.
        If approval is missing, this method raises an error.
        
        Steps:
        1. Validate approval status
        2. Extract inputs from state
        3. Determine action type from decision
        4. Generate appropriate draft
        5. Attach grounding sources
        6. Return structured output
        """
        start_time = time.time()
        
        # === 1. Validate Approval Status ===
        # This is a critical safety check
        if not self._is_approved(state):
            raise RuntimeError(
                "ActionAgent cannot run without human approval. "
                "This is a safety violation."
            )
        
        # === 2. Extract Inputs ===
        ticket_data = state.get("ticket_data", {})
        decision_output = state.get("decision_output") or {}
        human_decision = state.get("human_decision") or {}
        knowledge_output = state.get("knowledge_output") or {}
        retrieved_documents = state.get("retrieved_documents") or []
        
        # Use human-modified decision if available
        effective_decision = human_decision if human_decision.get("action") else decision_output
        decision_result = decision_output.get("result", {})
        
        # === 3. Determine Action Type ===
        recommended_action = decision_result.get("recommended_action", "manual_review")
        action_type = self._determine_action_type(recommended_action)
        
        # === 4. Generate Draft ===
        if action_type == "draft_response":
            content, disclaimers = self._generate_response_draft(
                ticket_data=ticket_data,
                decision=decision_result,
                documents=retrieved_documents,
            )
        else:
            content, disclaimers = self._generate_engineer_checklist(
                ticket_data=ticket_data,
                decision=decision_result,
                documents=retrieved_documents,
            )
        
        # === 5. Collect Grounding Sources ===
        grounding_sources = list(set(
            doc.get("filename", "unknown")
            for doc in retrieved_documents
            if doc.get("filename")
        ))
        
        # === 6. Calculate Confidence ===
        confidence = self._calculate_confidence(
            documents=retrieved_documents,
            knowledge_confidence=knowledge_output.get("confidence", 0.0),
        )
        
        # === Create Output ===
        action_output = ActionOutput(
            action_type=action_type,
            content=content,
            grounding_sources=grounding_sources,
            confidence=confidence,
            disclaimers=disclaimers,
            is_draft=True,
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # === Return Agent Output ===
        output = self._create_output(
            result=action_output.to_dict(),
            confidence=confidence,
            reasoning=f"Prepared {action_type} based on approved decision",
            requires_human_review=True,  # Drafts always need review
            human_review_reason="Draft requires human review before sending",
            sources=grounding_sources,
        )
        
        output["processing_time_ms"] = elapsed_ms
        
        # TODO: Log drafting metrics for observability
        # TODO: Track token usage when LLM is integrated
        # TODO: Add hook for human quality scoring
        
        return output
    
    def _is_approved(self, state: Dict[str, Any]) -> bool:
        """
        Check if human approval is present.
        
        This is the critical safety gate for ActionAgent.
        
        Returns True if:
        - human_decision.action == "approve"
        - OR human_approval_status == "approved"
        """
        human_decision = state.get("human_decision") or {}
        human_approval_status = state.get("human_approval_status")
        
        # Check explicit approval
        if human_decision.get("action") == "approve":
            return True
        
        if human_approval_status == "approved":
            return True
        
        # Check decision_output for auto-approve (theoretical, not implemented)
        decision_output = state.get("decision_output") or {}
        if decision_output.get("requires_human_review") is False:
            # Even if decision says no review needed, we still require approval
            # This is a safety-first system
            return False
        
        return False
    
    def _determine_action_type(
        self,
        recommended_action: str,
    ) -> Literal["draft_response", "engineer_checklist"]:
        """
        Determine what type of artifact to prepare.
        
        - auto_respond → draft_response
        - escalate → engineer_checklist
        - manual_review → draft_response (default)
        """
        if recommended_action == "escalate":
            return "engineer_checklist"
        else:
            return "draft_response"
    
    def _generate_response_draft(
        self,
        ticket_data: Dict[str, Any],
        decision: Dict[str, Any],
        documents: List[Dict[str, Any]],
    ) -> tuple[str, List[str]]:
        """
        Generate a draft customer response.
        
        DRAFTING GUIDELINES:
        - Polite and professional
        - Factual, grounded in retrieved documents
        - Non-committal (no promises)
        - Clearly marked as draft
        
        TODO: Integrate LLM for more sophisticated drafting
        """
        disclaimers = []
        
        # Extract ticket info
        subject = ticket_data.get("subject", "your inquiry")
        ticket_type = decision.get("ticket_type", "question")
        
        # Build response parts
        greeting = "Thank you for contacting support."
        
        # Context from documents
        if documents:
            doc_count = len(documents)
            top_doc = documents[0] if documents else {}
            context_info = f"Based on our documentation, I can provide the following information."
            
            # Extract relevant content snippet
            top_content = top_doc.get("content", "")[:200] if top_doc else ""
            if top_content:
                context_info += f"\n\n{top_content}..."
        else:
            context_info = "I'm looking into this and will provide more details shortly."
            disclaimers.append("No specific documentation found for this issue")
        
        # Closing
        closing = (
            "\n\nPlease let me know if you need any additional clarification. "
            "A member of our team will follow up with you soon."
        )
        
        # Draft marker
        draft_marker = "\n\n---\n[DRAFT - REQUIRES HUMAN REVIEW BEFORE SENDING]"
        
        content = f"{greeting}\n\n{context_info}{closing}{draft_marker}"
        
        return content, disclaimers
    
    def _generate_engineer_checklist(
        self,
        ticket_data: Dict[str, Any],
        decision: Dict[str, Any],
        documents: List[Dict[str, Any]],
    ) -> tuple[str, List[str]]:
        """
        Generate an engineer checklist for escalation.
        
        CHECKLIST GUIDELINES:
        - Step-by-step format
        - Actionable items
        - No speculation
        - References to relevant documentation
        
        TODO: Integrate LLM for more sophisticated checklist generation
        """
        disclaimers = []
        
        # Extract ticket info
        subject = ticket_data.get("subject", "Unknown issue")
        body = ticket_data.get("body", "")[:200]
        severity = decision.get("severity", "medium")
        
        # Build checklist
        checklist_items = [
            f"## Engineer Escalation Checklist",
            f"",
            f"**Ticket Summary:** {subject}",
            f"**Severity:** {severity.upper()}",
            f"",
            f"### Investigation Steps:",
            f"",
            f"1. [ ] Review ticket details and reproduce issue if possible",
            f"2. [ ] Check system logs for related errors",
            f"3. [ ] Verify customer account status and permissions",
        ]
        
        # Add documentation references
        if documents:
            checklist_items.append(f"4. [ ] Review related documentation:")
            for i, doc in enumerate(documents[:3], start=1):
                filename = doc.get("filename", "unknown")
                checklist_items.append(f"   - {filename}")
            checklist_items.append(f"5. [ ] Apply relevant fix from runbook if available")
        else:
            checklist_items.append(f"4. [ ] Search internal docs for related issues")
            disclaimers.append("No relevant runbooks found")
        
        checklist_items.extend([
            f"6. [ ] Document findings and resolution",
            f"7. [ ] Update customer with resolution",
            f"",
            f"---",
            f"[CHECKLIST - GENERATED FOR ENGINEER REVIEW]",
        ])
        
        content = "\n".join(checklist_items)
        
        return content, disclaimers
    
    def _calculate_confidence(
        self,
        documents: List[Dict[str, Any]],
        knowledge_confidence: float,
    ) -> float:
        """
        Calculate confidence in the generated draft.
        
        Higher confidence when:
        - More relevant documents available
        - Higher knowledge retrieval confidence
        """
        # Base from knowledge confidence
        base = knowledge_confidence * 0.6
        
        # Bonus for having documents
        if documents:
            doc_bonus = min(0.3, len(documents) * 0.1)
            base += doc_bonus
        
        # Minimum floor
        base = max(0.2, base)
        
        return round(min(1.0, base), 3)
    
    def _get_response_template(self) -> str:
        """Base template for customer responses."""
        return """
Thank you for contacting support regarding {subject}.

{context}

Please let me know if you need any additional clarification.

Best regards,
Support Team

---
[DRAFT - REQUIRES HUMAN REVIEW BEFORE SENDING]
"""
    
    def _get_checklist_template(self) -> str:
        """Base template for engineer checklists."""
        return """
## Engineer Escalation Checklist

**Issue:** {subject}
**Severity:** {severity}

### Steps:
1. [ ] Review and reproduce
2. [ ] Check logs
3. [ ] Verify permissions
4. [ ] Apply fix
5. [ ] Document resolution

---
[CHECKLIST - FOR ENGINEER REVIEW]
"""
