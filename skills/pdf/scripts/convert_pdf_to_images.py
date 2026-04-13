#!/usr/bin/env python3
"""
PDF to Images Converter
Convert PDF pages to PNG/JPG images with configurable DPI and format options.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"Error: Required dependencies not installed.")
    print(f"Please install: pip install pdf2image Pillow")
    print(f"Also ensure poppler is installed on your system.")
    sys.exit(1)


def parse_page_range(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of page numbers.

    Args:
        page_range: String like "1-5", "1,3,5", "1-3,5,7-9"
        total_pages: Total number of pages in PDF

    Returns:
        List of 0-indexed page numbers
    """
    pages = []
    parts = page_range.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            # Convert to 0-indexed
            for p in range(start - 1, min(end, total_pages)):
                if p >= 0:
                    pages.append(p)
        else:
            p = int(part) - 1  # Convert to 0-indexed
            if 0 <= p < total_pages:
                pages.append(p)

    return sorted(set(pages))


def convert_pdf_to_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 200,
    fmt: str = "png",
    page_range: Optional[str] = None,
    prefix: Optional[str] = None,
    quality: int = 95
) -> Tuple[List[str], List[str]]:
    """
    Convert PDF to images.

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for images
        dpi: Resolution in DPI
        fmt: Output format (png or jpg/jpeg)
        page_range: Optional page range string
        prefix: Optional filename prefix
        quality: JPEG quality (1-100), only for jpg format

    Returns:
        Tuple of (successful files, error messages)
    """
    errors = []
    output_files = []

    # Validate input file
    if not os.path.exists(pdf_path):
        errors.append(f"File not found: {pdf_path}")
        return [], errors

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get PDF filename for prefix
    pdf_name = Path(pdf_path).stem
    if prefix is None:
        prefix = pdf_name

    # Normalize format
    fmt = fmt.lower()
    if fmt == "jpeg":
        fmt = "jpg"

    try:
        # Convert PDF to images
        print(f"Converting PDF: {pdf_path}")
        print(f"DPI: {dpi}, Format: {fmt}")

        # Get total pages first
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=1,
            last_page=1
        )
        total_pages = len(convert_from_path(pdf_path, dpi=dpi))
        del images

        # Determine which pages to convert
        if page_range:
            page_indices = parse_page_range(page_range, total_pages)
            print(f"Converting pages: {[p + 1 for p in page_indices]}")
        else:
            page_indices = list(range(total_pages))

        if not page_indices:
            errors.append("No valid pages to convert")
            return [], errors

        # Convert pages
        for idx in page_indices:
            page_num = idx + 1
            print(f"Converting page {page_num}...")

            try:
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=page_num,
                    last_page=page_num
                )

                if images:
                    img = images[0]
                    output_file = os.path.join(
                        output_dir,
                        f"{prefix}_page_{page_num:04d}.{fmt}"
                    )

                    if fmt == "jpg":
                        img.save(output_file, "JPEG", quality=quality)
                    else:
                        img.save(output_file, "PNG")

                    output_files.append(output_file)
                    print(f"  Saved: {output_file}")

            except Exception as e:
                errors.append(f"Error converting page {page_num}: {str(e)}")

        return output_files, errors

    except Exception as e:
        errors.append(f"Error processing PDF: {str(e)}")
        return [], errors


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to PNG or JPG images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf -o images/
  %(prog)s document.pdf -o images/ --dpi 300 --format jpg
  %(prog)s document.pdf -o images/ --pages 1-5
  %(prog)s document.pdf -o images/ --pages 1,3,5-7 --prefix mydoc

Notes:
  - Requires poppler-utils to be installed on your system
  - On Windows: download from https://github.com/oschwartz10612/poppler-windows/releases
  - On macOS: brew install poppler
  - On Linux: apt-get install poppler-utils
"""
    )

    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file to convert"
    )

    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        default=".",
        help="Output directory for images (default: current directory)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Image resolution in DPI (default: 200)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["png", "jpg", "jpeg"],
        default="png",
        help="Output image format (default: png)"
    )

    parser.add_argument(
        "-p", "--pages",
        dest="page_range",
        help="Page range to convert (e.g., '1-5', '1,3,5', '1-3,5,7-9')"
    )

    parser.add_argument(
        "--prefix",
        help="Filename prefix for output images (default: PDF filename)"
    )

    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=95,
        help="JPEG quality 1-100 (default: 95, only for jpg format)"
    )

    args = parser.parse_args()

    # Validate DPI
    if args.dpi < 50 or args.dpi > 1200:
        print("Warning: DPI should typically be between 50 and 1200")

    # Validate quality
    if args.quality < 1 or args.quality > 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    # Convert PDF
    output_files, errors = convert_pdf_to_images(
        pdf_path=args.pdf_file,
        output_dir=args.output_dir,
        dpi=args.dpi,
        fmt=args.format,
        page_range=args.page_range,
        prefix=args.prefix,
        quality=args.quality
    )

    # Print summary
    print(f"\nConversion complete!")
    print(f"  Images created: {len(output_files)}")

    if errors:
        print(f"\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"\nOutput files:")
    for f in output_files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
