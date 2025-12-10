"""
FAQ Agent Module

Agent responsible for generating FAQ content from product and question data.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product, Question
from src.content_blocks.generators import generate_answer_block
from src.templates.template_definitions import FAQTemplate


class FAQGenerationAgent(BaseAgent):
    """
    Agent that generates FAQ entries from product and question data.
    Depends on parser and questions agents.
    """
    
    def __init__(self):
        """Initialize the FAQGenerationAgent with agent_id 'faq'."""
        super().__init__(agent_id="faq")
        self.dependencies: List[str] = ["parser", "questions"]
    
    def can_execute(self, completed_agents: List[str]) -> bool:
        """
        Check if this agent can execute.
        Returns True only if all dependencies have completed.
        
        Args:
            completed_agents: List of agent IDs that have completed execution
            
        Returns:
            True if all dependencies are in completed_agents
        """
        return all(dep in completed_agents for dep in self.dependencies)
    
    def execute(self, shared_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the FAQ generation agent logic.
        Generates FAQ content using product data and generated questions.
        
        Args:
            shared_data: Shared data dictionary with 'parser' and 'questions' keys
            
        Returns:
            Structured FAQ dictionary built using FAQTemplate
        """
        self.status = "running"
        
        product: Product = shared_data["parser"]
        questions: List[Question] = shared_data["questions"]
        
        # Select first 5 questions (mix of categories)
        selected_questions = questions[:5]
        
        # Generate answers for each question using generate_answer_block
        faq_items = []
        for question in selected_questions:
            answer = generate_answer_block(question, product)
            faq_items.append({
                "question": question.text,
                "answer": answer
            })
        
        # Use FAQTemplate to build final output
        faq_output = FAQTemplate.build(faq_items)
        
        self.output = faq_output
        self.mark_complete()
        
        return faq_output
