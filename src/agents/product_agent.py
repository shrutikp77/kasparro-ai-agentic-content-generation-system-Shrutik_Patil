"""
Product Agent Module

Agent responsible for generating product page content using LLM.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product
from src.templates.template_definitions import ProductTemplate
from src.llm_client import llm_client


class ProductPageAgent(BaseAgent):
    """
    Agent that generates product page content using LLM.
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
        Generate product page using LLM.
        
        Args:
            shared_data: Shared data dictionary with 'parser' key containing Product
            
        Returns:
            Structured product page dictionary built using ProductTemplate
        """
        self.status = "running"
        
        product: Product = shared_data["parser"]
        
        system_prompt = """You are a professional product copywriter for skincare e-commerce.
Generate compelling, accurate product page content based on provided data.
Write in a clear, engaging style that informs and persuades customers."""
        
        user_prompt = f"""Create product page content for:

Product Data:
Name: {product.name}
Concentration: {product.concentration}
Skin Type: {', '.join(product.skin_type)}
Ingredients: {', '.join(product.key_ingredients)}
Benefits: {', '.join(product.benefits)}
Usage: {product.how_to_use}
Side Effects: {product.side_effects}
Price: {product.price}

Generate a JSON object with these fields:
{{
  "description": "2-3 sentence compelling product description",
  "benefits_section": "Formatted benefits text highlighting what it does",
  "usage_section": "Clear usage instructions with tips",
  "ingredients_section": "Explanation of key ingredients and their roles",
  "safety_section": "Safety information and precautions"
}}

Write naturally, professionally. Base everything on the data provided. Return ONLY valid JSON."""
        
        content = llm_client.generate_json(system_prompt, user_prompt, max_tokens=1500)
        
        # Ensure all fields have defaults
        content.setdefault("description", f"{product.name} is a premium skincare product.")
        content.setdefault("benefits_section", product.benefits)
        content.setdefault("usage_section", product.how_to_use)
        content.setdefault("ingredients_section", ", ".join(product.key_ingredients))
        content.setdefault("safety_section", product.side_effects)
        
        # Structure using template - use field names expected by ProductTemplate
        product_data = {
            "name": product.name,
            "description": content["description"],  # LLM-generated description
            "concentration": product.concentration,
            "benefits": content["benefits_section"] if isinstance(content["benefits_section"], list) else product.benefits,
            "how_to_use": content["usage_section"],
            "key_ingredients": product.key_ingredients,
            "price": product.price,
            "side_effects": content["safety_section"]
        }
        
        template = ProductTemplate()
        product_output = template.build(product_data)
        
        self.output = product_output
        self.mark_complete()
        
        return product_output

