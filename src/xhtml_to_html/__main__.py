"""Command-line interface for XHTML to HTML conversion."""

import argparse
import logging
import sys

from .converter import validate_input_file, xhtml_to_html

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the command-line interface."""
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
        sys.exit(1)


if __name__ == "__main__":
    main()
