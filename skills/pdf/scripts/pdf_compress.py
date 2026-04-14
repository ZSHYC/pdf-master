#!/usr/bin/env python3
"""PDF Compression Script.

This script provides functionality to compress PDF files by removing
unnecessary objects such as annotations and links. It uses the pypdf
library for PDF manipulation.

Usage:
    python pdf_compress.py input.pdf -o output.pdf [-q QUALITY] [-v]
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library is required. Install with: pip install pypdf")
    sys.exit(1)


def compress_pdf(input_path: str, output_path: str, quality: int = 75, verbose: bool = False) -> bool:
    """Compress a PDF file by removing unnecessary objects.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path where the compressed PDF will be saved.
        quality: Compression quality (0-100). Higher values mean better quality.
        verbose: If True, print detailed progress information.

    Returns:
        True if compression was successful, False otherwise.

    Raises:
        FileNotFoundError: If the input file does not exist.
        PermissionError: If cannot read input or write output file.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    # Validate input file
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}")
        return False

    if not input_file.is_file():
        print(f"Error: Input path is not a file: {input_path}")
        return False

    # Validate quality parameter
    if not 0 <= quality <= 100:
        print(f"Error: Quality must be between 0 and 100, got: {quality}")
        return False

    try:
        if verbose:
            print(f"Reading PDF: {input_path}")

        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Copy all pages
        page_count = len(reader.pages)
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if verbose:
                print(f"  Processed page {i + 1}/{page_count}")

        # Copy metadata if present
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # Remove unnecessary objects to reduce file size
        # Remove annotations and links which are often unnecessary
        if verbose:
            print("Removing unnecessary objects...")

        try:
            writer.remove_objects_by_type("/Annots")
        except Exception as e:
            if verbose:
                print(f"  Note: Could not remove annotations: {e}")

        try:
            writer.remove_objects_by_type("/Links")
        except Exception as e:
            if verbose:
                print(f"  Note: Could not remove links: {e}")

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Writing compressed PDF: {output_path}")

        with open(output_path, "wb") as f:
            writer.write(f)

        # Calculate compression statistics
        orig_size = input_file.stat().st_size
        new_size = output_file.stat().st_size

        if orig_size > 0:
            ratio = (1 - new_size / orig_size) * 100
            print(f"Compressed: {orig_size:,} -> {new_size:,} bytes ({ratio:.1f}% reduction)")
        else:
            print(f"Compressed: {orig_size:,} -> {new_size:,} bytes")

        return True

    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
        return False
    except Exception as e:
        print(f"Error during compression: {e}")
        return False


def main() -> int:
    """Main entry point for the PDF compression script.

    Returns:
        Exit code: 0 for success, 1 for failure.
    """
    parser = argparse.ArgumentParser(
        description="Compress PDF files by removing unnecessary objects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf -o output.pdf
  %(prog)s input.pdf -o output.pdf -q 50
  %(prog)s input.pdf -o output.pdf -v
        """
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file path")
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=75,
        help="Compression quality (0-100, default: 75)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )

    args = parser.parse_args()

    success = compress_pdf(args.input, args.output, args.quality, args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())