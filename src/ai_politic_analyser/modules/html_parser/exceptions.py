"""
Custom exceptions for HTML parsing operations.
"""


class HTMLParsingError(Exception):
    """Base exception for HTML parsing errors."""
    pass


class InvalidHTMLError(HTMLParsingError):
    """Raised when HTML content is invalid or cannot be parsed."""
    pass


class EmptyContentError(HTMLParsingError):
    """Raised when HTML content is empty or contains no meaningful content."""
    pass