#!/usr/bin/env python3
"""
PDF Image Extraction Script

Extract images from PDF files and save them to disk.

Usage:
    python extract_images.py input.pdf -o ./images
    python extract_images.py input.pdf -o ./output --format png
    python extract_images.py input.pdf -p 1-5 -o ./images
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Dependency check
MISSING_DEPS = []

try:
    from pypdf import PdfReader
except ImportError:
    MISSING_DEPS.append("pypdf")

try:
    from PIL import Image
except ImportError:
    MISSING_DEPS.append("Pillow")


def check_dependencies() -> None:
    """Check if required dependencies are installed."""
    if MISSING_DEPS:
        print(f"Error: Missing required dependencies: {', '.join(MISSING_DEPS)}")
        print("Please install them with: pip install " + " ".join(MISSING_DEPS))
        sys.exit(1)


def extract_images(
    pdf_path: str,
    output_dir: str,
    image_format: str = "png",
    pages: Optional[str] = None,
    min_size: int = 100,
    prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract images from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        image_format: Output image format (png, jpg, jpeg)
        pages: Page range specification (optional)
        min_size: Minimum image size in bytes to extract
        prefix: Filename prefix for extracted images

    Returns:
        Dictionary containing extraction results
    """
    result = {
        "source": pdf_path,
        "output_directory": output_dir,
        "total_images": 0,
        "extracted_images": [],
        "pages_processed": 0
    }

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set filename prefix
    if prefix is None:
        prefix = Path(pdf_path).stem

    # Read PDF
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    result["total_pages"] = total_pages

    # Determine page numbers to process
    if pages:
        page_numbers = parse_page_range(pages, total_pages)
    else:
        page_numbers = range(1, total_pages + 1)

    # Normalize format
    img_format = image_format.lower()
    if img_format == "jpg":
        img_format = "jpeg"

    valid_formats = ["png", "jpeg"]
    if img_format not in valid_formats:
        print(f"Warning: Unsupported format '{image_format}', using 'png'", file=sys.stderr)
        img_format = "png"

    # Process each page
    for page_num in page_numbers:
        if page_num > total_pages:
            continue

        page = reader.pages[page_num - 1]
        result["pages_processed"] += 1

        if '/Resources' not in page or '/XObject' not in page['/Resources']:
            continue

        x_object = page['/Resources']['/XObject'].get_object()

        image_count = 0
        for obj_name in x_object:
            obj = x_object[obj_name]

            if obj.get('/Subtype') == '/Image':
                try:
                    # Extract image data
                    image_data = extract_image_data(obj)

                    if image_data is None:
                        continue

                    # Check size
                    if len(image_data) < min_size:
                        continue

                    # Save image
                    image_filename = f"{prefix}_p{page_num:03d}_img{image_count + 1}.{img_format}"
                    image_path = output_path / image_filename

                    # Convert and save
                    img = convert_to_pil(obj, image_data)
                    if img:
                        if img_format == "jpeg" and img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        img.save(str(image_path), img_format.upper())

                        result["extracted_images"].append({
                            "filename": image_filename,
                            "page": page_num,
                            "index": image_count + 1,
                            "size_bytes": image_path.stat().st_size,
                            "dimensions": f"{img.width}x{img.height}"
                        })
                        result["total_images"] += 1
                        image_count += 1

                except Exception as e:
                    print(f"Warning: Could not extract image on page {page_num}: {e}", file=sys.stderr)
                    continue

    return result


def extract_image_data(xobject) -> Optional[bytes]:
    """
    Extract raw image data from PDF XObject.

    Args:
        xobject: PDF XObject containing image

    Returns:
        Raw image bytes or None
    """
    try:
        # Try to get the image data directly
        if hasattr(xobject, 'get_data'):
            return xobject.get_data()
        elif hasattr(xobject, '_data'):
            return xobject._data
        elif '/Filter' in xobject:
            # Handle compressed images
            filters = xobject['/Filter']
            if isinstance(filters, list):
                # Multiple filters - complex case
                return None
            return xobject.get_data()
        return None
    except Exception:
        return None


def convert_to_pil(xobject, data: bytes) -> Optional[Image.Image]:
    """
    Convert PDF image object to PIL Image.

    Args:
        xobject: PDF XObject containing image
        data: Raw image data

    Returns:
        PIL Image object or None
    """
    try:
        from PIL import Image
        import io

        # Try direct conversion first
        try:
            return Image.open(io.BytesIO(data))
        except Exception:
            pass

        # Get image properties
        width = xobject.get('/Width', 0)
        height = xobject.get('/Height', 0)
        color_space = xobject.get('/ColorSpace')
        bits_per_component = xobject.get('/BitsPerComponent', 8)
        filters = xobject.get('/Filter')

        # Handle different color spaces
        mode = "RGB"
        if color_space == '/DeviceGray':
            mode = "L"
        elif color_space == '/DeviceCMYK':
            mode = "CMYK"
        elif color_space == '/DeviceRGB':
            mode = "RGB"

        # Handle DCTDecode (JPEG)
        if filters == '/DCTDecode':
            return Image.open(io.BytesIO(data))

        # Handle FlateDecode
        if filters == '/FlateDecode':
            try:
                img = Image.frombytes(mode, (width, height), data)
                return img
            except Exception:
                pass

        # Handle raw bytes
        try:
            img = Image.frombytes(mode, (width, height), data)
            return img
        except Exception:
            pass

        return None

    except Exception as e:
        return None


def parse_page_range(page_spec: str, total_pages: int) -> List[int]:
    """
    Parse page range specification.

    Args:
        page_spec: Page range string (e.g., '1-5', '1,3,5')
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

    valid_pages = [p for p in pages if 1 <= p <= total_pages]
    return sorted(valid_pages)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract images from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf -o ./images
    %(prog)s document.pdf -o ./output --format jpg
    %(prog)s document.pdf -p 1-5 -o ./images
    %(prog)s document.pdf -o ./output --min-size 1000
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-o", "--output",
        default="./extracted_images",
        help="Output directory for extracted images (default: ./extracted_images)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["png", "jpg", "jpeg"],
        default="png",
        help="Output image format (default: png)"
    )

    parser.add_argument(
        "-p", "--pages",
        help="Page range to extract (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--min-size",
        type=int,
        default=100,
        help="Minimum image size in bytes to extract (default: 100)"
    )

    parser.add_argument(
        "--prefix",
        help="Filename prefix for extracted images (default: PDF filename)"
    )

    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    # Validate input
    pdf_path = Path(args.input)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"Error: Not a PDF file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        import json

        result = extract_images(
            pdf_path=str(pdf_path),
            output_dir=args.output,
            image_format=args.format,
            pages=args.pages,
            min_size=args.min_size,
            prefix=args.prefix
        )

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Extraction complete!")
            print(f"  Output directory: {result['output_directory']}")
            print(f"  Pages processed: {result['pages_processed']}")
            print(f"  Images extracted: {result['total_images']}")

            if result['total_images'] > 0:
                print("\nExtracted images:")
                for img in result['extracted_images']:
                    print(f"  - {img['filename']} ({img['dimensions']}, {img['size_bytes']} bytes)")

    except Exception as e:
        print(f"Error extracting images: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
