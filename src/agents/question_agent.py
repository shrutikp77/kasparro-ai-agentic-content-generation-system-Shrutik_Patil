"""
Question Agent Module

Agent responsible for generating questions from product content.
"""

from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent
from src.models.schemas import Product, Question, QuestionCategory


class QuestionGenerationAgent(BaseAgent):
    """
    Agent that generates categorized questions based on product information.
    Depends on the parser agent to provide product data.
    """
    
    def __init__(self):
        """Initialize the QuestionGenerationAgent with agent_id 'questions'."""
        super().__init__(agent_id="questions")
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
    
    def execute(self, shared_data: Dict[str, Any]) -> List[Question]:
        """
        Execute the question generation agent logic.
        Generates 15+ categorized questions based on product data.
        
        Args:
            shared_data: Shared data dictionary with 'parser' key containing Product
            
        Returns:
            List of Question objects
        """
        self.status = "running"
        
        product: Product = shared_data["parser"]
        questions: List[Question] = []
        
        # Generate INFORMATIONAL questions (4)
        informational_questions = self._generate_informational_questions(product)
        questions.extend(informational_questions)
        
        # Generate SAFETY questions (3)
        safety_questions = self._generate_safety_questions(product)
        questions.extend(safety_questions)
        
        # Generate USAGE questions (3)
        usage_questions = self._generate_usage_questions(product)
        questions.extend(usage_questions)
        
        # Generate PURCHASE questions (3)
        purchase_questions = self._generate_purchase_questions(product)
        questions.extend(purchase_questions)
        
        # Generate COMPARISON questions (2)
        comparison_questions = self._generate_comparison_questions(product)
        questions.extend(comparison_questions)
        
        self.output = questions
        self.mark_complete()
        
        return questions
    
    def _generate_informational_questions(self, product: Product) -> List[Question]:
        """Generate INFORMATIONAL category questions."""
        return [
            Question(
                id="info_1",
                text=f"What are the key benefits of {product.name}?",
                category=QuestionCategory.INFORMATIONAL.value
            ),
            Question(
                id="info_2",
                text=f"What ingredients are in {product.name}?",
                category=QuestionCategory.INFORMATIONAL.value
            ),
            Question(
                id="info_3",
                text=f"What does {product.name} do for the skin?",
                category=QuestionCategory.INFORMATIONAL.value
            ),
            Question(
                id="info_4",
                text=f"What is the concentration of active ingredients in {product.name}?",
                category=QuestionCategory.INFORMATIONAL.value
            )
        ]
    
    def _generate_safety_questions(self, product: Product) -> List[Question]:
        """Generate SAFETY category questions."""
        return [
            Question(
                id="safety_1",
                text=f"What are the side effects of {product.name}?",
                category=QuestionCategory.SAFETY.value
            ),
            Question(
                id="safety_2",
                text=f"Who should avoid using {product.name}?",
                category=QuestionCategory.SAFETY.value
            ),
            Question(
                id="safety_3",
                text=f"Are there any warnings for {product.name}?",
                category=QuestionCategory.SAFETY.value
            )
        ]
    
    def _generate_usage_questions(self, product: Product) -> List[Question]:
        """Generate USAGE category questions."""
        return [
            Question(
                id="usage_1",
                text=f"How do I apply {product.name}?",
                category=QuestionCategory.USAGE.value
            ),
            Question(
                id="usage_2",
                text=f"When is the best time to use {product.name}?",
                category=QuestionCategory.USAGE.value
            ),
            Question(
                id="usage_3",
                text=f"How often should I use {product.name}?",
                category=QuestionCategory.USAGE.value
            )
        ]
    
    def _generate_purchase_questions(self, product: Product) -> List[Question]:
        """Generate PURCHASE category questions."""
        return [
            Question(
                id="purchase_1",
                text=f"What is the price of {product.name}?",
                category=QuestionCategory.PURCHASE.value
            ),
            Question(
                id="purchase_2",
                text=f"Where can I buy {product.name}?",
                category=QuestionCategory.PURCHASE.value
            ),
            Question(
                id="purchase_3",
                text=f"Is {product.name} worth the price?",
                category=QuestionCategory.PURCHASE.value
            )
        ]
    
    def _generate_comparison_questions(self, product: Product) -> List[Question]:
        """Generate COMPARISON category questions."""
        return [
            Question(
                id="comparison_1",
                text=f"How does {product.name} compare to other vitamin C serums?",
                category=QuestionCategory.COMPARISON.value
            ),
            Question(
                id="comparison_2",
                text=f"What are the alternatives to {product.name}?",
                category=QuestionCategory.COMPARISON.value
            )
        ]
