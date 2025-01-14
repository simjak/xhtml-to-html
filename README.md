# XHTML to HTML Converter

A Python tool for converting XHTML documents to HTML while preserving layout and styling, especially for tables and complex layouts.

## Features

- Preserves document structure and styling
- Enhanced table layout preservation
- Maintains inline styles and CSS
- Handles namespaces correctly
- Preserves document encoding

## Requirements

- Python 3.10 or higher
- lxml library

## Installation

You can install the package directly from PyPI(not ready yet):

```bash
pip install xhtml-to-html
```

Or from GitHub repository:

```bash
uv add git+https://github.com/simjak/xhtml-to-html.git
```

For development installation:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/xhtml-to-html.git
cd xhtml-to-html
```

2. Install using uv:
```bash
uv sync
```

## Usage

Convert an XHTML file to HTML using the command line:

```bash
xhtml-to-html --input input.xhtml --output output.html
```

Example:

```bash
xhtml-to-html --input data/airbus.xhtml --output data/output.html
```

Or use it in your Python code:

```python
from pathlib import Path
from xhtml_to_html import convert

# Convert XHTML to HTML
input_path = Path("input.xhtml")
output_path = Path("output.html")
convert(input_path, output_path)
```

For development usage (if you cloned the repository):

```bash
uv run xhtml-to-html --input input.xhtml --output output.html
```

## License

MIT License
