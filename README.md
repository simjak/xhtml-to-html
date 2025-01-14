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

Convert an XHTML file to HTML:

```bash
uv run xhtml-to-html --input input.xhtml --output output.html
```

Example:

```bash
uv run xhtml-to-html --input data/airbus.xhtml --output data/output.html
```

## License

MIT License
