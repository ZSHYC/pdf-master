#!/usr/bin/env python3
"""
PDF Table Extraction Script

Extract tables from PDF files with support for multiple output formats:
- json: Structured JSON output
- csv: CSV file output
- excel: Excel file output

Usage:
    python extract_tables.py input.pdf -o tables.json
    python extract_tables.py input.pdf -f csv -o tables.csv
    python extract_tables.py input.pdf -f excel -o tables.xlsx
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Dependency check
MISSING_DEPS = []

try:
    import pdfplumber
except ImportError:
    MISSING_DEPS.append("pdfplumber")

try:
    import pandas as pd
except ImportError:
    MISSING_DEPS.append("pandas")


def check_dependencies() -> None:
    """Check if required dependencies are installed."""
    if MISSING_DEPS:
        print(f"Error: Missing required dependencies: {', '.join(MISSING_DEPS)}")
        print("Please install them with: pip install " + " ".join(MISSING_DEPS))
        sys.exit(1)


def extract_tables(
    pdf_path: str,
    pages: Optional[str] = None,
    table_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        pages: Page range specification (optional)
        table_settings: Custom table extraction settings

    Returns:
        Dictionary containing extracted tables
    """
    result = {
        "source": pdf_path,
        "total_tables": 0,
        "pages": []
    }

    # Default table settings
    settings = table_settings or {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines"
    }

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        page_numbers = parse_page_range(pages, total_pages) if pages else range(1, total_pages + 1)

        for page_num in page_numbers:
            if page_num > total_pages:
                continue

            page = pdf.pages[page_num - 1]
            tables = page.extract_tables(table_settings=settings)

            if tables:
                page_data = {
                    "page_number": page_num,
                    "tables": []
                }

                for i, table in enumerate(tables):
                    if table:
                        # Clean table data
                        cleaned_table = []
                        for row in table:
                            cleaned_row = [cell.strip() if cell else "" for cell in row]
                            cleaned_table.append(cleaned_row)

                        page_data["tables"].append({
                            "table_number": i + 1,
                            "rows": len(cleaned_table),
                            "columns": len(cleaned_table[0]) if cleaned_table else 0,
                            "data": cleaned_table
                        })

                if page_data["tables"]:
                    result["pages"].append(page_data)
                    result["total_tables"] += len(page_data["tables"])

    return result


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


def format_as_json(data: Dict[str, Any]) -> str:
    """Format extracted tables as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_csv(data: Dict[str, Any]) -> str:
    """Format extracted tables as CSV (first table only, or combined)."""
    lines = []

    for page in data["pages"]:
        for table in page["tables"]:
            lines.append(f"# Page {page['page_number']}, Table {table['table_number']}")
            for row in table["data"]:
                # CSV format: quote fields containing commas
                formatted_row = []
                for cell in row:
                    if ',' in cell or '"' in cell or '\n' in cell:
                        cell = '"' + cell.replace('"', '""') + '"'
                    formatted_row.append(cell)
                lines.append(','.join(formatted_row))
            lines.append("")

    return '\n'.join(lines)


def save_as_excel(data: Dict[str, Any], output_path: str) -> None:
    """Save extracted tables to an Excel file."""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        sheet_count = 0

        for page in data["pages"]:
            for table in page["tables"]:
                if table["data"]:
                    df = pd.DataFrame(table["data"])

                    # Use first row as header if it looks like headers
                    if len(df) > 0:
                        # Check if first row looks like headers (no numeric patterns)
                        first_row = df.iloc[0]
                        df.columns = first_row
                        df = df.iloc[1:].reset_index(drop=True)

                    sheet_name = f"Page{page['page_number']}_T{table['table_number']}"
                    # Excel sheet name max 31 chars
                    sheet_name = sheet_name[:31]

                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheet_count += 1

        if sheet_count == 0:
            # Create empty sheet if no tables found
            pd.DataFrame().to_excel(writer, sheet_name="No Tables", index=False)


def extract_and_save(
    pdf_path: str,
    output_format: str = "json",
    output_file: Optional[str] = None,
    pages: Optional[str] = None,
    table_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main extraction and save function.

    Args:
        pdf_path: Path to the PDF file
        output_format: Output format ('json', 'csv', 'excel')
        output_file: Output file path
        pages: Page range to extract
        table_settings: Custom table settings

    Returns:
        Extracted data dictionary
    """
    # Validate input
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"Not a PDF file: {pdf_path}")

    # Extract tables
    data = extract_tables(str(pdf_path), pages, table_settings)

    if data["total_tables"] == 0:
        print("Warning: No tables found in the PDF.", file=sys.stderr)

    # Generate default output filename if not specified
    if not output_file:
        extensions = {"json": ".json", "csv": ".csv", "excel": ".xlsx"}
        output_file = str(pdf_path.with_suffix(extensions.get(output_format, ".json")))

    # Save output
    if output_format == "json":
        output = format_as_json(data)
        Path(output_file).write_text(output, encoding='utf-8')
        print(f"Tables saved to: {output_file}")

    elif output_format == "csv":
        output = format_as_csv(data)
        Path(output_file).write_text(output, encoding='utf-8')
        print(f"Tables saved to: {output_file}")

    elif output_format == "excel":
        save_as_excel(data, output_file)
        print(f"Tables saved to: {output_file}")

    # Print summary
    print(f"Extracted {data['total_tables']} table(s) from {len(data['pages'])} page(s)")

    return data


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf
    %(prog)s document.pdf -f csv -o tables.csv
    %(prog)s document.pdf -f excel -o tables.xlsx
    %(prog)s document.pdf -p 1-5 -f json

Table Settings (JSON format):
    --settings '{"vertical_strategy": "text", "horizontal_strategy": "text"}'
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "excel"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "-p", "--pages",
        help="Page range to extract (e.g., '1-5', '1,3,5')"
    )

    parser.add_argument(
        "--settings",
        help="Table extraction settings (JSON format)"
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout (only for json/csv formats)"
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    # Parse table settings
    table_settings = None
    if args.settings:
        try:
            table_settings = json.loads(args.settings)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in settings: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        data = extract_and_save(
            pdf_path=args.input,
            output_format=args.format,
            output_file=None if args.stdout else args.output,
            pages=args.pages,
            table_settings=table_settings
        )

        if args.stdout and args.format in ["json", "csv"]:
            if args.format == "json":
                print(format_as_json(data))
            else:
                print(format_as_csv(data))

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting tables: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
