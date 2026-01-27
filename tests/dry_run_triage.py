"""
Dry Run Test Script
===================

Tests the TriageAgent with a real normalized ticket using a mock LLM service.
This demonstrates the end-to-end flow without requiring actual LLM API calls.

Usage:
    python tests/dry_run_triage.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any


# Mock LLM response that simulates what a real LLM would return
MOCK_LLM_RESPONSE = {
    "ticket_id": "ticket_001",
    "primary_category": "dependency_lifecycle",
    "secondary_category": None,
    "issue_type": "bug",
    "severity": "P3",
    "severity_justification": "Partial degradation in dependency cleanup behavior. Workaround exists by declaring dependency on path function instead of router.",
    "confidence": 0.88,
    "confidence_factors": {
        "category_clarity": "clear",
        "symptom_specificity": "specific",
        "technical_detail_level": "high"
    },
    "requires_escalation": False,
    "escalation_reasons": [],
    "technical_signals": {
        "affected_components": ["APIRouter", "Depends", "yield dependencies", "scope parameter"],
        "framework_version": "0.121.0",
        "python_version": "3.11.12",
        "environment": "unknown",
        "has_reproduction_steps": True,
        "has_error_output": True
    },
    "keywords": ["yield dependencies", "dependency lifecycle", "APIRouter", "Depends", "scope", "cleanup"],
    "one_line_summary": "Yield dependency cleanup timing differs when dependency is declared on APIRouter vs path function.",
    "reasoning": {
        "category_rationale": "Ticket clearly describes yield dependency cleanup behavior issue with scope parameter. Affected components include Depends and yield dependencies, which are core dependency injection features.",
        "facts_from_ticket": [
            "Dependency cleanup error occurs after HTTP 200 response is sent",
            "Different behavior when dependency is on router vs path function",
            "Issue affects function-scoped yield dependencies",
            "Has reproducible code example"
        ],
        "inferences_made": [],
        "uncertainty_notes": None
    }
}


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
    latency_ms: int = 150


class MockLLMService:
    """
    Mock LLM service that returns pre-defined responses for testing.
    """
    
    def __init__(self, mock_response: Dict[str, Any]):
        self.mock_response = mock_response
        self.calls = []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> MockLLMResponse:
        """Return mock text response."""
        self.calls.append({"type": "generate", "prompt": prompt})
        return MockLLMResponse(
            content=json.dumps(self.mock_response),
            structured_output=None
        )
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
        system_prompt: Optional[str] = None,
    ) -> MockLLMResponse:
        """Return mock structured response."""
        self.calls.append({
            "type": "generate_structured",
            "prompt": prompt[:200] + "...",
            "schema": output_schema.__name__
        })
        return MockLLMResponse(
            content=json.dumps(self.mock_response),
            structured_output=self.mock_response
        )


async def run_dry_run():
    """Execute dry run test."""
    
    print("=" * 60)
    print("AI OPERATIONS COPILOT - DRY RUN TEST")
    print("=" * 60)
    print()
    
    # Load test ticket
    ticket_path = Path("data/tickets/normalized/ticket_001.json")
    print(f"[LOAD] Loading ticket: {ticket_path}")
    
    with open(ticket_path, "r", encoding="utf-8") as f:
        ticket_data = json.load(f)
    
    print(f"   Ticket ID: {ticket_data['ticket_id']}")
    print(f"   Category (ground truth): {ticket_data['category']}")
    print(f"   Issue Type (ground truth): {ticket_data['issue_type']}")
    print(f"   Summary: {ticket_data['summary'][:80]}...")
    print()
    
    # Create mock LLM service
    print("[INIT] Initializing Mock LLM Service...")
    mock_llm = MockLLMService(MOCK_LLM_RESPONSE)
    
    # Import and initialize TriageAgent
    print("[INIT] Initializing TriageAgent...")
    from agents.triage import TriageAgent
    agent = TriageAgent(llm_service=mock_llm)
    
    # Create workflow state
    state = {
        "ticket_data": ticket_data,
        "ticket_id": ticket_data["ticket_id"],
    }
    
    # Process ticket
    print()
    print("-" * 60)
    print("[RUN] PROCESSING TICKET")
    print("-" * 60)
    
    result = await agent.process(state)
    
    # Display results
    print()
    print("[OK] TRIAGE RESULT")
    print("-" * 60)
    
    if result.get("success", True):
        triage_result = result.get("result", {})
        
        print(f"   Primary Category: {triage_result.get('primary_category')}")
        print(f"   Secondary Category: {triage_result.get('secondary_category')}")
        print(f"   Issue Type: {triage_result.get('issue_type')}")
        print(f"   Severity: {triage_result.get('severity')}")
        print(f"   Confidence: {triage_result.get('confidence'):.2f}")
        print()
        
        # Escalation status
        if triage_result.get("requires_escalation"):
            print(f"   [!] ESCALATION REQUIRED")
            for reason in triage_result.get("escalation_reasons", []):
                print(f"      - {reason}")
        else:
            print(f"   [OK] No escalation required")
        print()
        
        # Human review status
        if result.get("requires_human_review"):
            print(f"   [REVIEW] HUMAN REVIEW REQUIRED: {result.get('human_review_reason')}")
        else:
            print(f"   [OK] Auto-processable")
        print()
        
        # Keywords for RAG
        print(f"   Keywords for RAG:")
        for kw in triage_result.get("keywords", []):
            print(f"      - {kw}")
        print()
        
        # Reasoning
        reasoning = triage_result.get("reasoning", {})
        print(f"   Category Rationale:")
        print(f"      {reasoning.get('category_rationale', 'N/A')}")
        print()
        
        # Facts extracted
        print(f"   Facts from Ticket:")
        for fact in reasoning.get("facts_from_ticket", []):
            print(f"      * {fact}")
        print()
        
        # Metadata
        print(f"   Agent Metadata:")
        print(f"      Prompt Version: {result.get('metadata', {}).get('prompt_version')}")
        print(f"      Agent Type: {result.get('agent_type')}")
        
    else:
        print(f"   [ERROR] Processing failed: {result.get('result', {}).get('error')}")
    
    print()
    print("=" * 60)
    print("DRY RUN COMPLETE")
    print("=" * 60)
    
    # Show LLM call details
    print()
    print("[INFO] LLM CALL DETAILS")
    print("-" * 60)
    for i, call in enumerate(mock_llm.calls, 1):
        print(f"   Call {i}:")
        print(f"      Type: {call['type']}")
        print(f"      Schema: {call.get('schema', 'N/A')}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(run_dry_run())
