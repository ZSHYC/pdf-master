#!/usr/bin/env python3
"""
PDF Summarization Script

Extract text from PDF and generate AI-powered summary.

Usage:
    python summarize_pdf.py input.pdf
    python summarize_pdf.py input.pdf -l en -p claude -m claude-3-5-sonnet-20241022
    python summarize_pdf.py input.pdf -o summary.txt --max-length 300
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
    # Handle case when run from different directory
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ai_provider import get_ai_provider, list_providers, ProviderType
    from extract_text import extract_text


def summarize_pdf(
    pdf_path: str,
    provider: str = "claude",
    model: Optional[str] = None,
    language: str = "zh",
    max_length: int = 500,
    output_file: Optional[str] = None,
    pages: Optional[str] = None,
    extraction_method: str = "pdfplumber"
) -> str:
    """
    Summarize PDF content using AI.

    Args:
        pdf_path: Path to the PDF file
        provider: AI provider name (claude, openai, gemini, deepseek, qwen, zhipu, moonshot, ollama)
        model: Model name (optional, uses provider default)
        language: Summary language (zh/en)
        max_length: Maximum summary length in characters
        output_file: Output file path (optional)
        pages: Page range to summarize (e.g., '1-5', '1,3,5')
        extraction_method: Text extraction method ('pypdf' or 'pdfplumber')

    Returns:
        str: Generated summary
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

    # Truncate if too long (to avoid token limits)
    max_input_chars = 50000
    if len(text) > max_input_chars:
        print(f"Warning: Text too long ({len(text)} chars), truncating to {max_input_chars} chars")
        text = text[:max_input_chars] + "\n... [text truncated]"

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

    # Generate summary
    print(f"Generating summary using {ai.provider_name} ({ai.model})...")
    summary = ai.summarize(text, language=language, max_length=max_length)

    # Output result
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(summary, encoding='utf-8')
        print(f"Summary saved to: {output_path}")
    else:
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(summary)
        print("=" * 50)

    return summary


def main():
    """Command-line interface."""
    # Get available providers
    providers = list_providers()
    provider_names = [p["name"] for p in providers]

    parser = argparse.ArgumentParser(
        description="Summarize PDF content using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported AI providers:
  {', '.join(provider_names)}

Examples:
    %(prog)s document.pdf
    %(prog)s document.pdf -l en -p openai
    %(prog)s document.pdf -o summary.txt --max-length 300
    %(prog)s document.pdf -p 1-10  # Summarize first 10 pages only
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
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
        "-l", "--language",
        choices=["zh", "en"],
        default="zh",
        help="Summary language (default: zh)"
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=500,
        help="Maximum summary length in characters (default: 500)"
    )

    parser.add_argument(
        "--pages",
        help="Page range to summarize (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--extraction-method",
        choices=["pypdf", "pdfplumber"],
        default="pdfplumber",
        help="Text extraction method (default: pdfplumber)"
    )

    args = parser.parse_args()

    try:
        summarize_pdf(
            pdf_path=args.input,
            provider=args.provider,
            model=args.model,
            language=args.language,
            max_length=args.max_length,
            output_file=args.output,
            pages=args.pages,
            extraction_method=args.extraction_method
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
        print(f"Error generating summary: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
