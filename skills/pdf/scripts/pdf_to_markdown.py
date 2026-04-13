#!/usr/bin/env python3
"""
PDF to Markdown Converter
Convert PDF content to Markdown format with preserved structure.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed.")
    print("Please install: pip install pdfplumber")
    sys.exit(1)


def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace."""
    if not text:
        return ""
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove trailing/leading whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines)


def detect_headers(text: str) -> str:
    """
    Detect and convert potential headers to Markdown headers.

    Args:
        text: Input text line

    Returns:
        Text with Markdown header formatting if detected
    """
    text = text.strip()

    # Skip empty lines
    if not text:
        return ""

    # Check for common header patterns
    # All caps lines (but not too long)
    if text.isupper() and len(text) < 100:
        return f"## {text.title()}"

    # Lines ending with colon and not too long (likely section headers)
    if text.endswith(':') and len(text) < 80:
        return f"### {text[:-1]}"

    # Numbered sections (1. Introduction, 1.1 Background, etc.)
    if re.match(r'^\d+\.\d*\s+\w', text) and len(text) < 80:
        if re.match(r'^\d+\.\d+\s', text):
            return f"#### {text}"
        else:
            return f"### {text}"

    return text


def format_list_items(text: str) -> str:
    """
    Detect and format list items.

    Args:
        text: Input text line

    Returns:
        Text with Markdown list formatting if detected
    """
    text = text.strip()

    # Bullet points
    bullet_match = re.match(r'^[•·\-\*]\s*(.+)$', text)
    if bullet_match:
        return f"- {bullet_match.group(1)}"

    # Numbered lists
    number_match = re.match(r'^(\d+)[\.\)]\s*(.+)$', text)
    if number_match:
        return f"{number_match.group(1)}. {number_match.group(2)}"

    return text


def convert_page_to_markdown(page, include_page_markers: bool = True, page_num: int = 0) -> str:
    """
    Convert a single PDF page to Markdown.

    Args:
        page: pdfplumber page object
        include_page_markers: Whether to include page break markers
        page_num: Page number for marker

    Returns:
        Markdown formatted string
    """
    md_lines = []

    # Add page marker
    if include_page_markers and page_num > 0:
        md_lines.append(f"\n---\n**Page {page_num}**\n")

    # Extract text
    text = page.extract_text()

    if not text:
        return "\n".join(md_lines)

    # Process text line by line
    lines = text.split('\n')
    prev_line = ""
    in_paragraph = False

    for line in lines:
        line = line.strip()

        if not line:
            if in_paragraph:
                md_lines.append("")  # Add blank line after paragraph
                in_paragraph = False
            continue

        # Check for headers
        processed = detect_headers(line)

        if processed != line:
            # Header detected
            if in_paragraph:
                md_lines.append("")
            md_lines.append(processed)
            in_paragraph = False
            prev_line = processed
            continue

        # Check for list items
        processed = format_list_items(line)

        if processed != line:
            # List item detected
            md_lines.append(processed)
            in_paragraph = False
            prev_line = processed
            continue

        # Regular text - check if continuation of previous line
        if prev_line and not prev_line.startswith('#') and not prev_line.startswith('-') and not re.match(r'^\d+\.', prev_line):
            # Check if this is likely a continuation (starts with lowercase)
            if line[0].islower():
                # Append to previous line
                md_lines[-1] = md_lines[-1].rstrip() + ' ' + line
                continue

        md_lines.append(line)
        in_paragraph = True
        prev_line = line

    return "\n".join(md_lines)


def extract_and_convert_pdf(
    pdf_path: str,
    pages: Optional[List[int]] = None,
    include_page_markers: bool = True,
    extract_images_info: bool = False
) -> Tuple[str, List[str]]:
    """
    Extract content from PDF and convert to Markdown.

    Args:
        pdf_path: Path to PDF file
        pages: Optional list of page numbers (0-indexed)
        include_page_markers: Include page break markers
        extract_images_info: Include image information

    Returns:
        Tuple of (markdown content, list of errors)
    """
    errors = []
    md_content = []

    # Add title from filename
    pdf_name = Path(pdf_path).stem
    md_content.append(f"# {pdf_name}\n")
    md_content.append(f"*Converted from: {Path(pdf_path).name}*\n")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            # Determine which pages to process
            if pages is None:
                pages_to_process = range(total_pages)
            else:
                pages_to_process = [p for p in pages if 0 <= p < total_pages]

            for page_num in pages_to_process:
                page = pdf.pages[page_num]

                # Convert page to Markdown
                page_md = convert_page_to_markdown(
                    page,
                    include_page_markers=include_page_markers,
                    page_num=page_num + 1
                )
                md_content.append(page_md)

                # Extract image info if requested
                if extract_images_info:
                    images = page.images
                    if images:
                        md_content.append(f"\n*Images on page {page_num + 1}: {len(images)}*")
                        for i, img in enumerate(images[:5]):  # Limit to first 5
                            md_content.append(f"  - Image {i+1}: {img.get('width', 0):.0f}x{img.get('height', 0):.0f}")

            # Extract tables if present
            for page_num in pages_to_process:
                page = pdf.pages[page_num]
                tables = page.extract_tables()

                for table_idx, table in enumerate(tables):
                    if table and len(table) > 0:
                        md_content.append(f"\n### Table {table_idx + 1} (Page {page_num + 1})\n")

                        # Create Markdown table
                        if len(table) > 0:
                            # Header
                            header = table[0]
                            md_content.append("| " + " | ".join(str(cell or "") for cell in header) + " |")
                            md_content.append("| " + " | ".join(["---"] * len(header)) + " |")

                            # Rows
                            for row in table[1:]:
                                md_content.append("| " + " | ".join(str(cell or "") for cell in row) + " |")

        return "\n".join(md_content), errors

    except Exception as e:
        errors.append(f"Error processing PDF: {str(e)}")
        return "", errors


def parse_page_range(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of 0-indexed page numbers.
    """
    pages = []
    parts = page_range.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            for p in range(start - 1, min(end, total_pages)):
                if p >= 0:
                    pages.append(p)
        else:
            p = int(part) - 1
            if 0 <= p < total_pages:
                pages.append(p)

    return sorted(set(pages))


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF content to Markdown format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf -o document.md
  %(prog)s document.pdf -o document.md --pages 1-10
  %(prog)s document.pdf -o document.md --no-page-markers
  %(prog)s document.pdf  # Prints to stdout

The output includes:
  - Preserved text structure
  - Detected headers (converted to #, ##, ###)
  - Detected lists (bullet and numbered)
  - Tables (converted to Markdown table format)
"""
    )

    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file to convert"
    )

    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Output Markdown file path (default: print to stdout)"
    )

    parser.add_argument(
        "-p", "--pages",
        dest="page_range",
        help="Page range to convert (e.g., '1-5', '1,3,5', '1-3,5,7-9')"
    )

    parser.add_argument(
        "--no-page-markers",
        action="store_true",
        help="Don't include page break markers in output"
    )

    parser.add_argument(
        "--images",
        action="store_true",
        help="Include information about images in the PDF"
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.pdf_file):
        print(f"Error: File not found: {args.pdf_file}")
        sys.exit(1)

    # Get total pages and parse page range
    with pdfplumber.open(args.pdf_file) as pdf:
        total_pages = len(pdf.pages)

    pages = None
    if args.page_range:
        pages = parse_page_range(args.page_range, total_pages)
        print(f"Converting pages: {[p + 1 for p in pages]}", file=sys.stderr)
    else:
        print(f"Converting all {total_pages} pages...", file=sys.stderr)

    # Convert PDF to Markdown
    markdown_content, errors = extract_and_convert_pdf(
        pdf_path=args.pdf_file,
        pages=pages,
        include_page_markers=not args.no_page_markers,
        extract_images_info=args.images
    )

    if errors:
        print("Errors encountered:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    # Output result
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Markdown saved to: {args.output_file}", file=sys.stderr)
    else:
        print(markdown_content)


if __name__ == "__main__":
    main()
