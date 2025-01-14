"""XHTML to HTML converter with improved layout preservation.

This module provides functionality to convert XHTML documents to HTML
while maintaining document structure, especially for tables and complex layouts.
"""

from .converter import convert, xhtml_to_html

__version__ = "0.1.0"
__all__ = ["convert", "xhtml_to_html"]
