#!/usr/bin/env python3
"""
PDF Translation Script

Extract text from PDF and translate using AI.

Usage:
    python translate_pdf.py input.pdf -t "Japanese"
    python translate_pdf.py input.pdf -t "Japanese" -s "English" -p openai
    python translate_pdf.py input.pdf -t "Chinese" -o translated.txt
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Import local modules
try:
    from ai_provider import get_ai_provider, list_providers, ProviderType
    from extract_text import extract_text
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ai_provider import get_ai_provider, list_providers, ProviderType
    from extract_text import extract_text


def translate_pdf(
    pdf_path: str,
    target_language: str,
    source_language: Optional[str] = None,
    provider: str = "claude",
    model: Optional[str] = None,
    output_file: Optional[str] = None,
    pages: Optional[str] = None,
    extraction_method: str = "pdfplumber",
    chunk_size: int = 10000
) -> str:
    """
    Translate PDF content using AI.

    Args:
        pdf_path: Path to the PDF file
        target_language: Target language for translation
        source_language: Source language (optional, auto-detected)
        provider: AI provider name
        model: Model name (optional)
        output_file: Output file path (optional)
        pages: Page range to translate (e.g., '1-5', '1,3,5')
        extraction_method: Text extraction method
        chunk_size: Maximum characters per translation chunk

    Returns:
        str: Translated text
    """
    # Validate input file
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"Not a PDF file: {pdf_path}")

    # Extract text from PDF
    print(f"Extracting text from {pdf_path}...")
    text = extract_text(
        pdf_path=str(pdf_path),
        method=extraction_method,
        output_format="text",
        output_file=None,
        pages=pages
    )

    if not text or not text.strip():
        raise ValueError("No text could be extracted from the PDF")

    # Initialize AI provider
    print(f"Initializing AI provider: {provider}")
    ai = get_ai_provider(provider=provider, model=model)

    # Check availability
    if not ai.is_available():
        provider_info = next(
            (p for p in list_providers() if p["name"] == provider),
            None
        )
        if provider_info and provider_info.get("env_key"):
            raise RuntimeError(
                f"AI provider '{provider}' is not available. "
                f"Please set the {provider_info['env_key']} environment variable."
            )
        else:
            raise RuntimeError(f"AI provider '{provider}' is not available.")

    # Translate text (chunked if necessary)
    print(f"Translating to {target_language} using {ai.provider_name} ({ai.model})...")

    if len(text) <= chunk_size:
        # Single translation
        translated = ai.translate(
            text,
            target_language=target_language,
            source_language=source_language
        )
    else:
        # Chunked translation
        print(f"Text is long ({len(text)} chars), translating in chunks...")
        translated_chunks = []
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for i, chunk in enumerate(chunks, 1):
            print(f"  Translating chunk {i}/{len(chunks)}...")
            translated_chunk = ai.translate(
                chunk,
                target_language=target_language,
                source_language=source_language
            )
            translated_chunks.append(translated_chunk)

        translated = "\n\n".join(translated_chunks)

    # Output result
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(translated, encoding='utf-8')
        print(f"Translation saved to: {output_path}")
    else:
        print("\n" + "=" * 50)
        print("TRANSLATION")
        print("=" * 50)
        print(translated)
        print("=" * 50)

    return translated


def main():
    """Command-line interface."""
    providers = list_providers()
    provider_names = [p["name"] for p in providers]

    parser = argparse.ArgumentParser(
        description="Translate PDF content using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported AI providers:
  {', '.join(provider_names)}

Examples:
    %(prog)s document.pdf -t "Japanese"
    %(prog)s document.pdf -t "Chinese" -s "English"
    %(prog)s document.pdf -t "Spanish" -o translated.txt
    %(prog)s document.pdf -t "French" -p openai -m gpt-4o
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Target language for translation (e.g., 'Chinese', 'Japanese', 'Spanish')"
    )

    parser.add_argument(
        "-s", "--source",
        help="Source language (optional, auto-detected if not specified)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to console)"
    )

    parser.add_argument(
        "-p", "--provider",
        choices=provider_names,
        default="claude",
        help="AI provider to use (default: claude)"
    )

    parser.add_argument(
        "-m", "--model",
        help="Model name (optional, uses provider default)"
    )

    parser.add_argument(
        "--pages",
        help="Page range to translate (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--extraction-method",
        choices=["pypdf", "pdfplumber"],
        default="pdfplumber",
        help="Text extraction method (default: pdfplumber)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10000,
        help="Maximum characters per translation chunk (default: 10000)"
    )

    args = parser.parse_args()

    try:
        translate_pdf(
            pdf_path=args.input,
            target_language=args.target,
            source_language=args.source,
            provider=args.provider,
            model=args.model,
            output_file=args.output,
            pages=args.pages,
            extraction_method=args.extraction_method,
            chunk_size=args.chunk_size
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error translating PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
