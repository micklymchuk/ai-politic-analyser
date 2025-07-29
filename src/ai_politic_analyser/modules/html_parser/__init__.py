"""
HTML Parser Module for AI Political Analysis

This module provides HTML parsing capabilities optimized for AI text analysis.
It extracts semantic content while preserving structure and adding contextual labels.
"""

from .parser import HTMLParser
from .exceptions import HTMLParsingError

__version__ = "0.1.0"
__all__ = ["HTMLParser", "HTMLParsingError"]