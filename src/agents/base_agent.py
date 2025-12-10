"""
Base Agent Module

Abstract base class for all agents in the content generation system.
Enables autonomous agent execution with dependency tracking.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Provides dependency tracking and status management for autonomous execution.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize the base agent.
        
        Args:
            agent_id: The agent's unique identifier
        """
        self.agent_id = agent_id
        self.dependencies: List[str] = []
        self.status: str = "pending"  # pending, running, completed
        self.output: Any = None
    
    @abstractmethod
    def can_execute(self, completed_agents: List[str]) -> bool:
        """
        Check if this agent's dependencies are satisfied.
        
        Args:
            completed_agents: List of agent IDs that have completed execution
            
        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, shared_data: Dict[str, Any]) -> Any:
        """
        Execute agent logic autonomously.
        
        Args:
            shared_data: Shared data dictionary accessible by all agents
            
        Returns:
            Agent execution output
        """
        pass
    
    def mark_complete(self):
        """Mark the agent as completed."""
        self.status = "completed"
