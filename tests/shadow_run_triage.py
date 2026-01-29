"""
Shadow Mode TriageAgent Test
=============================

Runs TriageAgent with REAL LLM (OpenRouter) in shadow/observation mode.

PURPOSE:
- Verify real LLM produces valid JSON
- Verify schema validation passes
- Observe confidence distribution
- Observe escalation behavior
- NO correctness assertions

USAGE:
    # Set environment variables first
    $env:LLM_PROVIDER="openrouter"
    $env:OPENROUTER_API_KEY="your-key"
    $env:LLM_MODEL="anthropic/claude-3.5-sonnet"
    $env:LLM_TEMPERATURE="0.2"
    
    python tests/shadow_run_triage.py
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment from .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from agents.triage import TriageAgent
from agents.triage.schema import TriageOutput
from backend.services.llm import get_llm_service


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# === Test Tickets ===

TEST_TICKETS = [
    "ticket_001.json",  # dependency_lifecycle bug
    "ticket_006.json",  # authentication question
    "ticket_010.json",  # validation bug
    "ticket_015.json",  # performance issue
    "ticket_020.json",  # validation bug (high severity)
]


def load_ticket(filename: str) -> Dict[str, Any]:
    """Load normalized ticket from data directory."""
    ticket_path = project_root / "data" / "tickets" / "normalized" / filename
    if not ticket_path.exists():
        raise FileNotFoundError(f"Ticket not found: {ticket_path}")
    with open(ticket_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_separator(title: str = "", width: int = 70):
    """Print formatted separator."""
    if title:
        print(f"\n{'='*width}")
        print(f"  {title}")
        print(f"{'='*width}")
    else:
        print("=" * width)


async def run_triage_on_ticket(
    agent: TriageAgent,
    ticket_data: Dict[str, Any],
    ticket_name: str,
) -> Dict[str, Any]:
    """
    Run TriageAgent on a single ticket.
    
    Returns result dict with validation status.
    """
    ticket_id = ticket_data.get("ticket_id", "unknown")
    
    print(f"\n[{ticket_name}] Processing ticket: {ticket_id}")
    print(f"  Ground truth: category={ticket_data.get('category')}, severity={ticket_data.get('severity')}")
    
    # Build state
    state = {
        "ticket_data": ticket_data,
        "ticket_id": ticket_id,
    }
    
    result = {
        "ticket_id": ticket_id,
        "ticket_file": ticket_name,
        "ground_truth_category": ticket_data.get("category"),
        "ground_truth_severity": ticket_data.get("severity"),
        "success": False,
        "json_valid": False,
        "schema_valid": False,
        "predicted_category": None,
        "predicted_severity": None,
        "confidence": None,
        "requires_escalation": None,
        "escalation_reasons": [],
        "error": None,
    }
    
    try:
        # Run agent
        output = await agent.process(state)
        
        # Check if output is valid
        if output.get("success", True):
            result["success"] = True
            result["json_valid"] = True
            
            # Extract triage result
            triage_result = output.get("result", {})
            
            # Check schema validation
            try:
                # Attempt to validate with schema
                validated = TriageOutput.model_validate(triage_result)
                result["schema_valid"] = True
                
                # Extract key fields
                result["predicted_category"] = triage_result.get("primary_category")
                result["predicted_severity"] = triage_result.get("severity")
                result["confidence"] = output.get("confidence")
                result["requires_escalation"] = triage_result.get("requires_escalation", False)
                result["escalation_reasons"] = triage_result.get("escalation_reasons", [])
                
            except Exception as validation_error:
                result["schema_valid"] = False
                result["error"] = f"Schema validation: {validation_error}"
                logger.warning(f"Schema validation failed: {validation_error}")
        else:
            result["error"] = output.get("result", {}).get("error", "Unknown error")
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Agent error: {e}")
    
    # Print summary
    if result["success"] and result["schema_valid"]:
        print(f"  [OK] category={result['predicted_category']}, severity={result['predicted_severity']}")
        print(f"       confidence={result['confidence']:.2f}, escalation={result['requires_escalation']}")
        if result["escalation_reasons"]:
            print(f"       reasons: {result['escalation_reasons']}")
    else:
        print(f"  [FAIL] {result['error']}")
    
    return result


async def run_shadow_test():
    """Run shadow mode test on multiple tickets."""
    print_separator("AI OPERATIONS COPILOT - SHADOW MODE TEST")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Mode: Shadow (real LLM, no downstream agents)")
    
    # Get LLM service
    llm_service = get_llm_service()
    print(f"\nLLM Provider: {type(llm_service).__name__}")
    
    # Create agent
    agent = TriageAgent(llm_service=llm_service)
    print(f"Agent: TriageAgent v{agent.prompt_version}")
    
    # Results collection
    results: List[Dict[str, Any]] = []
    
    # Process each ticket
    for ticket_file in TEST_TICKETS:
        try:
            ticket_data = load_ticket(ticket_file)
            result = await run_triage_on_ticket(agent, ticket_data, ticket_file)
            results.append(result)
        except FileNotFoundError as e:
            print(f"\n[SKIP] {ticket_file}: {e}")
    
    # Print summary
    print_separator("SUMMARY")
    
    total = len(results)
    json_valid = sum(1 for r in results if r["json_valid"])
    schema_valid = sum(1 for r in results if r["schema_valid"])
    escalated = sum(1 for r in results if r.get("requires_escalation"))
    
    print(f"\nTotal tickets: {total}")
    print(f"JSON valid: {json_valid}/{total}")
    print(f"Schema valid: {schema_valid}/{total}")
    print(f"Escalated: {escalated}/{total}")
    
    # Confidence distribution
    confidences = [r["confidence"] for r in results if r["confidence"] is not None]
    if confidences:
        print(f"\nConfidence distribution:")
        print(f"  Min: {min(confidences):.2f}")
        print(f"  Max: {max(confidences):.2f}")
        print(f"  Avg: {sum(confidences)/len(confidences):.2f}")
    
    # Category distribution
    print(f"\nCategory distribution:")
    categories = {}
    for r in results:
        cat = r.get("predicted_category", "error")
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Save results
    results_path = project_root / "tests" / "shadow_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tickets": total,
            "json_valid": json_valid,
            "schema_valid": schema_valid,
            "escalated": escalated,
            "results": results,
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")
    print_separator("SHADOW TEST COMPLETE")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_shadow_test())
