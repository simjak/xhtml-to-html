"""Utility functions for XHTML to HTML conversion."""

import logging
from typing import List

import lxml.etree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_parser() -> ET.XMLParser:
    """Create a consistent XML parser configuration."""
    return ET.XMLParser(recover=True, remove_comments=False, resolve_entities=False)


def safe_get_attrib(element: ET._Element, attr: str, default: str = "") -> str:
    """Safely get an attribute value from an element."""
    try:
        return element.attrib.get(attr, default)
    except Exception:
        return default


def find_elements(tree: ET._Element, tag: str) -> List[ET._Element]:
    """Find all elements with the given tag."""
    try:
        return tree.findall(f".//{tag}", namespaces={})
    except Exception as e:
        logger.warning(f"Error finding elements with tag '{tag}': {str(e)}")
        return []
