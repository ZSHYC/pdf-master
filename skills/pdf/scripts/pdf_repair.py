#!/usr/bin/env python3
"""PDF Repair Script.

This module provides functionality to repair corrupted or damaged PDF files
using multiple PDF libraries (pikepdf as primary, pypdf as fallback).

Usage:
    python pdf_repair.py input.pdf -o output.pdf
    python pdf_repair.py input.pdf -o output.pdf -v  # verbose mode
"""

import argparse
import os
import sys
from pathlib import Path

HAS_PIKEPDF = False
try:
    import pikepdf
    HAS_PIKEPDF = True
except ImportError:
    pass

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: Missing pypdf. Install with: pip install pypdf")
    sys.exit(1)

def validate_pdf_path(file_path: str, must_exist: bool = True) -> Path:
    """Validate a PDF file path.

    Args:
        file_path: Path to validate.
        must_exist: If True, the file must exist.

    Returns:
        Validated Path object.

    Raises:
        ValueError: If the path is invalid or file doesn't exist.
    """
    if not file_path:
        raise ValueError("File path cannot be empty")

    path = Path(file_path)

    if must_exist and not path.exists():
        raise ValueError(f"File does not exist: {file_path}")

    if must_exist and not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Validate extension
    if path.suffix.lower() != '.pdf':
        raise ValueError(f"File must have .pdf extension: {file_path}")

    return path


def repair_pdf(input_path: str, output_path: str, verbose: bool = False) -> bool:
    """Repair a corrupted or damaged PDF file.

    Attempts repair using pikepdf first (better recovery), falls back to pypdf.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path for the repaired output PDF file.
        verbose: If True, print detailed progress messages.

    Returns:
        True if repair succeeded, False otherwise.

    Raises:
        ValueError: If input validation fails.
    """
    # Validate input parameters
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean")

    # Validate file paths
    input_file = validate_pdf_path(input_path, must_exist=True)
    output_file = validate_pdf_path(output_path, must_exist=False)

    # Check output directory exists
    output_dir = output_file.parent
    if not output_dir.exists():
        raise ValueError(f"Output directory does not exist: {output_dir}")

    # Check input file is readable
    if not os.access(input_file, os.R_OK):
        raise ValueError(f"Input file is not readable: {input_path}")

    if HAS_PIKEPDF:
        try:
            pdf = pikepdf.open(input_path, allow_overwriting_input=False)
            pdf.save(output_path)
            pdf.close()
            print(f"Repaired with pikepdf: {output_path}")
            return True
        except Exception as e:
            if verbose:
                print(f"pikepdf failed: {e}, trying pypdf")
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Repaired with pypdf: {output_path}")
        return True
    except Exception as e:
        print(f"Repair failed: {e}")
        return False

def main():
    """Parse command-line arguments and execute PDF repair."""
    parser = argparse.ArgumentParser(
        description="Repair corrupted or damaged PDF files"
    )
    parser.add_argument(
        "input",
        help="Input PDF file path"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output PDF file path"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()

    try:
        success = repair_pdf(args.input, args.output, args.verbose)
        sys.exit(0 if success else 1)
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()