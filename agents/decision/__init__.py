"""
Decision Agent
==============

Synthesizes signals from triage and knowledge to produce structured recommendations.

WHY THIS AGENT EXISTS:
- Combines classification signals with retrieved knowledge
- Produces a grounded recommendation for human review
- Enforces human-in-the-loop before any action execution
- Explicitly communicates uncertainty and trade-offs

CORE PRINCIPLE:
This agent is DECISION SUPPORT, not DECISION MAKING.
It recommends; humans decide. It NEVER executes actions.

STRICT BOUNDARIES:
- DOES NOT execute actions
- DOES NOT modify external systems
- DOES NOT generate final customer responses
- ONLY produces structured recommendations
- ONLY flags cases requiring human review

DECISION LOGIC:
- If triage confidence < 0.6 → require human approval
- If no documents retrieved → require human approval
- If retrieved sources are low relevance → require human approval
- Always err on the side of safety

INPUT (from workflow state):
- ticket_data: Original ticket content
- triage_output: Classification, severity, confidence
- knowledge_output: Retrieved documents with citations
- retrieved_documents: Extracted documents list

OUTPUT:
- recommended_action: auto_respond | escalate | manual_review
- reasoning_summary: Short, factual explanation
- confidence: 0.0 - 1.0
- risk_flags: List of identified risks
- requires_human_approval: Boolean
"""

from typing import Dict, Any, List, Literal, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time

from agents.base import BaseAgent


# === Output Schema ===

@dataclass
class DecisionOutput:
    """
    Structured output from the DecisionAgent.
    
    This schema defines exactly what downstream systems can expect.
    """
    
    recommended_action: Literal["auto_respond", "escalate", "manual_review"]
    """
    The recommended operational path:
    - auto_respond: Can be handled with standard response template
    - escalate: Needs engineering or specialist attention
    - manual_review: Operator should handle directly
    """
    
    reasoning_summary: str
    """
    Short, factual explanation grounded in retrieved sources.
    Example: "API authentication issue. Found matching runbook for 401 errors."
    """
    
    confidence: float
    """0.0 to 1.0. Based on triage confidence and retrieval quality."""
    
    risk_flags: List[str] = field(default_factory=list)
    """
    Identified risks that inform the requires_human_approval decision.
    Examples:
    - "low_triage_confidence"
    - "no_documents_retrieved"
    - "conflicting_sources"
    - "high_severity_ticket"
    """
    
    requires_human_approval: bool = True
    """
    WHY DEFAULT IS TRUE:
    We err on the side of safety. The agent must explicitly determine
    that a case is low-risk and high-confidence to NOT require approval.
    """
    
    sources_used: List[str] = field(default_factory=list)
    """Filenames of documents that informed this decision."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for state storage."""
        return {
            "recommended_action": self.recommended_action,
            "reasoning_summary": self.reasoning_summary,
            "confidence": self.confidence,
            "risk_flags": self.risk_flags,
            "requires_human_approval": self.requires_human_approval,
            "sources_used": self.sources_used,
        }


# === Decision Thresholds ===

TRIAGE_CONFIDENCE_THRESHOLD = 0.6
"""Below this, triage is uncertain and human review is required."""

RETRIEVAL_SCORE_THRESHOLD = 0.3
"""Below this, retrieved documents are not relevant enough."""

AUTO_APPROVE_CONFIDENCE_THRESHOLD = 0.85
"""
Above this AND with no risk flags, decision could theoretically auto-approve.
However, we currently require human approval for all actions as a safety measure.
"""


class DecisionAgent(BaseAgent):
    """
    Decision-support agent that synthesizes signals and recommends actions.
    
    This agent does NOT execute anything. It produces structured recommendations
    that must be reviewed by a human operator before any action is taken.
    """
    
    def __init__(self):
        super().__init__(agent_type="decision")
        
        # Thresholds (can be configured)
        self.triage_confidence_threshold = TRIAGE_CONFIDENCE_THRESHOLD
        self.retrieval_score_threshold = RETRIEVAL_SCORE_THRESHOLD
        self.auto_approve_threshold = AUTO_APPROVE_CONFIDENCE_THRESHOLD
        
        # Severities that always require human review
        self.high_risk_severities = ["critical", "high"]
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce a structured recommendation based on prior agent outputs.
        
        Steps:
        1. Extract inputs from state
        2. Analyze signals (triage + knowledge)
        3. Identify risk flags
        4. Determine recommended action
        5. Calculate confidence
        6. Determine if human approval needed
        7. Return structured output
        """
        start_time = time.time()
        
        # === 1. Extract Inputs ===
        ticket_data = state.get("ticket_data", {})
        triage_output = state.get("triage_output") or {}
        knowledge_output = state.get("knowledge_output") or {}
        retrieved_documents = state.get("retrieved_documents") or []
        
        # Extract key signals
        triage_result = triage_output.get("result", {})
        triage_confidence = triage_output.get("confidence", 0.0)
        ticket_severity = triage_result.get("severity", "medium")
        ticket_type = triage_result.get("ticket_type", "question")
        
        knowledge_result = knowledge_output.get("result", {})
        knowledge_confidence = knowledge_output.get("confidence", 0.0)
        
        # === 2. Identify Risk Flags ===
        risk_flags = self._identify_risk_flags(
            triage_confidence=triage_confidence,
            knowledge_confidence=knowledge_confidence,
            ticket_severity=ticket_severity,
            retrieved_documents=retrieved_documents,
        )
        
        # === 3. Determine Recommended Action ===
        recommended_action = self._determine_action(
            ticket_type=ticket_type,
            ticket_severity=ticket_severity,
            triage_confidence=triage_confidence,
            knowledge_confidence=knowledge_confidence,
            has_documents=len(retrieved_documents) > 0,
            risk_flags=risk_flags,
        )
        
        # === 4. Calculate Overall Confidence ===
        confidence = self._calculate_confidence(
            triage_confidence=triage_confidence,
            knowledge_confidence=knowledge_confidence,
            risk_flags=risk_flags,
        )
        
        # === 5. Determine Human Approval Requirement ===
        requires_human_approval = self._requires_human_approval(
            confidence=confidence,
            risk_flags=risk_flags,
            recommended_action=recommended_action,
        )
        
        # === 6. Build Reasoning Summary ===
        reasoning_summary = self._build_reasoning_summary(
            ticket_type=ticket_type,
            ticket_severity=ticket_severity,
            recommended_action=recommended_action,
            retrieved_documents=retrieved_documents,
            risk_flags=risk_flags,
        )
        
        # === 7. Collect Sources ===
        sources_used = list(set(
            doc.get("filename", "unknown")
            for doc in retrieved_documents
            if doc.get("filename")
        ))
        
        # === Create Output ===
        decision = DecisionOutput(
            recommended_action=recommended_action,
            reasoning_summary=reasoning_summary,
            confidence=confidence,
            risk_flags=risk_flags,
            requires_human_approval=requires_human_approval,
            sources_used=sources_used,
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # === Return Agent Output ===
        output = self._create_output(
            result=decision.to_dict(),
            confidence=confidence,
            reasoning=reasoning_summary,
            requires_human_review=requires_human_approval,
            human_review_reason="Human approval required for all operational decisions" if requires_human_approval else None,
            sources=sources_used,
        )
        
        output["processing_time_ms"] = elapsed_ms
        
        # TODO: Log decision metrics for observability
        # TODO: Emit evaluation event for calibration
        
        return output
    
    def _identify_risk_flags(
        self,
        triage_confidence: float,
        knowledge_confidence: float,
        ticket_severity: str,
        retrieved_documents: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Identify risk factors that inform the human approval decision.
        
        WHY THIS MATTERS:
        - Explicit risk flags make decisions auditable
        - Operators can quickly see why approval is needed
        - Enables evaluation of risk detection accuracy
        """
        flags = []
        
        # Low triage confidence
        if triage_confidence < self.triage_confidence_threshold:
            flags.append("low_triage_confidence")
        
        # No documents retrieved
        if not retrieved_documents:
            flags.append("no_documents_retrieved")
        
        # Low retrieval quality
        elif knowledge_confidence < self.retrieval_score_threshold:
            flags.append("low_retrieval_confidence")
        
        # High severity ticket
        if ticket_severity in self.high_risk_severities:
            flags.append("high_severity_ticket")
        
        # Check for low-scoring retrieved documents
        if retrieved_documents:
            avg_score = sum(doc.get("score", 0) for doc in retrieved_documents) / len(retrieved_documents)
            if avg_score < self.retrieval_score_threshold:
                flags.append("low_relevance_documents")
        
        return flags
    
    def _determine_action(
        self,
        ticket_type: str,
        ticket_severity: str,
        triage_confidence: float,
        knowledge_confidence: float,
        has_documents: bool,
        risk_flags: List[str],
    ) -> Literal["auto_respond", "escalate", "manual_review"]:
        """
        Determine the recommended operational path.
        
        DECISION LOGIC:
        1. Critical/high severity → escalate
        2. No documents and not simple question → manual_review
        3. Low confidence → manual_review
        4. Good confidence with documents → auto_respond candidate
        """
        # High severity always escalates
        if ticket_severity in ["critical", "high"]:
            return "escalate"
        
        # Many risk flags → manual review
        if len(risk_flags) >= 2:
            return "manual_review"
        
        # No grounding → manual review
        if not has_documents:
            return "manual_review"
        
        # Low confidence → manual review
        if triage_confidence < self.triage_confidence_threshold:
            return "manual_review"
        
        # Reasonable confidence with documents → could auto-respond
        if triage_confidence >= 0.7 and knowledge_confidence >= 0.5:
            return "auto_respond"
        
        # Default to manual review (safety)
        return "manual_review"
    
    def _calculate_confidence(
        self,
        triage_confidence: float,
        knowledge_confidence: float,
        risk_flags: List[str],
    ) -> float:
        """
        Calculate overall decision confidence.
        
        Combines triage and knowledge confidence with risk penalty.
        """
        # Base: weighted average of upstream confidences
        # Triage matters slightly more for classification
        base_confidence = (
            0.4 * triage_confidence +
            0.4 * knowledge_confidence +
            0.2  # Base score
        )
        
        # Penalty for risk flags
        risk_penalty = 0.1 * len(risk_flags)
        
        confidence = max(0.0, min(1.0, base_confidence - risk_penalty))
        
        return round(confidence, 3)
    
    def _requires_human_approval(
        self,
        confidence: float,
        risk_flags: List[str],
        recommended_action: str,
    ) -> bool:
        """
        Determine if human approval is required.
        
        WHY ALMOST ALWAYS TRUE:
        - This is a human-in-the-loop system
        - AI assists, does not replace human judgment
        - Any risk flag means human must review
        - Only theoretical path to auto-approve is high confidence + no risks
        
        CURRENTLY:
        We require human approval for all decisions.
        This can be relaxed in future with explicit configuration.
        """
        # Any risk flag → require approval
        if risk_flags:
            return True
        
        # Low confidence → require approval
        if confidence < self.auto_approve_threshold:
            return True
        
        # Escalation always requires approval
        if recommended_action == "escalate":
            return True
        
        # SAFETY: Even if all checks pass, we still require approval
        # This is a human-in-the-loop system by design
        # TODO: Add configuration flag to enable auto-approval for very safe cases
        return True
    
    def _build_reasoning_summary(
        self,
        ticket_type: str,
        ticket_severity: str,
        recommended_action: str,
        retrieved_documents: List[Dict[str, Any]],
        risk_flags: List[str],
    ) -> str:
        """
        Build a short, factual reasoning summary.
        
        This is for human operators to quickly understand the decision.
        """
        parts = []
        
        # Ticket classification
        parts.append(f"{ticket_severity.capitalize()} {ticket_type}.")
        
        # Document status
        if retrieved_documents:
            doc_count = len(retrieved_documents)
            sources = list(set(d.get("filename", "") for d in retrieved_documents[:3]))
            parts.append(f"Found {doc_count} relevant document(s): {', '.join(sources)}.")
        else:
            parts.append("No relevant documents found.")
        
        # Recommendation
        action_desc = {
            "auto_respond": "Standard response recommended.",
            "escalate": "Escalation to specialist recommended.",
            "manual_review": "Manual operator review recommended.",
        }
        parts.append(action_desc.get(recommended_action, ""))
        
        # Risk flags
        if risk_flags:
            parts.append(f"Flags: {', '.join(risk_flags)}.")
        
        return " ".join(parts)
