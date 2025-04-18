"""
Custom exceptions for the Email Creation application.

This module defines custom exception classes for different types of errors
that can occur in the application, making error handling more specific and informative.
"""

class EmailCreationError(Exception):
    """Base exception class for all email creation errors."""
    pass


class ConfigurationError(EmailCreationError):
    """Exception raised for errors in the application configuration."""
    pass


class APIKeyError(ConfigurationError):
    """Exception raised when required API keys are missing or invalid."""
    pass


class TemplateError(EmailCreationError):
    """Base class for template-related errors."""
    pass


class TemplateSelectionError(TemplateError):
    """Exception raised when template selection fails."""
    pass


class TemplateNotFoundError(TemplateError):
    """Exception raised when a template cannot be found."""
    pass


class ContentGenerationError(EmailCreationError):
    """Exception raised when content generation fails."""
    pass


class EmailCompilationError(EmailCreationError):
    """Exception raised when email compilation fails."""
    pass


class ContactDataError(EmailCreationError):
    """Exception raised for errors related to contact data."""
    pass


class AIServiceError(EmailCreationError):
    """Exception raised when AI service encounters an error."""
    
    def __init__(self, message: str, service_name: str, raw_response: str = None):
        """
        Initialize AIServiceError with additional context.
        
        Args:
            message: Error message
            service_name: Name of the AI service that encountered the error
            raw_response: Optional raw response from the service
        """
        self.service_name = service_name
        self.raw_response = raw_response
        super().__init__(f"{service_name} error: {message}")
