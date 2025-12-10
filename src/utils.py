"""
Utility Functions Module

This module contains helper functions and utilities used across the content generation system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def write_json_output(data: Dict, filename: str, output_dir: str = "output/") -> None:
    """
    Write data to a JSON file with proper formatting.
    
    Args:
        data: Dictionary data to write (must be JSON-serializable)
        filename: Name of the output file
        output_dir: Directory for output files (default: "output/")
        
    Raises:
        ValueError: If data is not JSON-serializable
        IOError: If file cannot be written
    """
    try:
        # Validate data is JSON-serializable
        json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Data is not JSON-serializable: {e}")
    
    try:
        # Create output_dir if it doesn't exist
        ensure_directory(output_dir)
        
        # Build full file path
        filepath = os.path.join(output_dir, filename)
        
        # Write data to JSON file with proper formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except IOError as e:
        raise IOError(f"Failed to write file {filename}: {e}")


def ensure_directory(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to the output file
        indent: JSON indentation level
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def generate_timestamp() -> str:
    """
    Generate a timestamp string for file naming.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that a configuration dictionary contains required keys.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: List of required key names
        
    Returns:
        True if all required keys are present, False otherwise
    """
    return all(key in config for key in required_keys)
