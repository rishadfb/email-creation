"""
Configuration module for the Email Creation application.

This module centralizes all configuration settings and environment variable handling.
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Constants for required API keys and configuration settings
REQUIRED_API_KEYS = ["GEMINI_API_KEY", "APOLLO_API_KEY"]

# Load environment variables from .env file
load_dotenv()

def get_api_key(key_name: str) -> Optional[str]:
    """
    Get an API key from environment variables.
    
    Args:
        key_name: Name of the API key to retrieve
        
    Returns:
        The API key value or None if not found
    """
    return os.getenv(key_name)

def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that all required API keys are present.
    
    Returns:
        Dictionary mapping API key names to boolean indicating presence
    """
    return {key: bool(get_api_key(key)) for key in REQUIRED_API_KEYS}

def is_config_valid() -> bool:
    """
    Check if all required configuration is valid.
    
    Returns:
        True if all required configuration is present, False otherwise
    """
    return all(validate_api_keys().values())

def get_missing_keys() -> list:
    """
    Get a list of missing API keys.
    
    Returns:
        List of missing API key names
    """
    validation = validate_api_keys()
    return [key for key, present in validation.items() if not present]

# Application settings
APP_SETTINGS = {
    "default_template": "welcome_email.html",
    "models": {
        "template_selection": "gemini-2.0-flash",
        "content_generation": "gemini-2.0-flash"
    }
}

def get_app_setting(setting_path: str) -> any:
    """
    Get an application setting using dot notation.
    
    Args:
        setting_path: Path to the setting using dot notation (e.g., "models.template_selection")
        
    Returns:
        The setting value or None if not found
    """
    parts = setting_path.split('.')
    current = APP_SETTINGS
    
    for part in parts:
        if part not in current:
            return None
        current = current[part]
        
    return current
