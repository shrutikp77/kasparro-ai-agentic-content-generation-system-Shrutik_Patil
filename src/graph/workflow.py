"""
Workflow Module

Defines the LangGraph workflow for the content generation pipeline.
Uses StateGraph to orchestrate agents with DAG-based dependencies.
"""

import os
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from src.graph.state import ContentGenerationState
from src.models.schemas import Product, Question
from src.templates.template_definitions import FAQTemplate, ProductTemplate, ComparisonTemplate
from src.llm_client import llm_client


# Rate limiting delay between LLM calls (configurable via env)
AGENT_DELAY = int(os.getenv("AGENT_DELAY", "5"))


def _delay_for_rate_limit():
    """Add delay between LLM calls to respect rate limits."""
    print(f"Waiting {AGENT_DELAY}s to respect rate limits...")
    time.sleep(AGENT_DELAY)


# ============================================================================
# Node Functions - Each wraps agent logic
# ============================================================================

def parse_product(state: ContentGenerationState) -> Dict[str, Any]:
    """
    Parser node: Validates and creates Product model from raw input.
    No LLM call - pure data transformation.
    """
    print("Executing node: parse_product...")
    
    raw_data = state["raw_input"]
    
    product = Product(
        name=raw_data.get("name", ""),
        concentration=raw_data.get("concentration", ""),
        skin_type=raw_data.get("skin_type", []),
        key_ingredients=raw_data.get("key_ingredients", []),
        benefits=raw_data.get("benefits", []),
        how_to_use=raw_data.get("how_to_use", ""),
        side_effects=raw_data.get("side_effects", ""),
        price=raw_data.get("price", "")
    )
    
    print("Node parse_product completed.")
    return {"parsed_product": product}


def generate_questions(state: ContentGenerationState) -> Dict[str, Any]:
    """
    Question generation node: Uses LLM to generate categorized questions.
    """
    print("Executing node: generate_questions...")
    
    product = state["parsed_product"]
    
    system_prompt = """You are a product content specialist. Generate diverse, natural user questions about skincare products.
Questions should cover multiple categories: Informational, Safety, Usage, Purchase, and Comparison."""
    
    user_prompt = f"""Given this product data:
Name: {product.name}
Concentration: {product.concentration}
Skin Type: {', '.join(product.skin_type)}
Ingredients: {', '.join(product.key_ingredients)}
Benefits: {', '.join(product.benefits)}
Usage: {product.how_to_use}
Side Effects: {product.side_effects}
Price: {product.price}

Generate EXACTLY 15 user questions across these categories:
- 4 INFORMATIONAL questions (about benefits, ingredients, what it does, concentration)
- 3 SAFETY questions (side effects, who should avoid, warnings, allergies)
- 3 USAGE questions (how to apply, when to use, frequency, routine placement)
- 3 PURCHASE questions (price, value, where to buy, alternatives)
- 2 COMPARISON questions (vs other products, how it differs)

Return ONLY a JSON array with this structure:
[
  {{"id": "q1", "text": "question text here", "category": "INFORMATIONAL"}},
  {{"id": "q2", "text": "question text here", "category": "SAFETY"}},
  ...
]

Use natural language. Make questions realistic and varied."""
    
    response = llm_client.generate_json(system_prompt, user_prompt)
    
    questions = []
    for q_data in response:
        questions.append(Question(
            id=q_data["id"],
            text=q_data["text"],
            category=q_data["category"]
        ))
    
    print("Node generate_questions completed.")
    _delay_for_rate_limit()
    return {"questions": questions}


def generate_product_page(state: ContentGenerationState) -> Dict[str, Any]:
    """
    Product page generation node: Uses LLM to create product page content.
    """
    print("Executing node: generate_product_page...")
    
    product = state["parsed_product"]
    
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
    
    # Structure using template
    product_data = {
        "name": product.name,
        "description": content["description"],
        "concentration": product.concentration,
        "benefits": content["benefits_section"] if isinstance(content["benefits_section"], list) else product.benefits,
        "how_to_use": content["usage_section"],
        "key_ingredients": product.key_ingredients,
        "price": product.price,
        "side_effects": content["safety_section"]
    }
    
    template = ProductTemplate()
    product_output = template.build(product_data)
    
    print("Node generate_product_page completed.")
    _delay_for_rate_limit()
    return {"product_output": product_output}


def generate_comparison_page(state: ContentGenerationState) -> Dict[str, Any]:
    """
    Comparison page generation node: Uses LLM to create fictional competitor and comparison.
    """
    print("Executing node: generate_comparison_page...")
    
    product_a = state["parsed_product"]
    
    # Step 1: Generate fictional competitor
    system_prompt = """You are a product data specialist. Create realistic fictional competitor products for comparison."""
    
    user_prompt = f"""Given this real product:
Name: {product_a.name}
Concentration: {product_a.concentration}
Skin Type: {', '.join(product_a.skin_type)}
Ingredients: {', '.join(product_a.key_ingredients)}
Benefits: {', '.join(product_a.benefits)}
Price: {product_a.price}

Create a fictional competitor product (Product B) with this exact JSON structure:
{{
  "name": "fictional product name (similar category but different brand)",
  "concentration": "different concentration of similar active ingredient",
  "skin_type": ["different skin types"],
  "key_ingredients": ["3-4 ingredients, some overlapping, some unique"],
  "benefits": ["2-3 benefits, some similar, some different"],
  "how_to_use": "usage instructions",
  "side_effects": "potential side effects",
  "price": "price in ₹ (make it 15-30% different)"
}}

Make it realistic and competitive. Return ONLY valid JSON."""
    
    product_b_data = llm_client.generate_json(system_prompt, user_prompt, max_tokens=800)
    
    # Ensure all required fields exist with defaults
    product_b_data.setdefault("name", "Competitor Vitamin C Serum")
    product_b_data.setdefault("concentration", "15% Vitamin C")
    product_b_data.setdefault("skin_type", ["Normal", "Dry"])
    product_b_data.setdefault("key_ingredients", ["Vitamin C", "Vitamin E"])
    product_b_data.setdefault("benefits", ["Brightening", "Anti-aging"])
    product_b_data.setdefault("how_to_use", "Apply 2-3 drops daily")
    product_b_data.setdefault("side_effects", "May cause mild irritation")
    product_b_data.setdefault("price", "₹799")
    
    product_b = Product(**product_b_data)
    
    _delay_for_rate_limit()
    
    # Step 2: Generate comparison analysis
    system_prompt = """You are a product comparison expert. Analyze and compare skincare products objectively."""
    
    user_prompt = f"""Compare these two products:

Product A: {product_a.name}
- Concentration: {product_a.concentration}
- Ingredients: {', '.join(product_a.key_ingredients)}
- Benefits: {', '.join(product_a.benefits)}
- Price: {product_a.price}
- Skin Type: {', '.join(product_a.skin_type)}

Product B: {product_b.name}
- Concentration: {product_b.concentration}
- Ingredients: {', '.join(product_b.key_ingredients)}
- Benefits: {', '.join(product_b.benefits)}
- Price: {product_b.price}
- Skin Type: {', '.join(product_b.skin_type)}

Generate a JSON comparison with:
{{
  "ingredient_comparison": {{
    "common": ["shared ingredients"],
    "unique_to_a": ["ingredients only in A"],
    "unique_to_b": ["ingredients only in B"],
    "analysis": "2 sentence comparison of ingredient profiles"
  }},
  "price_comparison": {{
    "price_difference": "₹ amount and percentage",
    "value_assessment": "which offers better value and why (2 sentences)"
  }},
  "effectiveness_comparison": {{
    "concentration_analysis": "comparison of active ingredient concentrations",
    "benefit_overlap": ["shared benefits"],
    "unique_benefits_a": ["benefits unique to A"],
    "unique_benefits_b": ["benefits unique to B"]
  }},
  "recommendation": "1-2 sentences on which product suits which skin type/concern better"
}}

Return ONLY valid JSON."""
    
    comparison_metrics = llm_client.generate_json(system_prompt, user_prompt, max_tokens=1200)
    
    # Structure using template
    template = ComparisonTemplate()
    comparison_output = template.build(
        product_a.model_dump(),
        product_b.model_dump(),
        [comparison_metrics]
    )
    
    print("Node generate_comparison_page completed.")
    _delay_for_rate_limit()
    return {"comparison_output": comparison_output}


def generate_faq_page(state: ContentGenerationState) -> Dict[str, Any]:
    """
    FAQ page generation node: Uses LLM to generate answers for questions.
    Depends on questions being generated first.
    """
    print("Executing node: generate_faq_page...")
    
    product = state["parsed_product"]
    questions = state["questions"]
    
    # Format questions for LLM
    questions_text = "\n".join([f"{i+1}. [{q.category}] {q.text}" for i, q in enumerate(questions)])
    
    system_prompt = """You are a skincare product expert and customer service specialist.
Generate helpful, accurate, and engaging FAQ answers based on product data.
Answers should be informative yet concise (2-4 sentences each)."""
    
    user_prompt = f"""Generate FAQ answers for this product:

Product Data:
Name: {product.name}
Concentration: {product.concentration}
Skin Type: {', '.join(product.skin_type)}
Ingredients: {', '.join(product.key_ingredients)}
Benefits: {', '.join(product.benefits)}
Usage: {product.how_to_use}
Side Effects: {product.side_effects}
Price: {product.price}

Questions to answer:
{questions_text}

Return a JSON array with this structure:
[
  {{"question": "exact question text", "answer": "helpful answer based on product data"}},
  ...
]

Base all answers on the product data provided. Be helpful and accurate. Return ONLY valid JSON."""
    
    faq_items = llm_client.generate_json(system_prompt, user_prompt, max_tokens=2000)
    
    # Use FAQTemplate to build final output
    faq_output = FAQTemplate.build(faq_items)
    
    print("Node generate_faq_page completed.")
    return {"faq_output": faq_output}


# ============================================================================
# Workflow Graph Definition
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow for content generation.
    
    DAG Structure:
    - parse_product (no deps) → runs first
    - generate_questions, generate_product_page, generate_comparison_page (dep: parse_product)
    - generate_faq_page (deps: parse_product, generate_questions) → runs after questions
    
    Returns:
        Compiled LangGraph StateGraph
    """
    # Create the graph with our state type
    workflow = StateGraph(ContentGenerationState)
    
    # Add nodes
    workflow.add_node("parse_product", parse_product)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("generate_product_page", generate_product_page)
    workflow.add_node("generate_comparison_page", generate_comparison_page)
    workflow.add_node("generate_faq_page", generate_faq_page)
    
    # Define edges (DAG structure)
    # START -> parse_product
    workflow.add_edge(START, "parse_product")
    
    # parse_product -> questions, product, comparison (parallel-capable)
    workflow.add_edge("parse_product", "generate_questions")
    workflow.add_edge("parse_product", "generate_product_page")
    workflow.add_edge("parse_product", "generate_comparison_page")
    
    # questions -> faq (sequential dependency)
    workflow.add_edge("generate_questions", "generate_faq_page")
    
    # All terminal nodes -> END
    workflow.add_edge("generate_product_page", END)
    workflow.add_edge("generate_comparison_page", END)
    workflow.add_edge("generate_faq_page", END)
    
    # Compile and return
    return workflow.compile()


# Create singleton workflow instance
content_workflow = create_workflow()
