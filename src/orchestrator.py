"""
Orchestrator Module

This module coordinates the execution of multiple agents in the content generation pipeline.
It manages the workflow using DAG-based orchestration for autonomous agent execution.
"""

from typing import Dict, List, Any
from src.agents.parser_agent import DataParserAgent
from src.agents.question_agent import QuestionGenerationAgent
from src.agents.faq_agent import FAQGenerationAgent
from src.agents.product_agent import ProductPageAgent
from src.agents.comparison_agent import ComparisonAgent


class AgentOrchestrator:
    """
    Orchestrator class that coordinates agent execution using DAG-based dependencies.
    
    DAG Structure:
    - parser (no deps) → runs first
    - questions, product, comparison (dep: parser) → run after parser
    - faq (deps: parser, questions) → runs after questions completes
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents and shared data."""
        # Initialize all 5 agents
        self.parser_agent = DataParserAgent()
        self.question_agent = QuestionGenerationAgent()
        self.faq_agent = FAQGenerationAgent()
        self.product_agent = ProductPageAgent()
        self.comparison_agent = ComparisonAgent()
        
        # Create agents dict: {agent_id: agent_instance}
        self.agents: Dict[str, Any] = {
            "parser": self.parser_agent,
            "questions": self.question_agent,
            "faq": self.faq_agent,
            "product": self.product_agent,
            "comparison": self.comparison_agent
        }
        
        # Create shared_data dict for agents to read/write
        self.shared_data: Dict[str, Any] = {}
    
    def execute_dag(self, raw_product_data: Dict) -> Dict[str, Any]:
        """
        Execute the agent DAG with dependency-based scheduling.
        
        Args:
            raw_product_data: Raw product data to process
            
        Returns:
            Dictionary with all outputs: {"faq": ..., "product": ..., "comparison": ...}
        """
        # Add raw_product_data to shared_data
        self.shared_data["raw_input"] = raw_product_data
        
        # Track completed agents
        completed_agents: List[str] = []
        
        # Get total number of agents
        total_agents = len(self.agents)
        
        # Execute DAG until all agents are completed
        while len(completed_agents) < total_agents:
            # Find agents that can execute (dependencies satisfied)
            executable_agents = []
            for agent_id, agent in self.agents.items():
                if agent_id not in completed_agents and agent.can_execute(completed_agents):
                    executable_agents.append((agent_id, agent))
            
            # Execute those agents (sequentially for simplicity)
            for agent_id, agent in executable_agents:
                # Execute the agent
                output = agent.execute(self.shared_data)
                
                # Store agent output in shared_data[agent_id]
                self.shared_data[agent_id] = output
                
                # Add agent_id to completed_agents
                completed_agents.append(agent_id)
        
        # Return dict with all page outputs
        return {
            "faq": self.shared_data.get("faq"),
            "product": self.shared_data.get("product"),
            "comparison": self.shared_data.get("comparison")
        }
    
    def get_agent_status(self) -> Dict[str, str]:
        """
        Get the status of all agents.
        
        Returns:
            Dictionary with agent statuses
        """
        return {agent_id: agent.status for agent_id, agent in self.agents.items()}
    
    def reset(self):
        """Reset the orchestrator for a new execution."""
        self.__init__()


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
