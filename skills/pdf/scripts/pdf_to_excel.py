#!/usr/bin/env python3
"""
PDF to Excel Converter
Extract tables from PDF and save to Excel format.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed.")
    print("Please install: pip install pdfplumber")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed.")
    print("Please install: pip install pandas")
    sys.exit(1)

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl not installed.")
    print("Please install: pip install openpyxl")
    sys.exit(1)


def extract_tables_from_pdf(
    pdf_path: str,
    pages: Optional[List[int]] = None,
    table_settings: Optional[dict] = None
) -> List[Tuple[int, int, pd.DataFrame]]:
    """
    Extract tables from PDF file.

    Args:
        pdf_path: Path to PDF file
        pages: List of page numbers to extract (0-indexed), None for all
        table_settings: Optional table extraction settings

    Returns:
        List of tuples (page_num, table_index, dataframe)
    """
    tables_data = []

    if table_settings is None:
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines"
        }

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        # Determine which pages to process
        if pages is None:
            pages_to_process = range(total_pages)
        else:
            pages_to_process = [p for p in pages if 0 <= p < total_pages]

        for page_num in pages_to_process:
            page = pdf.pages[page_num]
            tables = page.extract_tables(table_settings=table_settings)

            for table_idx, table in enumerate(tables):
                if table and len(table) > 0:
                    # Convert to DataFrame
                    # First row as header if it looks like headers
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables_data.append((page_num + 1, table_idx + 1, df))

    return tables_data


def save_to_excel(
    tables_data: List[Tuple[int, int, pd.DataFrame]],
    output_path: str,
    multi_sheet: bool = True
) -> Tuple[int, List[str]]:
    """
    Save extracted tables to Excel file.

    Args:
        tables_data: List of (page, index, dataframe) tuples
        output_path: Output Excel file path
        multi_sheet: If True, each table on separate sheet; else all on one sheet

    Returns:
        Tuple of (number of tables saved, list of error messages)
    """
    errors = []

    if not tables_data:
        errors.append("No tables found to save")
        return 0, errors

    try:
        if multi_sheet:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for page_num, table_idx, df in tables_data:
                    sheet_name = f"Page{page_num}_Table{table_idx}"
                    # Excel sheet name max 31 chars
                    sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Combine all tables into one sheet with labels
            all_dfs = []
            for page_num, table_idx, df in tables_data:
                # Add a label row before each table
                label_df = pd.DataFrame([[f"=== Page {page_num}, Table {table_idx} ==="]],
                                         columns=[''])
                all_dfs.append(label_df)
                all_dfs.append(df)
                all_dfs.append(pd.DataFrame())  # Empty row separator

            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df.to_excel(output_path, index=False, engine='openpyxl')

        return len(tables_data), errors

    except Exception as e:
        errors.append(f"Error saving Excel file: {str(e)}")
        return 0, errors


def parse_page_range(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of 0-indexed page numbers.

    Args:
        page_range: String like "1-5", "1,3,5", "1-3,5,7-9"
        total_pages: Total number of pages

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


def main():
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF and save to Excel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf -o tables.xlsx
  %(prog)s document.pdf -o tables.xlsx --pages 1-5
  %(prog)s document.pdf -o tables.xlsx --single-sheet
  %(prog)s document.pdf -o tables.xlsx --strategy text

Table detection strategies:
  - lines: Use detected lines (default, best for bordered tables)
  - text: Use text positioning (better for borderless tables)
"""
    )

    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file"
    )

    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        required=True,
        help="Output Excel file path (required)"
    )

    parser.add_argument(
        "-p", "--pages",
        dest="page_range",
        help="Page range to extract (e.g., '1-5', '1,3,5', '1-3,5,7-9')"
    )

    parser.add_argument(
        "--single-sheet",
        action="store_true",
        help="Put all tables on a single sheet instead of separate sheets"
    )

    parser.add_argument(
        "--strategy",
        choices=["lines", "text", "explicit"],
        default="lines",
        help="Table detection strategy (default: lines)"
    )

    parser.add_argument(
        "--min-rows",
        type=int,
        default=2,
        help="Minimum rows for a table to be extracted (default: 2)"
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.pdf_file):
        print(f"Error: File not found: {args.pdf_file}")
        sys.exit(1)

    # Build table settings
    table_settings = {
        "vertical_strategy": args.strategy,
        "horizontal_strategy": args.strategy
    }

    # Get total pages and parse page range
    with pdfplumber.open(args.pdf_file) as pdf:
        total_pages = len(pdf.pages)

    pages = None
    if args.page_range:
        pages = parse_page_range(args.page_range, total_pages)
        print(f"Processing pages: {[p + 1 for p in pages]}")
    else:
        print(f"Processing all {total_pages} pages")

    # Extract tables
    print(f"\nExtracting tables from: {args.pdf_file}")
    print(f"Strategy: {args.strategy}")

    tables_data = extract_tables_from_pdf(
        pdf_path=args.pdf_file,
        pages=pages,
        table_settings=table_settings
    )

    # Filter by minimum rows
    tables_data = [(p, t, df) for p, t, df in tables_data if len(df) >= args.min_rows]

    if not tables_data:
        print("\nNo tables found in the specified pages.")
        print("Try different strategies:")
        print("  --strategy lines  (for bordered tables)")
        print("  --strategy text   (for borderless tables)")
        sys.exit(0)

    print(f"\nFound {len(tables_data)} table(s):")
    for page_num, table_idx, df in tables_data:
        print(f"  Page {page_num}, Table {table_idx}: {len(df)} rows x {len(df.columns)} columns")

    # Save to Excel
    print(f"\nSaving to: {args.output_file}")
    saved_count, errors = save_to_excel(
        tables_data=tables_data,
        output_path=args.output_file,
        multi_sheet=not args.single_sheet
    )

    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"\nSuccessfully saved {saved_count} table(s) to {args.output_file}")


if __name__ == "__main__":
    main()
