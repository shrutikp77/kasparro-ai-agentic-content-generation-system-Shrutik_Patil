"""
Orchestrator Module

Coordinates the execution of multiple agents using LangGraph workflow.
This module provides a high-level interface for the content generation pipeline.
"""

import os
from typing import Dict, Any

from src.graph.workflow import content_workflow
from src.graph.state import ContentGenerationState


class AgentOrchestrator:
    """
    Orchestrator class that coordinates agent execution using LangGraph.
    
    This class wraps the LangGraph workflow and provides a simple interface
    for executing the content generation pipeline.
    
    DAG Structure (managed by LangGraph):
    - parse_product (no deps) → runs first
    - generate_questions, generate_product_page, generate_comparison_page (dep: parse_product)
    - generate_faq_page (deps: parse_product, generate_questions) → runs after questions
    """
    
    def __init__(self):
        """Initialize the orchestrator with LangGraph workflow."""
        self.workflow = content_workflow
        self._last_state: Dict[str, Any] = {}
    
    def execute_dag(self, raw_product_data: Dict) -> Dict[str, Any]:
        """
        Execute the LangGraph workflow with the given product data.
        
        Args:
            raw_product_data: Raw product data dictionary
            
        Returns:
            Dictionary with all outputs: {"faq": ..., "product": ..., "comparison": ...}
        """
        print("Starting LangGraph workflow execution...")
        
        # Create initial state
        initial_state: ContentGenerationState = {
            "raw_input": raw_product_data
        }
        
        # Execute the LangGraph workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Store state for status checks
        self._last_state = final_state
        
        print("LangGraph workflow execution completed.")
        
        # Return dict with all page outputs (same interface as before)
        return {
            "faq": final_state.get("faq_output"),
            "product": final_state.get("product_output"),
            "comparison": final_state.get("comparison_output")
        }
    
    def get_agent_status(self) -> Dict[str, str]:
        """
        Get the status of all agents based on last execution.
        
        Returns:
            Dictionary with agent statuses
        """
        # In LangGraph, if we have outputs, the nodes completed successfully
        return {
            "parser": "completed" if self._last_state.get("parsed_product") else "pending",
            "questions": "completed" if self._last_state.get("questions") else "pending",
            "faq": "completed" if self._last_state.get("faq_output") else "pending",
            "product": "completed" if self._last_state.get("product_output") else "pending",
            "comparison": "completed" if self._last_state.get("comparison_output") else "pending"
        }
    
    def reset(self):
        """Reset the orchestrator for a new execution."""
        self._last_state = {}


def main():
    """Main entry point for the orchestrator."""
    # Sample product data
    raw_product_data = {
        "name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": ["Oily", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
        "benefits": ["Brightening", "Fades dark spots"],
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }
    
    # Create and run orchestrator
    orchestrator = AgentOrchestrator()
    results = orchestrator.execute_dag(raw_product_data)
    
    print("Orchestrator execution completed successfully")
    print(f"Agent statuses: {orchestrator.get_agent_status()}")
    
    return results


if __name__ == "__main__":
    main()
