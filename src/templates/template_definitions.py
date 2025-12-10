"""
Template Definitions Module

Defines templates for various content types.
"""

from typing import Dict, Any, List


class FAQTemplate:
    """Template class for FAQ pages."""
    
    page_type: str = "faq"
    
    @staticmethod
    def build(questions: List[Dict]) -> Dict[str, Any]:
        """
        Build an FAQ page structure.
        
        Args:
            questions: List of question dictionaries with 'question' and 'answer' keys
            
        Returns:
            Structured FAQ page dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        validated_faqs = []
        for idx, q in enumerate(questions):
            if "question" not in q:
                raise ValueError(f"Question at index {idx} missing 'question' field")
            if "answer" not in q:
                raise ValueError(f"Question at index {idx} missing 'answer' field")
            validated_faqs.append({
                "question": str(q["question"]),
                "answer": str(q["answer"])
            })
        
        return {
            "page_type": "faq",
            "faqs": validated_faqs
        }


class ProductTemplate:
    """Template class for product pages."""
    
    page_type: str = "product"
    
    @staticmethod
    def build(product_data: Dict) -> Dict[str, Any]:
        """
        Build a product page structure.
        
        Args:
            product_data: Dictionary with product information
            
        Returns:
            Structured product page dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["name", "benefits", "how_to_use", "key_ingredients", "price"]
        for field in required_fields:
            if field not in product_data:
                raise ValueError(f"Missing required field: '{field}'")
        
        return {
            "page_type": "product",
            "sections": {
                "name": str(product_data.get("name", "")),
                "description": str(product_data.get("description", "")),  # LLM-generated description
                "concentration": str(product_data.get("concentration", "")),  # Product concentration
                "benefits": list(product_data.get("benefits", [])),
                "usage": str(product_data.get("how_to_use", "")),
                "ingredients": list(product_data.get("key_ingredients", [])),
                "price": str(product_data.get("price", "")),
                "warnings": str(product_data.get("side_effects", ""))
            }
        }


class ComparisonTemplate:
    """Template class for product comparison pages."""
    
    page_type: str = "comparison"
    
    @staticmethod
    def build(product_a: Dict, product_b: Dict, comparison_metrics: List[Dict]) -> Dict[str, Any]:
        """
        Build a comparison page structure.
        
        Args:
            product_a: First product dictionary
            product_b: Second product dictionary
            comparison_metrics: List of comparison metric dictionaries
            
        Returns:
            Structured comparison page dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        if not product_a or not isinstance(product_a, dict):
            raise ValueError("product_a must be a non-empty dictionary")
        if not product_b or not isinstance(product_b, dict):
            raise ValueError("product_b must be a non-empty dictionary")
        if not isinstance(comparison_metrics, list):
            raise ValueError("comparison_metrics must be a list")
        
        validated_metrics = []
        for idx, metric in enumerate(comparison_metrics):
            if not isinstance(metric, dict):
                raise ValueError(f"Metric at index {idx} must be a dictionary")
            validated_metrics.append(dict(metric))
        
        return {
            "page_type": "comparison",
            "products": [dict(product_a), dict(product_b)],
            "comparison_metrics": validated_metrics
        }


# Template definitions (legacy)
TEMPLATES: Dict[str, Dict[str, Any]] = {
    "faq": {
        "name": "FAQ Template",
        "fields": ["question", "answer"],
    },
    "product": {
        "name": "Product Template",
        "fields": ["title", "description", "features"],
    },
    "comparison": {
        "name": "Comparison Template",
        "fields": ["items", "criteria"],
    },
}


def get_template(template_name: str) -> Dict[str, Any]:
    """
    Get a template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Template definition
    """
    return TEMPLATES.get(template_name, {})


def list_templates() -> list:
    """
    List all available templates.
    
    Returns:
        List of template names
    """
    return list(TEMPLATES.keys())
