"""
Base Agent
==========

Abstract base class for all agents in the system.

WHY THIS FILE EXISTS:
- Ensures consistent agent interface
- Provides common functionality (logging, timing, error handling)
- Enables type-safe agent composition in workflow

ALL AGENTS MUST:
1. Inherit from BaseAgent
2. Implement the process() method
3. Return AgentOutput with required fields
4. Include confidence score and reasoning
5. Signal if human review is required
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import time

# TODO: Import actual schemas when available
# from backend.schemas.agent import AgentInput, AgentOutput, AgentType


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Provides:
    - Consistent interface for workflow integration
    - Automatic timing of process() calls
    - Error handling and logging hooks
    """
    
    def __init__(self, agent_type: str):
        """
        Initialize the agent.
        
        Args:
            agent_type: String identifier for this agent type
        """
        self.agent_type = agent_type
        # TODO: Initialize logger
        # TODO: Initialize metrics
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the workflow state and return results.
        
        This is the main entry point called by the orchestrator.
        
        Args:
            state: Current workflow state (WorkflowState)
        
        Returns:
            Updated state with this agent's output
        
        Raises:
            AgentError: If processing fails
        """
        pass
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper around process() that adds timing and error handling.
        
        This is what the orchestrator actually calls.
        """
        start_time = time.time()
        
        try:
            # TODO: Log agent start
            result = await self.process(state)
            
            # Add timing
            elapsed_ms = int((time.time() - start_time) * 1000)
            result["processing_time_ms"] = elapsed_ms
            
            # TODO: Log agent completion
            # TODO: Record metrics
            
            return result
            
        except Exception as e:
            # TODO: Log error
            # TODO: Record error metrics
            raise
    
    def _create_output(
        self,
        result: Dict[str, Any],
        confidence: float,
        reasoning: str,
        requires_human_review: bool = False,
        human_review_reason: str = None,
        sources: list = None,
    ) -> Dict[str, Any]:
        """
        Helper to create a properly formatted agent output.
        
        Ensures all required fields are present.
        """
        return {
            "agent_type": self.agent_type,
            "success": True,
            "result": result,
            "confidence": confidence,
            "reasoning": reasoning,
            "requires_human_review": requires_human_review,
            "human_review_reason": human_review_reason,
            "sources": sources or [],
            "timestamp": datetime.utcnow().isoformat(),
        }
