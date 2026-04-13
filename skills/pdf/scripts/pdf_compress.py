#!/usr/bin/env python3
import argparse, sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: Missing pypdf"); sys.exit(1)

def compress_pdf(input_path: str, output_path: str, quality: int = 75, verbose: bool = False):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    writer.remove_objects_by_type(pdf_object_type="/")
    with open(output_path, "wb") as f:
        writer.write(f)
    orig_size = Path(input_path).stat().st_size
    new_size = Path(output_path).stat().st_size
    ratio = (1 - new_size/orig_size) * 100 if orig_size > 0 else 0
    print(f"Compressed: {orig_size} -> {new_size} bytes ({ratio:.1f}% reduction)")

def main():
    parser = argparse.ArgumentParser(description="Compress PDF files")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    parser.add_argument("-q", "--quality", type=int, default=75, help="Quality (0-100)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    compress_pdf(args.input, args.output, args.quality, args.verbose)

if __name__ == "__main__": main()