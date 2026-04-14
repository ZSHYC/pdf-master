#!/usr/bin/env python3
"""PDF Comparison Tool.

This module provides functionality to compare two PDF files and identify
differences in page count, page dimensions, and metadata.

Usage:
    python pdf_compare.py file1.pdf file2.pdf [--json] [-v|--verbose]

Exit codes:
    0 - PDFs are identical
    1 - PDFs have differences or an error occurred
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from typing import Dict

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing pypdf. Install with: pip install pypdf")
    sys.exit(1)

def validate_pdf_file(file_path: str) -> Path:
    """Validate that a file exists and is a valid PDF.

    Args:
        file_path: Path to the PDF file to validate.

    Returns:
        Path object representing the validated file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a PDF.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {file_path} (extension: {path.suffix})")

    return path


def compare_pdfs(file1: str, file2: str, verbose: bool = False) -> Dict[str, Any]:
    """Compare two PDF files and return their differences.

    Args:
        file1: Path to the first PDF file.
        file2: Path to the second PDF file.
        verbose: Whether to include verbose output (currently unused).

    Returns:
        A dictionary containing comparison results with keys:
        - file1: Path to first file
        - file2: Path to second file
        - differences: List of detected differences
        - identical: Boolean indicating if files are identical

    Raises:
        FileNotFoundError: If either file does not exist.
        ValueError: If either file is not a valid PDF.
    """
    # Validate input files
    validate_pdf_file(file1)
    validate_pdf_file(file2)

    result: Dict[str, Any] = {"file1": file1, "file2": file2, "differences": []}
    
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        r1, r2 = PdfReader(f1), PdfReader(f2)
        pages1, pages2 = len(r1.pages), len(r2.pages)
        
        if pages1 != pages2:
            result["differences"].append(f"Page count: {pages1} vs {pages2}")
        
        # Compare each page
        for i in range(min(pages1, pages2)):
            p1, p2 = r1.pages[i], r2.pages[i]
            # Compare page size
            w1, h1 = float(p1.mediabox.width), float(p1.mediabox.height)
            w2, h2 = float(p2.mediabox.width), float(p2.mediabox.height)
            if abs(w1 - w2) > 0.1 or abs(h1 - h2) > 0.1:
                result["differences"].append(f"Page {i+1} size differs")
        
        # Compare metadata
        m1, m2 = r1.metadata or {}, r2.metadata or {}
        for key in set(list(m1.keys()) + list(m2.keys())):
            v1, v2 = m1.get(key), m2.get(key)
            if v1 != v2:
                result["differences"].append(f"Metadata {key} differs")
    
    result["identical"] = len(result["differences"]) == 0
    return result

def main() -> None:
    """Main entry point for the PDF comparison tool."""
    parser = argparse.ArgumentParser(
        description="Compare two PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python pdf_compare.py doc1.pdf doc2.pdf
    python pdf_compare.py doc1.pdf doc2.pdf --json
    python pdf_compare.py doc1.pdf doc2.pdf -v
        """,
    )
    parser.add_argument("file1", help="First PDF file")
    parser.add_argument("file2", help="Second PDF file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    try:
        result = compare_pdfs(args.file1, args.file2, args.verbose)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["identical"]:
            print("PDFs are identical")
        else:
            print("Differences found:")
            for diff in result["differences"]:
                print(f"  - {diff}")

    sys.exit(0 if result["identical"] else 1)


if __name__ == "__main__":
    main()