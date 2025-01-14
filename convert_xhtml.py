"""
convert_xhtml.py

A Python script to convert XHTML to HTML with improved layout preservation.
Focuses on maintaining document structure, especially for tables and complex layouts.

Requirements:
    - Python 3.7+
    - pip install lxml cssselect

Usage:
    Convert XHTML → HTML (with structure preservation):
    python convert_xhtml.py --input report.xhtml --output out.html
"""

import argparse
import logging
import os

import lxml.etree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
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


def create_parser() -> ET.XMLParser:
    """Create a consistent XML parser configuration."""
    return ET.XMLParser(recover=True, remove_comments=False, resolve_entities=False)


def safe_get_attrib(element: ET._Element, attr: str, default: str = "") -> str:
    """Safely get an attribute value from an element."""
    try:
        return element.attrib.get(attr, default)
    except Exception:
        return default


def find_elements(tree: ET._Element, tag: str) -> list[ET._Element]:
    """Find all elements with the given tag."""
    try:
        return tree.findall(f".//{tag}", namespaces={})
    except Exception as e:
        logger.warning(f"Error finding elements with tag '{tag}': {str(e)}")
        return []


def extract_styles(tree: ET._Element) -> list[str]:
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


def enhance_table_structure(tree: ET._Element) -> None:
    """
    Enhance table structure by adding additional attributes and classes
    for better layout preservation.
    """
    # Find all tables
    for table in find_elements(tree, "table"):
        if table is not None:
            # Add layout preservation classes
            classes = safe_get_attrib(table, "class").split()
            classes.extend(["preserved-table"])
            table.set("class", " ".join(classes))

            # Process cells for colspan/rowspan
            cells = find_elements(table, "td") + find_elements(table, "th")
            for cell in cells:
                if cell is not None:
                    colspan = safe_get_attrib(cell, "colspan")
                    rowspan = safe_get_attrib(cell, "rowspan")
                    if colspan or rowspan:
                        classes = safe_get_attrib(cell, "class")
                        cell.set("class", (classes + " merged-cell").strip())


def remove_namespaces(xml_content: str) -> str:
    """
    Enhanced namespace removal that preserves document structure and styling.
    """
    try:
        parser = create_parser()
        tree = ET.ElementTree(ET.fromstring(xml_content.encode("utf-8", errors="replace"), parser))

        # Extract styles before transformation
        original_styles = extract_styles(tree)

        # Enhance table structure
        enhance_table_structure(tree)

        xslt_remove_ns = b"""
            <xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                exclude-result-prefixes="*">

              <xsl:output method="html" indent="yes" encoding="UTF-8"/>

              <!-- Keep elements with structure preservation -->
              <xsl:template match="*">
                <xsl:element name="{local-name()}">
                  <xsl:apply-templates select="@*"/>
                  <xsl:apply-templates select="node()"/>
                </xsl:element>
              </xsl:template>

              <!-- Preserve all attributes -->
              <xsl:template match="@*">
                <xsl:attribute name="{local-name()}">
                  <xsl:value-of select="."/>
                </xsl:attribute>
              </xsl:template>

              <!-- Special handling for table structure -->
              <xsl:template match="table">
                <table>
                  <xsl:apply-templates select="@*"/>
                  <xsl:apply-templates select="node()"/>
                </table>
              </xsl:template>
            </xsl:stylesheet>
        """

        # Create XSLT transform
        xslt_doc = ET.fromstring(xslt_remove_ns, parser)
        transform = ET.XSLT(xslt_doc)
        transformed_tree = transform(tree)

        # Combine original styles with table CSS
        combined_styles = "\n".join([TABLE_CSS] + original_styles)
        style_element = f"<style>{combined_styles}</style>"

        # Insert doctype and combined styles
        result = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {style_element}
</head>
<body>
{str(transformed_tree)}
</body>
</html>"""

        return result

    except Exception as e:
        logger.error(f"Error during namespace removal: {str(e)}")
        raise


def xhtml_to_html(xhtml_file: str, output_html: str) -> None:
    """
    Convert XHTML to HTML with enhanced structure preservation.
    """
    try:
        logger.info(f"Converting {xhtml_file} to HTML...")
        with open(xhtml_file, encoding="utf-8", errors="replace") as fin:
            xhtml_content = fin.read()

        html_content = remove_namespaces(xhtml_content)

        with open(output_html, "w", encoding="utf-8") as fout:
            fout.write(html_content)

        logger.info(f"Successfully converted to HTML: {output_html}")

    except Exception as e:
        logger.error(f"Error during HTML conversion: {str(e)}")
        raise


def validate_input_file(file_path: str) -> None:
    """
    Validate the input XHTML file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            parser = create_parser()
            ET.fromstring(content.encode("utf-8"), parser)
    except Exception as e:
        raise ValueError(f"Invalid XHTML file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced XHTML to HTML converter with layout preservation."
    )
    parser.add_argument("--input", required=True, help="Path to the input XHTML file.")
    parser.add_argument("--output", required=True, help="Output HTML filename.")

    args = parser.parse_args()

    try:
        # Validate input file
        validate_input_file(args.input)

        # Validate output format
        if not args.output.lower().endswith(".html"):
            raise ValueError("Output name must end with .html")

        # Perform conversion
        xhtml_to_html(args.input, args.output)

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
