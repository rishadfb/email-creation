"""
Agent implementations for the Email Creation application.

This module exports the agent classes for use in the application.
"""
from .base import Agent, TemplateSelector, ContentGenerator, HtmlCompiler
from .template_selector import GeminiTemplateSelector
from .content_generator import GeminiContentGenerator
from .html_compiler import GeminiHtmlCompiler

# Export the concrete implementations with more descriptive names
EmailTemplateSelector = GeminiTemplateSelector
EmailContentGenerator = GeminiContentGenerator
EmailHtmlCompiler = GeminiHtmlCompiler
