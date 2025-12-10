"""
Parser Agent Module

Agent responsible for parsing and extracting information from input content.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product


class DataParserAgent(BaseAgent):
    """
    Agent that parses input content and creates Product model instances.
    This agent runs first with no dependencies.
    """
    
    def __init__(self):
        """Initialize the DataParserAgent with agent_id 'parser'."""
        super().__init__(agent_id="parser")
        self.dependencies: List[str] = []  # No dependencies, runs first
    
    def can_execute(self, completed_agents: List[str]) -> bool:
        """
        Check if this agent can execute.
        Always returns True as this agent has no dependencies.
        
        Args:
            completed_agents: List of agent IDs that have completed execution
            
        Returns:
            Always True
        """
        return True
    
    def execute(self, shared_data: Dict[str, Any]) -> Product:
        """
        Execute the parser agent logic.
        Takes raw_data from shared_data and validates/creates a Product model instance.
        
        Args:
            shared_data: Shared data dictionary with 'raw_input' key
            
        Returns:
            Product model instance
            
        Raises:
            KeyError: If 'raw_input' is not in shared_data
            ValidationError: If raw_input data is invalid for Product model
        """
        self.status = "running"
        
        raw_data = shared_data["raw_input"]
        
        # Create and validate Product model instance
        product = Product(
            name=raw_data.get("name", ""),
            concentration=raw_data.get("concentration", ""),
            skin_type=raw_data.get("skin_type", []),
            key_ingredients=raw_data.get("key_ingredients", []),
            benefits=raw_data.get("benefits", []),
            how_to_use=raw_data.get("how_to_use", ""),
            side_effects=raw_data.get("side_effects", ""),
            price=raw_data.get("price", "")
        )
        
        self.output = product
        self.mark_complete()
        
        return product
