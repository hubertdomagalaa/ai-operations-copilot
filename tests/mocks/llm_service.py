"""
Mock LLM Service for Dry Run Testing
=====================================

Provides deterministic LLM responses for workflow verification.
No real LLM calls are made.
"""

import json
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass


@dataclass
class MockLLMResponse:
    """Mock response matching LLMResponse interface."""
    content: str
    structured_output: Optional[Dict[str, Any]]
    input_tokens: int = 500
    output_tokens: int = 300
    total_tokens: int = 800
    model: str = "mock-model"
    provider: str = "mock"
    latency_ms: int = 100


class DryRunLLMService:
    """
    Deterministic LLM service for dry run testing.
    
    Returns pre-defined responses based on ticket characteristics.
    """
    
    def __init__(self, responses: Dict[str, Dict[str, Any]] = None):
        """
        Initialize with optional pre-defined responses.
        
        Args:
            responses: Dict mapping ticket_id to mock triage response
        """
        self.responses = responses or {}
        self.calls = []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> MockLLMResponse:
        """Return mock text response."""
        self.calls.append({"type": "generate", "prompt_length": len(prompt)})
        return MockLLMResponse(
            content="Mock response",
            structured_output=None
        )
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: Type,
        system_prompt: Optional[str] = None,
    ) -> MockLLMResponse:
        """Return mock structured response."""
        # Extract ticket_id from prompt
        ticket_id = self._extract_ticket_id(prompt)
        
        self.calls.append({
            "type": "generate_structured",
            "ticket_id": ticket_id,
            "schema": output_schema.__name__ if output_schema else "unknown"
        })
        
        # Get pre-defined response or generate default
        if ticket_id and ticket_id in self.responses:
            response = self.responses[ticket_id]
        else:
            response = self._generate_default_response(ticket_id, prompt)
        
        return MockLLMResponse(
            content=json.dumps(response),
            structured_output=response
        )
    
    def _extract_ticket_id(self, prompt: str) -> Optional[str]:
        """Extract ticket_id from prompt JSON."""
        try:
            # Look for "ticket_id": "..." pattern
            import re
            match = re.search(r'"ticket_id":\s*"([^"]+)"', prompt)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None
    
    def _generate_default_response(self, ticket_id: str, prompt: str) -> Dict[str, Any]:
        """Generate default triage response based on prompt content."""
        # Detect severity from prompt
        prompt_lower = prompt.lower()
        
        # Determine escalation triggers
        escalation_keywords = ["security", "outage", "500 error", "production", "critical", "urgent"]
        requires_escalation = any(kw in prompt_lower for kw in escalation_keywords)
        
        # Determine severity
        if "critical" in prompt_lower or "outage" in prompt_lower:
            severity = "P1"
            confidence = 0.75
        elif "high" in prompt_lower or "500" in prompt_lower:
            severity = "P2"
            confidence = 0.80
        elif "medium" in prompt_lower:
            severity = "P3"
            confidence = 0.85
        else:
            severity = "P4"
            confidence = 0.90
        
        # Determine issue type
        if "incident" in prompt_lower:
            issue_type = "incident"
        elif "question" in prompt_lower or "how" in prompt_lower:
            issue_type = "question"
        else:
            issue_type = "bug"
        
        # Determine category
        category = "other"
        category_map = {
            "validation": ["validation", "pydantic", "form"],
            "authentication": ["auth", "jwt", "oauth", "login"],
            "performance": ["slow", "latency", "timeout", "performance"],
            "dependency_lifecycle": ["depends", "yield", "lifecycle", "dependency"],
        }
        for cat, keywords in category_map.items():
            if any(kw in prompt_lower for kw in keywords):
                category = cat
                break
        
        escalation_reasons = []
        if requires_escalation:
            if "security" in prompt_lower:
                escalation_reasons.append("Security-related content detected")
            if "outage" in prompt_lower or "500" in prompt_lower:
                escalation_reasons.append("Production incident indicators")
            if severity == "P1":
                escalation_reasons.append("Severity P1")
            if confidence < 0.70:
                escalation_reasons.append("Low confidence score")
        
        return {
            "ticket_id": ticket_id or "unknown",
            "primary_category": category,
            "secondary_category": None,
            "issue_type": issue_type,
            "severity": severity,
            "severity_justification": f"Severity {severity} based on stated impact in ticket.",
            "confidence": confidence,
            "confidence_factors": {
                "category_clarity": "clear" if confidence > 0.8 else "moderate",
                "symptom_specificity": "specific" if confidence > 0.75 else "general",
                "technical_detail_level": "medium"
            },
            "requires_escalation": requires_escalation,
            "escalation_reasons": escalation_reasons,
            "technical_signals": {
                "affected_components": [],
                "framework_version": None,
                "python_version": None,
                "environment": "unknown",
                "has_reproduction_steps": False,
                "has_error_output": False
            },
            "keywords": ["ticket", "support", "issue"],
            "one_line_summary": f"Support ticket requiring {issue_type} handling.",
            "reasoning": {
                "category_rationale": f"Classified as {category} based on content analysis.",
                "facts_from_ticket": ["Ticket content analyzed"],
                "inferences_made": [],
                "uncertainty_notes": None
            }
        }


# Pre-defined responses for specific test scenarios
SCENARIO_A_RESPONSE = {
    "ticket_id": "ticket_006",
    "primary_category": "authentication",
    "secondary_category": None,
    "issue_type": "question",
    "severity": "P4",
    "severity_justification": "Low severity question about authentication best practices.",
    "confidence": 0.92,
    "confidence_factors": {
        "category_clarity": "clear",
        "symptom_specificity": "specific",
        "technical_detail_level": "high"
    },
    "requires_escalation": False,
    "escalation_reasons": [],
    "technical_signals": {
        "affected_components": ["OAuth", "JWT"],
        "framework_version": None,
        "python_version": None,
        "environment": "development",
        "has_reproduction_steps": False,
        "has_error_output": False
    },
    "keywords": ["authentication", "oauth", "jwt", "token", "best practices"],
    "one_line_summary": "Question about OAuth token handling best practices.",
    "reasoning": {
        "category_rationale": "Clear authentication question about OAuth/JWT token management.",
        "facts_from_ticket": ["User asking about authentication patterns"],
        "inferences_made": [],
        "uncertainty_notes": None
    }
}


SCENARIO_B_RESPONSE = {
    "ticket_id": "ticket_020",
    "primary_category": "validation",
    "secondary_category": None,
    "issue_type": "bug",
    "severity": "P2",
    "severity_justification": "High severity bug affecting request validation with no workaround.",
    "confidence": 0.65,  # Below threshold to trigger escalation
    "confidence_factors": {
        "category_clarity": "moderate",
        "symptom_specificity": "general",
        "technical_detail_level": "medium"
    },
    "requires_escalation": True,
    "escalation_reasons": ["Low confidence score", "Severity P2"],
    "technical_signals": {
        "affected_components": ["Pydantic", "RequestValidation"],
        "framework_version": None,
        "python_version": None,
        "environment": "production",
        "has_reproduction_steps": True,
        "has_error_output": True
    },
    "keywords": ["validation", "pydantic", "bug", "request", "error"],
    "one_line_summary": "Validation bug causing request failures in production.",
    "reasoning": {
        "category_rationale": "Validation-related bug with Pydantic model issues.",
        "facts_from_ticket": ["Request validation failing", "Production environment"],
        "inferences_made": ["May affect multiple endpoints"],
        "uncertainty_notes": "Unclear if this is a Pydantic version issue."
    }
}


SCENARIO_C_RESPONSE = {
    "ticket_id": "test_incident_001",
    "primary_category": "performance",
    "secondary_category": None,
    "issue_type": "incident",
    "severity": "P1",
    "severity_justification": "Active production outage affecting all users with 500 errors.",
    "confidence": 0.88,
    "confidence_factors": {
        "category_clarity": "clear",
        "symptom_specificity": "specific",
        "technical_detail_level": "high"
    },
    "requires_escalation": True,
    "escalation_reasons": ["Severity P1", "Production incident indicators", "Contains keyword: outage"],
    "technical_signals": {
        "affected_components": ["API Gateway", "Auth Service"],
        "framework_version": None,
        "python_version": None,
        "environment": "production",
        "has_reproduction_steps": False,
        "has_error_output": True
    },
    "keywords": ["incident", "outage", "500 error", "production", "api gateway", "urgent"],
    "one_line_summary": "Production API returning 500 errors for all users - active incident.",
    "reasoning": {
        "category_rationale": "Active production incident with service-wide impact.",
        "facts_from_ticket": [
            "500 errors on all endpoints",
            "Service unavailable",
            "Affecting all users"
        ],
        "inferences_made": ["Likely infrastructure or deployment issue"],
        "uncertainty_notes": None
    }
}


def get_dry_run_llm_service() -> DryRunLLMService:
    """Get configured LLM service for dry run testing."""
    return DryRunLLMService(responses={
        "ticket_006": SCENARIO_A_RESPONSE,
        "ticket_020": SCENARIO_B_RESPONSE,
        "test_incident_001": SCENARIO_C_RESPONSE,
    })
