"""
Graph State Module

Defines the typed state schema for LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional
from src.models.schemas import Product, Question


class ContentGenerationState(TypedDict, total=False):
    """
    Typed state for the content generation workflow.
    
    This state is passed between all nodes in the LangGraph workflow.
    Each node reads from and writes to this shared state.
    """
    # Input data
    raw_input: Dict[str, Any]
    
    # Parser agent output
    parsed_product: Optional[Product]
    
    # Question agent output
    questions: Optional[List[Question]]
    
    # Final page outputs
    faq_output: Optional[Dict[str, Any]]
    product_output: Optional[Dict[str, Any]]
    comparison_output: Optional[Dict[str, Any]]
