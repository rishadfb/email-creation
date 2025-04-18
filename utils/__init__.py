"""
Email Creation Application Utilities

This package contains utilities for the Email Creation application,
organized into subpackages:

- agents: Agent implementations for email creation tasks
- core: Core functionality like configuration and exceptions
- orchestration: Orchestration logic for coordinating agents
- services: External service integrations and utilities
- ui: User interface components
"""

# Import key components for easier access
from .orchestration.orchestrator import EmailOrchestrator
from .core.config import is_config_valid, get_missing_keys
from .core.exceptions import EmailCreationError, ConfigurationError
