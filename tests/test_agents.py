"""
Tests for Agent Modules

Unit tests for the agent classes in the content generation system.
"""

import pytest
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.agents.parser_agent import DataParserAgent
from src.agents.question_agent import QuestionGenerationAgent
from src.agents.faq_agent import FAQGenerationAgent
from src.agents.product_agent import ProductPageAgent
from src.agents.comparison_agent import ComparisonAgent
from src.models.schemas import Product


# Sample product data for tests
SAMPLE_PRODUCT_DATA: Dict[str, Any] = {
    "name": "Test Vitamin C Serum",
    "concentration": "10% Vitamin C",
    "skin_type": ["Oily", "Combination"],
    "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
    "benefits": ["Brightening", "Fades dark spots"],
    "how_to_use": "Apply 2-3 drops in the morning",
    "side_effects": "Mild tingling for sensitive skin",
    "price": "₹699"
}


class TestDataParserAgent:
    """Tests for DataParserAgent."""
    
    def test_agent_initialization(self):
        """Test that parser agent initializes with correct ID and no dependencies."""
        agent = DataParserAgent()
        assert agent.agent_id == "parser"
        assert agent.dependencies == []
        assert agent.status == "pending"
    
    def test_can_execute_always_true(self):
        """Test that parser agent can always execute (no dependencies)."""
        agent = DataParserAgent()
        assert agent.can_execute([]) is True
        assert agent.can_execute(["other_agent"]) is True
    
    def test_execute_creates_valid_product(self):
        """Test that execute creates a valid Product model."""
        agent = DataParserAgent()
        shared_data = {"raw_input": SAMPLE_PRODUCT_DATA}
        
        result = agent.execute(shared_data)
        
        assert isinstance(result, Product)
        assert result.name == "Test Vitamin C Serum"
        assert result.concentration == "10% Vitamin C"
        assert "Oily" in result.skin_type
        assert agent.status == "completed"
    
    def test_execute_with_missing_fields(self):
        """Test that execute handles missing optional fields with defaults."""
        agent = DataParserAgent()
        minimal_data = {
            "name": "Minimal Product",
            "concentration": "",
            "skin_type": [],
            "key_ingredients": [],
            "benefits": [],
            "how_to_use": "",
            "side_effects": "",
            "price": ""
        }
        shared_data = {"raw_input": minimal_data}
        
        result = agent.execute(shared_data)
        
        assert isinstance(result, Product)
        assert result.name == "Minimal Product"


class TestQuestionGenerationAgent:
    """Tests for QuestionGenerationAgent."""
    
    def test_agent_initialization(self):
        """Test that question agent initializes correctly."""
        agent = QuestionGenerationAgent()
        assert agent.agent_id == "questions"
        assert agent.dependencies == ["parser"]
        assert agent.status == "pending"
    
    def test_can_execute_requires_parser(self):
        """Test that question agent requires parser to complete first."""
        agent = QuestionGenerationAgent()
        assert agent.can_execute([]) is False
        assert agent.can_execute(["other_agent"]) is False
        assert agent.can_execute(["parser"]) is True
        assert agent.can_execute(["parser", "other"]) is True


class TestFAQGenerationAgent:
    """Tests for FAQGenerationAgent."""
    
    def test_agent_initialization(self):
        """Test that FAQ agent initializes correctly."""
        agent = FAQGenerationAgent()
        assert agent.agent_id == "faq"
        assert agent.dependencies == ["parser", "questions"]
        assert agent.status == "pending"
    
    def test_can_execute_requires_both_dependencies(self):
        """Test that FAQ agent requires both parser and questions."""
        agent = FAQGenerationAgent()
        assert agent.can_execute([]) is False
        assert agent.can_execute(["parser"]) is False
        assert agent.can_execute(["questions"]) is False
        assert agent.can_execute(["parser", "questions"]) is True


class TestProductPageAgent:
    """Tests for ProductPageAgent."""
    
    def test_agent_initialization(self):
        """Test that product agent initializes correctly."""
        agent = ProductPageAgent()
        assert agent.agent_id == "product"
        assert agent.dependencies == ["parser"]
        assert agent.status == "pending"
    
    def test_can_execute_requires_parser(self):
        """Test that product agent requires parser to complete first."""
        agent = ProductPageAgent()
        assert agent.can_execute([]) is False
        assert agent.can_execute(["parser"]) is True


class TestComparisonAgent:
    """Tests for ComparisonAgent."""
    
    def test_agent_initialization(self):
        """Test that comparison agent initializes correctly."""
        agent = ComparisonAgent()
        assert agent.agent_id == "comparison"
        assert agent.dependencies == ["parser"]
        assert agent.status == "pending"
    
    def test_can_execute_requires_parser(self):
        """Test that comparison agent requires parser to complete first."""
        agent = ComparisonAgent()
        assert agent.can_execute([]) is False
        assert agent.can_execute(["parser"]) is True


class TestAgentDependencyChain:
    """Tests for the complete agent dependency chain."""
    
    def test_initial_state_only_parser_can_run(self):
        """Test that only parser can run in initial state."""
        parser = DataParserAgent()
        questions = QuestionGenerationAgent()
        faq = FAQGenerationAgent()
        product = ProductPageAgent()
        comparison = ComparisonAgent()
        
        completed = []
        
        assert parser.can_execute(completed) is True
        assert questions.can_execute(completed) is False
        assert faq.can_execute(completed) is False
        assert product.can_execute(completed) is False
        assert comparison.can_execute(completed) is False
    
    def test_after_parser_multiple_can_run(self):
        """Test that questions, product, comparison can run after parser."""
        questions = QuestionGenerationAgent()
        faq = FAQGenerationAgent()
        product = ProductPageAgent()
        comparison = ComparisonAgent()
        
        completed = ["parser"]
        
        assert questions.can_execute(completed) is True
        assert faq.can_execute(completed) is False  # Still needs questions
        assert product.can_execute(completed) is True
        assert comparison.can_execute(completed) is True
    
    def test_after_parser_and_questions_faq_can_run(self):
        """Test that faq can run after both parser and questions complete."""
        faq = FAQGenerationAgent()
        
        completed = ["parser", "questions"]
        
        assert faq.can_execute(completed) is True
