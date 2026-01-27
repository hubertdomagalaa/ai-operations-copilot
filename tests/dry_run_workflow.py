"""
Full Dry Run Workflow Test
==========================

Executes the complete workflow end-to-end with mock components.
Tests all 3 scenarios defined in the verification plan.

Usage:
    python tests/dry_run_workflow.py
    python tests/dry_run_workflow.py --scenario A
    python tests/dry_run_workflow.py --ticket path/to/ticket.json
"""

import sys
import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestration.langgraph.workflow import build_workflow
from orchestration.langgraph.state import create_initial_state
from orchestration.langgraph.nodes import set_llm_service
from tests.mocks.llm_service import get_dry_run_llm_service


def load_ticket(ticket_path: str) -> dict:
    """Load ticket from JSON file."""
    with open(ticket_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_separator(title: str = "", char: str = "=", width: int = 70):
    """Print formatted separator."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def print_state_summary(state: dict, stage: str = ""):
    """Print summary of workflow state."""
    if stage:
        print_separator(stage, "-")
    
    print(f"  Status: {state.get('status')}")
    print(f"  Current Step: {state.get('current_step')}")
    
    if state.get("error"):
        print(f"  [ERROR] {state.get('error')}")
    
    # Triage output
    if state.get("triage_output"):
        triage = state["triage_output"]
        result = triage.get("result", {})
        print(f"\n  Triage:")
        print(f"    Success: {triage.get('success', True)}")
        print(f"    Category: {result.get('primary_category', 'N/A')}")
        print(f"    Severity: {result.get('severity', 'N/A')}")
        print(f"    Confidence: {triage.get('confidence', 'N/A')}")
        print(f"    Requires Escalation: {result.get('requires_escalation', False)}")
        if result.get("escalation_reasons"):
            print(f"    Escalation Reasons: {result.get('escalation_reasons')}")
    
    # Knowledge output
    if state.get("knowledge_output"):
        knowledge = state["knowledge_output"]
        result = knowledge.get("result", {})
        print(f"\n  Knowledge:")
        print(f"    Success: {knowledge.get('success', True)}")
        print(f"    Documents Found: {result.get('document_count', 0)}")
        print(f"    Confidence: {knowledge.get('confidence', 'N/A')}")
    
    # Decision output
    if state.get("decision_output"):
        decision = state["decision_output"]
        result = decision.get("result", {})
        print(f"\n  Decision:")
        print(f"    Success: {decision.get('success', True)}")
        print(f"    Recommended Action: {result.get('recommended_action', 'N/A')}")
        print(f"    Risk Flags: {result.get('risk_flags', [])}")
        print(f"    Requires Human Approval: {result.get('requires_human_approval', True)}")
    
    # Action output
    if state.get("action_output"):
        action = state["action_output"]
        result = action.get("result", {})
        print(f"\n  Action:")
        print(f"    Success: {action.get('success', True)}")
        print(f"    Action Type: {result.get('action_type', 'N/A')}")
        print(f"    Content Length: {len(result.get('content', ''))} chars")
    
    # Human decision
    if state.get("human_decision"):
        print(f"\n  Human Decision: {state.get('human_decision')}")
    
    print()


async def run_scenario(
    ticket_path: str,
    scenario_name: str,
    simulate_approval: bool = False
) -> dict:
    """
    Run a single scenario through the workflow.
    
    Args:
        ticket_path: Path to ticket JSON
        scenario_name: Name of this scenario for logging
        simulate_approval: If True, simulate human approval and continue
    
    Returns:
        Final workflow state
    """
    print_separator(f"SCENARIO {scenario_name}")
    print()
    
    # Load ticket
    ticket_data = load_ticket(ticket_path)
    ticket_id = ticket_data.get("ticket_id", "unknown")
    
    print(f"[LOAD] Ticket: {ticket_id}")
    print(f"  Category (ground truth): {ticket_data.get('category', 'N/A')}")
    print(f"  Issue Type: {ticket_data.get('issue_type', 'N/A')}")
    print(f"  Severity: {ticket_data.get('severity', 'N/A')}")
    print()
    
    # Configure mock LLM service
    llm_service = get_dry_run_llm_service()
    set_llm_service(llm_service)
    
    # Create initial state
    import uuid
    trace_id = str(uuid.uuid4())[:8]
    state = create_initial_state(
        ticket_id=ticket_id,
        ticket_data=ticket_data,
        trace_id=trace_id,
    )
    
    print(f"[INIT] Created initial state with trace_id={trace_id}")
    print()
    
    # Build workflow
    workflow = build_workflow()
    config = {"configurable": {"thread_id": ticket_id}}
    
    # Run workflow
    print("[RUN] Executing workflow...")
    print()
    
    try:
        result = await workflow.ainvoke(state, config)
        
        print_state_summary(result, "WORKFLOW RESULT")
        
        # Check if paused for human
        if result.get("status") == "paused_for_human":
            print("[PAUSE] Workflow paused for human review")
            
            if simulate_approval:
                print("[SIMULATE] Simulating human approval...")
                
                # Resume with approval
                result["human_decision"] = {"action": "approve", "notes": "Dry run approval"}
                result = await workflow.ainvoke(result, config)
                
                print_state_summary(result, "AFTER APPROVAL")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}


async def run_all_scenarios():
    """Run all three test scenarios."""
    print_separator("AI OPERATIONS COPILOT - FULL DRY RUN")
    print(f"Date: {datetime.now().isoformat()}")
    print()
    
    results = {}
    
    # Scenario A: Clean auto-processable case
    ticket_a = "data/tickets/normalized/ticket_006.json"
    if Path(ticket_a).exists():
        results["A"] = await run_scenario(ticket_a, "A - Clean Auto-Processable", simulate_approval=True)
    else:
        print(f"[SKIP] Scenario A: ticket not found at {ticket_a}")
    
    print()
    
    # Scenario B: Ambiguous case triggering escalation
    ticket_b = "data/tickets/normalized/ticket_020.json"
    if Path(ticket_b).exists():
        results["B"] = await run_scenario(ticket_b, "B - Ambiguous Escalation", simulate_approval=False)
    else:
        print(f"[SKIP] Scenario B: ticket not found at {ticket_b}")
    
    print()
    
    # Scenario C: High-risk incident case
    ticket_c = "tests/fixtures/incident_ticket.json"
    if Path(ticket_c).exists():
        results["C"] = await run_scenario(ticket_c, "C - High-Risk Incident", simulate_approval=False)
    else:
        print(f"[SKIP] Scenario C: ticket not found at {ticket_c}")
    
    # Print summary
    print_separator("SUMMARY")
    print()
    
    for scenario, result in results.items():
        status = result.get("status", "unknown")
        current_step = result.get("current_step", "unknown")
        
        if status == "completed":
            outcome = "[OK] Completed"
        elif status == "paused_for_human":
            outcome = "[PAUSE] Awaiting Human Review"
        elif status == "failed":
            outcome = "[FAIL] Failed"
        else:
            outcome = f"[?] {status}"
        
        print(f"  Scenario {scenario}: {outcome} (step: {current_step})")
    
    print()
    print_separator("DRY RUN COMPLETE")
    
    return results


async def run_single_ticket(ticket_path: str, simulate_approval: bool = False):
    """Run workflow for a single ticket."""
    print_separator("AI OPERATIONS COPILOT - SINGLE TICKET DRY RUN")
    print(f"Date: {datetime.now().isoformat()}")
    print()
    
    result = await run_scenario(ticket_path, "Single Ticket", simulate_approval=simulate_approval)
    
    print_separator("DRY RUN COMPLETE")
    return result


def main():
    parser = argparse.ArgumentParser(description="Full dry run workflow test")
    parser.add_argument("--ticket", type=str, help="Path to specific ticket JSON")
    parser.add_argument("--scenario", type=str, choices=["A", "B", "C", "all"], default="all",
                        help="Which scenario to run")
    parser.add_argument("--approve", action="store_true", help="Simulate human approval")
    
    args = parser.parse_args()
    
    if args.ticket:
        asyncio.run(run_single_ticket(args.ticket, args.approve))
    elif args.scenario == "all":
        asyncio.run(run_all_scenarios())
    else:
        # Run specific scenario
        scenarios = {
            "A": "data/tickets/normalized/ticket_006.json",
            "B": "data/tickets/normalized/ticket_020.json",
            "C": "tests/fixtures/incident_ticket.json",
        }
        ticket_path = scenarios.get(args.scenario)
        if ticket_path:
            asyncio.run(run_single_ticket(ticket_path, args.approve))
        else:
            print(f"Unknown scenario: {args.scenario}")


if __name__ == "__main__":
    main()
