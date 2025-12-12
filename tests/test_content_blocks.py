"""
Tests for Content Block Generators

Unit tests for the pure functions in the content_blocks/generators module.
"""

import pytest
from typing import Dict, Any, List

from src.content_blocks.generators import (
    extract_product_summary,
    calculate_price_difference,
    extract_common_ingredients,
    extract_unique_ingredients,
    generate_content_block,
    merge_content_blocks
)
from src.models.schemas import Product


# Sample products for testing
@pytest.fixture
def sample_product_a() -> Product:
    """Create sample product A for testing."""
    return Product(
        name="GlowBoost Vitamin C Serum",
        concentration="10% Vitamin C",
        skin_type=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid", "Niacinamide"],
        benefits=["Brightening", "Fades dark spots"],
        how_to_use="Apply 2-3 drops in the morning",
        side_effects="Mild tingling for sensitive skin",
        price="₹699"
    )


@pytest.fixture
def sample_product_b() -> Product:
    """Create sample product B for testing."""
    return Product(
        name="RadiantGlow Serum",
        concentration="15% Vitamin C",
        skin_type=["Normal", "Dry"],
        key_ingredients=["Vitamin C", "Vitamin E", "Aloe Vera"],
        benefits=["Brightening", "Anti-aging"],
        how_to_use="Apply 2-3 drops daily",
        side_effects="May cause mild irritation",
        price="₹899"
    )


class TestExtractProductSummary:
    """Tests for extract_product_summary function."""
    
    def test_basic_summary(self, sample_product_a):
        """Test that summary contains product name and key info."""
        result = extract_product_summary(sample_product_a)
        
        assert "GlowBoost Vitamin C Serum" in result
        assert "10% Vitamin C" in result
        assert "Oily" in result
        assert "Combination" in result
    
    def test_summary_format(self, sample_product_a):
        """Test that summary follows expected format."""
        result = extract_product_summary(sample_product_a)
        
        assert " - " in result
        assert " for " in result


class TestCalculatePriceDifference:
    """Tests for calculate_price_difference function."""
    
    def test_basic_calculation(self):
        """Test basic price difference calculation."""
        result = calculate_price_difference("₹699", "₹899")
        
        assert "difference" in result
        assert "percentage" in result
        assert "₹200" in result["difference"]
    
    def test_higher_to_lower_price(self):
        """Test calculation when first price is higher."""
        result = calculate_price_difference("₹1000", "₹800")
        
        assert "₹200" in result["difference"]
    
    def test_same_price(self):
        """Test calculation when prices are equal."""
        result = calculate_price_difference("₹500", "₹500")
        
        assert "₹0" in result["difference"]
        assert "0" in result["percentage"]
    
    def test_invalid_price_format(self):
        """Test handling of invalid price format."""
        result = calculate_price_difference("Invalid", "₹500")
        
        assert result["difference"] == "N/A"
        assert result["percentage"] == "N/A"
    
    def test_numeric_only_prices(self):
        """Test with numeric-only prices."""
        result = calculate_price_difference("699", "899")
        
        assert "₹200" in result["difference"]
    
    def test_percentage_calculation(self):
        """Test that percentage is calculated correctly."""
        result = calculate_price_difference("₹100", "₹150")
        
        # Difference is 50, percentage is 50/100 * 100 = 50%
        assert "50" in result["percentage"]


class TestExtractCommonIngredients:
    """Tests for extract_common_ingredients function."""
    
    def test_common_ingredients(self, sample_product_a, sample_product_b):
        """Test finding common ingredients between products."""
        result = extract_common_ingredients(sample_product_a, sample_product_b)
        
        assert isinstance(result, list)
        assert "Vitamin C" in result
    
    def test_no_common_ingredients(self):
        """Test when products have no common ingredients."""
        product_a = Product(
            name="Product A",
            concentration="",
            skin_type=[],
            key_ingredients=["Ingredient A", "Ingredient B"],
            benefits=[],
            how_to_use="",
            side_effects="",
            price=""
        )
        product_b = Product(
            name="Product B",
            concentration="",
            skin_type=[],
            key_ingredients=["Ingredient C", "Ingredient D"],
            benefits=[],
            how_to_use="",
            side_effects="",
            price=""
        )
        
        result = extract_common_ingredients(product_a, product_b)
        
        assert result == []
    
    def test_all_ingredients_common(self):
        """Test when all ingredients are common."""
        product_a = Product(
            name="Product A",
            concentration="",
            skin_type=[],
            key_ingredients=["A", "B"],
            benefits=[],
            how_to_use="",
            side_effects="",
            price=""
        )
        product_b = Product(
            name="Product B",
            concentration="",
            skin_type=[],
            key_ingredients=["A", "B"],
            benefits=[],
            how_to_use="",
            side_effects="",
            price=""
        )
        
        result = extract_common_ingredients(product_a, product_b)
        
        assert len(result) == 2


class TestExtractUniqueIngredients:
    """Tests for extract_unique_ingredients function."""
    
    def test_unique_ingredients(self, sample_product_a, sample_product_b):
        """Test finding unique ingredients in product A."""
        result = extract_unique_ingredients(sample_product_a, sample_product_b)
        
        assert isinstance(result, list)
        assert "Hyaluronic Acid" in result
        assert "Niacinamide" in result
        assert "Vitamin C" not in result  # Common ingredient
    
    def test_unique_ingredients_reverse(self, sample_product_a, sample_product_b):
        """Test finding unique ingredients in product B."""
        result = extract_unique_ingredients(sample_product_b, sample_product_a)
        
        assert "Vitamin E" in result
        assert "Aloe Vera" in result
        assert "Vitamin C" not in result


class TestGenerateContentBlock:
    """Tests for generate_content_block function."""
    
    def test_basic_block_generation(self):
        """Test generating a content block."""
        data = {"key": "value", "number": 123}
        result = generate_content_block("test_type", data)
        
        assert result["type"] == "test_type"
        assert result["content"] == data
    
    def test_empty_data(self):
        """Test generating block with empty data."""
        result = generate_content_block("empty", {})
        
        assert result["type"] == "empty"
        assert result["content"] == {}


class TestMergeContentBlocks:
    """Tests for merge_content_blocks function."""
    
    def test_merge_multiple_blocks(self):
        """Test merging multiple content blocks."""
        blocks = [
            {"type": "block1", "content": {}},
            {"type": "block2", "content": {}},
            {"type": "block3", "content": {}}
        ]
        result = merge_content_blocks(blocks)
        
        assert "blocks" in result
        assert len(result["blocks"]) == 3
    
    def test_merge_empty_list(self):
        """Test merging empty list of blocks."""
        result = merge_content_blocks([])
        
        assert result["blocks"] == []
