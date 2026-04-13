#!/usr/bin/env python3
"""
PDF Text Extraction Script

Extract text from PDF files with support for multiple output formats:
- text: Plain text output
- markdown: Markdown formatted output
- json: Structured JSON output

Usage:
    python extract_text.py input.pdf -o output.txt
    python extract_text.py input.pdf -f markdown -o output.md
    python extract_text.py input.pdf -f json --stdout
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Dependency check
MISSING_DEPS = []

try:
    import pypdf
except ImportError:
    MISSING_DEPS.append("pypdf")

try:
    import pdfplumber
except ImportError:
    MISSING_DEPS.append("pdfplumber")


def check_dependencies() -> None:
    """Check if required dependencies are installed."""
    if MISSING_DEPS:
        print(f"Error: Missing required dependencies: {', '.join(MISSING_DEPS)}")
        print("Please install them with: pip install " + " ".join(MISSING_DEPS))
        sys.exit(1)


def extract_text_pypdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text using pypdf library.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing extracted text and metadata
    """
    result = {
        "source": pdf_path,
        "method": "pypdf",
        "pages": [],
        "total_pages": 0
    }

    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        result["total_pages"] = len(reader.pages)

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            result["pages"].append({
                "page_number": i + 1,
                "text": text.strip()
            })

    return result


def extract_text_pdfplumber(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text using pdfplumber library (better layout preservation).

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing extracted text and metadata
    """
    result = {
        "source": pdf_path,
        "method": "pdfplumber",
        "pages": [],
        "total_pages": 0
    }

    with pdfplumber.open(pdf_path) as pdf:
        result["total_pages"] = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            result["pages"].append({
                "page_number": i + 1,
                "text": text.strip()
            })

    return result


def format_as_text(data: Dict[str, Any]) -> str:
    """Format extracted data as plain text."""
    lines = []
    for page in data["pages"]:
        lines.append(f"--- Page {page['page_number']} ---")
        lines.append(page["text"])
        lines.append("")
    return "\n".join(lines)


def format_as_markdown(data: Dict[str, Any]) -> str:
    """Format extracted data as markdown."""
    lines = [f"# Extracted Text from {Path(data['source']).name}", ""]
    lines.append(f"- **Source:** {data['source']}")
    lines.append(f"- **Total Pages:** {data['total_pages']}")
    lines.append(f"- **Method:** {data['method']}")
    lines.append("")

    for page in data["pages"]:
        lines.append(f"## Page {page['page_number']}")
        lines.append("")
        lines.append(page["text"])
        lines.append("")

    return "\n".join(lines)


def format_as_json(data: Dict[str, Any]) -> str:
    """Format extracted data as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def extract_text(
    pdf_path: str,
    method: str = "pdfplumber",
    output_format: str = "text",
    output_file: Optional[str] = None,
    pages: Optional[str] = None
) -> str:
    """
    Main extraction function.

    Args:
        pdf_path: Path to the PDF file
        method: Extraction method ('pypdf' or 'pdfplumber')
        output_format: Output format ('text', 'markdown', 'json')
        output_file: Output file path (optional, prints to stdout if None)
        pages: Page range (e.g., '1-5', '1,3,5', defaults to all)

    Returns:
        Extracted text content
    """
    # Validate input file
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"Not a PDF file: {pdf_path}")

    # Extract text
    if method == "pypdf":
        data = extract_text_pypdf(str(pdf_path))
    else:
        data = extract_text_pdfplumber(str(pdf_path))

    # Filter pages if specified
    if pages:
        page_numbers = parse_page_range(pages, data["total_pages"])
        data["pages"] = [p for p in data["pages"] if p["page_number"] in page_numbers]

    # Format output
    formatters = {
        "text": format_as_text,
        "markdown": format_as_markdown,
        "json": format_as_json
    }

    formatter = formatters.get(output_format, format_as_text)
    output = formatter(data)

    # Write or print output
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(output, encoding='utf-8')
        print(f"Text extracted to: {output_path}")
    else:
        print(output)

    return output


def parse_page_range(page_spec: str, total_pages: int) -> List[int]:
    """
    Parse page range specification.

    Args:
        page_spec: Page range string (e.g., '1-5', '1,3,5', '1-3,5,7-9')
        total_pages: Total number of pages in the document

    Returns:
        List of page numbers
    """
    pages = set()

    for part in page_spec.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))

    # Validate page numbers
    valid_pages = [p for p in pages if 1 <= p <= total_pages]
    if len(valid_pages) != len(pages):
        print(f"Warning: Some page numbers are out of range (1-{total_pages})", file=sys.stderr)

    return sorted(valid_pages)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf
    %(prog)s document.pdf -f markdown -o output.md
    %(prog)s document.pdf -p 1-5 --stdout
    %(prog)s document.pdf -m pypdf -f json
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "-m", "--method",
        choices=["pypdf", "pdfplumber"],
        default="pdfplumber",
        help="Extraction method (default: pdfplumber)"
    )

    parser.add_argument(
        "-p", "--pages",
        help="Page range to extract (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Force output to stdout"
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    try:
        extract_text(
            pdf_path=args.input,
            method=args.method,
            output_format=args.format,
            output_file=None if args.stdout else args.output,
            pages=args.pages
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting text: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
