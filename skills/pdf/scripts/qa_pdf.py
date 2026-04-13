#!/usr/bin/env python3
"""
PDF Question-Answering Script

Extract text from PDF and answer questions based on the content.

Usage:
    python qa_pdf.py input.pdf "What is the main topic?"
    python qa_pdf.py input.pdf "Summarize the key findings" -p openai
    python qa_pdf.py input.pdf "What are the conclusions?" -o answer.txt
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


def qa_pdf(
    pdf_path: str,
    question: str,
    provider: str = "claude",
    model: Optional[str] = None,
    language: str = "zh",
    output_file: Optional[str] = None,
    pages: Optional[str] = None,
    extraction_method: str = "pdfplumber"
) -> str:
    """
    Answer questions based on PDF content using AI.

    Args:
        pdf_path: Path to the PDF file
        question: Question to answer
        provider: AI provider name
        model: Model name (optional)
        language: Response language (zh/en)
        output_file: Output file path (optional)
        pages: Page range to use as context (e.g., '1-5', '1,3,5')
        extraction_method: Text extraction method

    Returns:
        str: Answer to the question
    """
    # Validate input file
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"Not a PDF file: {pdf_path}")

    # Validate question
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

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
    max_input_chars = 100000
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

    # Generate answer
    print(f"Answering question using {ai.provider_name} ({ai.model})...")
    answer = ai.qa(question, context=text, language=language)

    # Output result
    if output_file:
        output_path = Path(output_file)
        output_content = f"Question: {question}\n\nAnswer: {answer}"
        output_path.write_text(output_content, encoding='utf-8')
        print(f"Answer saved to: {output_path}")
    else:
        print("\n" + "=" * 50)
        print("QUESTION")
        print("=" * 50)
        print(question)
        print("\n" + "=" * 50)
        print("ANSWER")
        print("=" * 50)
        print(answer)
        print("=" * 50)

    return answer


def interactive_mode(
    pdf_path: str,
    provider: str = "claude",
    model: Optional[str] = None,
    language: str = "zh",
    pages: Optional[str] = None,
    extraction_method: str = "pdfplumber"
):
    """
    Interactive Q&A mode for continuous questioning.

    Args:
        pdf_path: Path to the PDF file
        provider: AI provider name
        model: Model name (optional)
        language: Response language
        pages: Page range to use as context
        extraction_method: Text extraction method
    """
    # Validate and extract once
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

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

    # Truncate if too long
    max_input_chars = 100000
    if len(text) > max_input_chars:
        print(f"Warning: Text too long ({len(text)} chars), truncating to {max_input_chars} chars")
        text = text[:max_input_chars] + "\n... [text truncated]"

    # Initialize AI provider
    print(f"Initializing AI provider: {provider}")
    ai = get_ai_provider(provider=provider, model=model)

    if not ai.is_available():
        raise RuntimeError(f"AI provider '{provider}' is not available.")

    print("\n" + "=" * 50)
    print("INTERACTIVE Q&A MODE")
    print("=" * 50)
    print(f"Document: {pdf_path.name}")
    print(f"Provider: {ai.provider_name} ({ai.model})")
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("=" * 50 + "\n")

    while True:
        try:
            question = input("Question: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            print("\nAnswering...")
            answer = ai.qa(question, context=text, language=language)

            print("\n" + "-" * 50)
            print("Answer:")
            print("-" * 50)
            print(answer)
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    """Command-line interface."""
    providers = list_providers()
    provider_names = [p["name"] for p in providers]

    parser = argparse.ArgumentParser(
        description="Answer questions based on PDF content using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported AI providers:
  {', '.join(provider_names)}

Examples:
    %(prog)s document.pdf "What is the main topic?"
    %(prog)s document.pdf "Summarize the key findings" -l en
    %(prog)s document.pdf "What are the conclusions?" -o answer.txt
    %(prog)s document.pdf --interactive  # Interactive Q&A mode
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "question",
        nargs="?",
        help="Question to answer (required unless --interactive is used)"
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
        help="Response language (default: zh)"
    )

    parser.add_argument(
        "--pages",
        help="Page range to use as context (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--extraction-method",
        choices=["pypdf", "pdfplumber"],
        default="pdfplumber",
        help="Text extraction method (default: pdfplumber)"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive Q&A mode for continuous questioning"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.interactive and not args.question:
        parser.error("question is required unless --interactive is used")

    try:
        if args.interactive:
            interactive_mode(
                pdf_path=args.input,
                provider=args.provider,
                model=args.model,
                language=args.language,
                pages=args.pages,
                extraction_method=args.extraction_method
            )
        else:
            qa_pdf(
                pdf_path=args.input,
                question=args.question,
                provider=args.provider,
                model=args.model,
                language=args.language,
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
        print(f"Error answering question: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
