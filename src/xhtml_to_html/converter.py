"""Core conversion functionality for XHTML to HTML transformation."""

import logging
import os
from typing import List

import lxml.etree as ET

from .styles import TABLE_CSS, extract_styles, generate_unique_selector
from .utils import create_parser, find_elements, safe_get_attrib

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
