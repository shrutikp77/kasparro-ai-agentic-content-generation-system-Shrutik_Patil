"""
Product Agent Module

Agent responsible for generating product page content.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product
from src.content_blocks.generators import (
    generate_benefits_block,
    generate_usage_block,
    generate_safety_block,
    generate_ingredients_block
)
from src.templates.template_definitions import ProductTemplate


class ProductPageAgent(BaseAgent):
    """
    Agent that generates product page content using content blocks.
    Depends on parser agent for product data.
    """
    
    def __init__(self):
        """Initialize the ProductPageAgent with agent_id 'product'."""
        super().__init__(agent_id="product")
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
        Execute the product page agent logic.
        Generates a complete product page using content blocks and template.
        
        Args:
            shared_data: Shared data dictionary with 'parser' key containing Product
            
        Returns:
            Structured product page dictionary built using ProductTemplate
        """
        self.status = "running"
        
        product: Product = shared_data["parser"]
        
        # Generate content sections using content blocks
        benefits_section = generate_benefits_block(product)
        usage_section = generate_usage_block(product)
        safety_section = generate_safety_block(product)
        ingredients_section = generate_ingredients_block(product)
        
        # Build product_data dict with all sections
        product_data = {
            "name": product.name,
            "concentration": product.concentration,
            "benefits": product.benefits,
            "how_to_use": product.how_to_use,
            "key_ingredients": product.key_ingredients,
            "price": product.price,
            "side_effects": product.side_effects,
            "skin_type": product.skin_type,
            # Generated content sections
            "benefits_content": benefits_section,
            "usage_content": usage_section,
            "safety_content": safety_section,
            "ingredients_content": ingredients_section
        }
        
        # Use ProductTemplate to build final output
        product_output = ProductTemplate.build(product_data)
        
        self.output = product_output
        self.mark_complete()
        
        return product_output
