#!/usr/bin/env python3
"""
PDF OCR Script
Perform OCR on scanned PDF documents using Tesseract.
Converts PDF pages to images and extracts text using pytesseract.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
except ImportError as e:
    print("Error: Required dependencies not installed.")
    print("Please install: pip install pytesseract pdf2image Pillow")
    print("\nAlso ensure the following are installed on your system:")
    print("  - Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("  - Poppler: https://github.com/oschwartz10612/poppler-windows/releases")
    sys.exit(1)


def check_tesseract_installed() -> bool:
    """Check if Tesseract is installed and accessible."""
    try:
        version = pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def get_available_languages() -> List[str]:
    """Get list of available Tesseract languages."""
    try:
        langs = pytesseract.get_languages()
        return langs
    except Exception:
        return []


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
            for p in range(start - 1, min(end, total_pages)):
                if p >= 0:
                    pages.append(p)
        else:
            p = int(part) - 1
            if 0 <= p < total_pages:
                pages.append(p)

    return sorted(set(pages))


def ocr_image(image: Image.Image, lang: str = 'eng', config: str = '') -> Dict[str, Any]:
    """
    Perform OCR on a single image.

    Args:
        image: PIL Image object
        lang: Tesseract language code(s)
        config: Additional Tesseract configuration

    Returns:
        Dictionary with OCR results
    """
    try:
        # Get text
        text = pytesseract.image_to_string(image, lang=lang, config=config)

        # Get bounding box data for JSON output
        data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)

        return {
            'text': text.strip(),
            'data': data,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'text': '',
            'data': {},
            'success': False,
            'error': str(e)
        }


def ocr_pdf(
    pdf_path: str,
    lang: str = 'eng',
    dpi: int = 300,
    page_range: Optional[str] = None,
    output_format: str = 'text',
    tesseract_config: str = '',
    output_file: Optional[str] = None
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Perform OCR on a PDF document.

    Args:
        pdf_path: Path to PDF file
        lang: Tesseract language code(s), comma-separated for multiple
        dpi: Resolution for PDF to image conversion
        page_range: Optional page range string
        output_format: Output format ('text' or 'json')
        tesseract_config: Additional Tesseract configuration string
        output_file: Optional output file path

    Returns:
        Tuple of (results dictionary, error messages)
    """
    errors = []
    results = {
        'source_file': pdf_path,
        'language': lang,
        'dpi': dpi,
        'pages': [],
        'full_text': ''
    }

    # Validate input file
    if not os.path.exists(pdf_path):
        errors.append(f"File not found: {pdf_path}")
        return results, errors

    # Check Tesseract
    if not check_tesseract_installed():
        errors.append("Tesseract OCR is not installed or not in PATH.")
        errors.append("Please install Tesseract: https://github.com/tesseract-ocr/tesseract")
        return results, errors

    # Validate language
    available_langs = get_available_languages()
    requested_langs = lang.split('+')

    missing_langs = [l for l in requested_langs if l not in available_langs]
    if missing_langs:
        errors.append(f"Language(s) not available in Tesseract: {', '.join(missing_langs)}")
        errors.append(f"Available languages: {', '.join(available_langs)}")
        return results, errors

    try:
        print(f"Processing PDF: {pdf_path}")
        print(f"Language: {lang}")
        print(f"DPI: {dpi}")

        # Get total pages
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        total_pages = len(convert_from_path(pdf_path, dpi=dpi))
        del images

        print(f"Total pages: {total_pages}")

        # Determine which pages to process
        if page_range:
            page_indices = parse_page_range(page_range, total_pages)
            print(f"Processing pages: {[p + 1 for p in page_indices]}")
        else:
            page_indices = list(range(total_pages))

        if not page_indices:
            errors.append("No valid pages to process")
            return results, errors

        # Process each page
        all_text = []

        for idx in page_indices:
            page_num = idx + 1
            print(f"\nProcessing page {page_num}...")

            try:
                # Convert page to image
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=page_num,
                    last_page=page_num
                )

                if images:
                    img = images[0]

                    # Perform OCR
                    ocr_result = ocr_image(img, lang=lang, config=tesseract_config)

                    page_result = {
                        'page_number': page_num,
                        'text': ocr_result['text'],
                        'success': ocr_result['success'],
                        'error': ocr_result['error']
                    }

                    if output_format == 'json':
                        page_result['data'] = ocr_result['data']

                    results['pages'].append(page_result)

                    if ocr_result['success']:
                        all_text.append(f"--- Page {page_num} ---\n{ocr_result['text']}")
                        print(f"  Extracted {len(ocr_result['text'])} characters")
                    else:
                        print(f"  Error: {ocr_result['error']}")

            except Exception as e:
                errors.append(f"Error processing page {page_num}: {str(e)}")
                results['pages'].append({
                    'page_number': page_num,
                    'text': '',
                    'success': False,
                    'error': str(e)
                })

        # Combine all text
        results['full_text'] = '\n\n'.join(all_text)

        # Output results
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(results['full_text'])

            print(f"\nOutput saved to: {output_file}")

        return results, errors

    except Exception as e:
        errors.append(f"Error processing PDF: {str(e)}")
        return results, errors


def main():
    parser = argparse.ArgumentParser(
        description="Perform OCR on scanned PDF documents using Tesseract.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scanned.pdf
  %(prog)s scanned.pdf --lang chi_sim+eng
  %(prog)s scanned.pdf --lang chi_sim --output result.txt
  %(prog)s scanned.pdf --format json --output result.json
  %(prog)s scanned.pdf --pages 1-5 --dpi 300

Common Language Codes:
  eng    - English
  chi_sim - Chinese (Simplified)
  chi_tra - Chinese (Traditional)
  jpn    - Japanese
  kor    - Korean
  fra    - French
  deu    - German
  spa    - Spanish
  rus    - Russian

Notes:
  - Requires Tesseract OCR to be installed
  - Requires poppler for PDF to image conversion
  - Use '+' to combine multiple languages (e.g., 'eng+chi_sim')
  - Install language packs: tesseract --list-langs
"""
    )

    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file to OCR"
    )

    parser.add_argument(
        "-l", "--lang",
        default="eng",
        help="OCR language code(s), use '+' for multiple (default: eng)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolution for PDF conversion (default: 300)"
    )

    parser.add_argument(
        "-p", "--pages",
        dest="page_range",
        help="Page range to process (e.g., '1-5', '1,3,5', '1-3,5,7-9')"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Output file path (prints to console if not specified)"
    )

    parser.add_argument(
        "--tesseract-config",
        default="",
        help="Additional Tesseract configuration string"
    )

    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="List available Tesseract languages and exit"
    )

    args = parser.parse_args()

    # Handle --list-langs
    if args.list_langs:
        print("Available Tesseract languages:")
        langs = get_available_languages()
        if langs:
            for lang in sorted(langs):
                print(f"  {lang}")
        else:
            print("  Unable to retrieve languages. Is Tesseract installed?")
        sys.exit(0)

    # Perform OCR
    results, errors = ocr_pdf(
        pdf_path=args.pdf_file,
        lang=args.lang,
        dpi=args.dpi,
        page_range=args.page_range,
        output_format=args.format,
        tesseract_config=args.tesseract_config,
        output_file=args.output_file
    )

    # Print output if not saving to file
    if not args.output_file:
        if args.format == 'json':
            print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print("\n" + "=" * 50)
            print("OCR RESULT")
            print("=" * 50)
            print(results['full_text'])

    # Print summary
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Pages processed: {len(results['pages'])}")
    success_count = sum(1 for p in results['pages'] if p.get('success', False))
    print(f"Successful: {success_count}")
    print(f"Total characters: {len(results['full_text'])}")

    if errors:
        print(f"\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
