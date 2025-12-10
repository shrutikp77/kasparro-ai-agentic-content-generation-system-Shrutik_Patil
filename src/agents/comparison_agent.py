"""
Comparison Agent Module

Agent responsible for generating comparison content between products.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product
from src.content_blocks.generators import (
    compare_ingredients_block,
    compare_price_block
)
from src.templates.template_definitions import ComparisonTemplate


class ComparisonAgent(BaseAgent):
    """
    Agent that generates comparison content between products.
    Depends on parser agent for product data.
    """
    
    def __init__(self):
        """Initialize the ComparisonAgent with agent_id 'comparison'."""
        super().__init__(agent_id="comparison")
        self.dependencies: List[str] = ["parser"]
    
    def can_execute(self, completed_agents: List[str]) -> bool:
        """
        Check if this agent can execute.
        Returns True only if the parser agent has completed.
        
        Args:
            completed_agents: List of agent IDs that have completed execution
            
        Returns:
            True if 'parser' is in completed_agents
        """
        return "parser" in completed_agents
    
    def execute(self, shared_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the comparison agent logic.
        Compares the parsed product with a fictional competitor product.
        
        Args:
            shared_data: Shared data dictionary with 'parser' key containing Product
            
        Returns:
            Structured comparison dictionary built using ComparisonTemplate
        """
        self.status = "running"
        
        # Get product_a (GlowBoost) from shared_data
        product_a: Product = shared_data["parser"]
        
        # Create fictional product_b for comparison
        product_b = Product(
            name="RadiantGlow Vitamin C Serum",
            concentration="15% Vitamin C",
            skin_type=["Normal", "Dry"],
            key_ingredients=["Vitamin C", "Vitamin E", "Ferulic Acid"],
            benefits=["Anti-aging", "Brightening"],
            how_to_use="Apply 3-4 drops morning and evening",
            side_effects="May cause slight redness",
            price="₹899"
        )
        
        # Use comparison blocks to generate comparison data
        ingredients_comparison = compare_ingredients_block(product_a, product_b)
        price_comparison = compare_price_block(product_a, product_b)
        
        # Prepare comparison metrics
        comparison_metrics = [
            ingredients_comparison,
            price_comparison
        ]
        
        # Use ComparisonTemplate to build final output
        comparison_output = ComparisonTemplate.build(
            product_a=product_a.model_dump(),
            product_b=product_b.model_dump(),
            comparison_metrics=comparison_metrics
        )
        
        self.output = comparison_output
        self.mark_complete()
        
        return comparison_output
