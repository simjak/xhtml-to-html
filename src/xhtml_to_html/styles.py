"""Style-related functionality for XHTML to HTML conversion."""

import logging
from typing import List

import lxml.etree as ET

from .utils import find_elements, safe_get_attrib

# Configure logging
logger = logging.getLogger(__name__)

# CSS styles to preserve table layout
TABLE_CSS = """
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
    page-break-inside: avoid;
}
td, th {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f8f9fa;
}
"""


def generate_unique_selector(element: ET._Element) -> str:
    """
    Generate a unique CSS selector for an element based on its attributes.
    """
    element_id = safe_get_attrib(element, "id")
    if element_id:
        return f"#{element_id}"

    element_class = safe_get_attrib(element, "class")
    if element_class:
        classes = element_class.split()
        return f"{element.tag}.{'.'.join(classes)}"

    # Generate a path-based selector if no id/class
    path = []
    parent = element.getparent()
    while parent is not None:
        try:
            siblings = [c for c in parent.getchildren() if c.tag == element.tag]
            if len(siblings) > 1:
                index = siblings.index(element) + 1
                path.append(f"{element.tag}:nth-child({index})")
            else:
                path.append(element.tag)
        except Exception as e:
            logger.warning(f"Error generating selector part: {str(e)}")
            path.append(element.tag)
        element = parent
        parent = element.getparent()

    return " > ".join(reversed(path))


def extract_styles(tree: ET._Element) -> List[str]:
    """
    Extract all CSS styles from style tags and attributes.
    """
    styles = []

    # Extract styles from <style> tags
    for style in find_elements(tree, "style"):
        if style is not None and style.text:
            styles.append(style.text.strip())

    # Extract inline styles
    for element in tree.getroot().iter():
        style = safe_get_attrib(element, "style")
        if style:
            selector = generate_unique_selector(element)
            styles.append(f"{selector} {{ {style} }}")

    return styles
