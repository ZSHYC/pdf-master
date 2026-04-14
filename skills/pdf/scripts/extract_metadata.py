#!/usr/bin/env python3
"""
PDF Metadata Extraction Script

Extract metadata from PDF files including:
- Title, Author, Subject, Keywords
- Creator, Producer
- Creation date, Modification date
- Page count, File size
- Encryption status, PDF version
- Permissions

Usage:
    python extract_metadata.py input.pdf
    python extract_metadata.py input.pdf -o metadata.json
    python extract_metadata.py input.pdf --format text
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from pypdf import PdfReader

# Dependency check
MISSING_DEPS = []

try:
    from pypdf import PdfReader
except ImportError:
    MISSING_DEPS.append("pypdf")


def check_dependencies() -> None:
    """Check if required dependencies are installed."""
    if MISSING_DEPS:
        print(f"Error: Missing required dependencies: {', '.join(MISSING_DEPS)}")
        print("Please install them with: pip install " + " ".join(MISSING_DEPS))
        sys.exit(1)


def parse_pdf_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse PDF date format (D:YYYYMMDDHHmmss) to readable format.

    Args:
        date_str: PDF date string

    Returns:
        Formatted date string or None
    """
    if not date_str:
        return None

    try:
        # Remove 'D:' prefix if present
        if date_str.startswith('D:'):
            date_str = date_str[2:]

        # Parse the date components
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(date_str[8:10]) if len(date_str) > 8 else 0
        minute = int(date_str[10:12]) if len(date_str) > 10 else 0
        second = int(date_str[12:14]) if len(date_str) > 12 else 0

        dt = datetime(year, month, day, hour, minute, second)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return date_str


def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing PDF metadata
    """
    pdf_path = Path(pdf_path)
    result = {
        "file_info": {
            "filename": pdf_path.name,
            "path": str(pdf_path.absolute()),
            "size_bytes": pdf_path.stat().st_size,
            "size_human": format_file_size(pdf_path.stat().st_size)
        },
        "document_info": {},
        "technical_info": {},
        "security": {}
    }

    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)

        # Document metadata
        if reader.metadata:
            metadata = reader.metadata
            result["document_info"] = {
                "title": metadata.get('/Title', None),
                "author": metadata.get('/Author', None),
                "subject": metadata.get('/Subject', None),
                "keywords": metadata.get('/Keywords', None),
                "creator": metadata.get('/Creator', None),
                "producer": metadata.get('/Producer', None),
                "creation_date": parse_pdf_date(metadata.get('/CreationDate', None)),
                "modification_date": parse_pdf_date(metadata.get('/ModDate', None))
            }

            # Clean up None values
            result["document_info"] = {k: v for k, v in result["document_info"].items() if v is not None}

        # Technical information
        try:
            has_xmp = reader.xmp_metadata is not None
        except Exception:
            has_xmp = False
        result["technical_info"] = {
            "page_count": len(reader.pages),
            "pdf_version": get_pdf_version(f),
            "is_linear": getattr(reader, 'is_linear', False),
            "xmp_metadata": has_xmp
        }

        # Security information
        result["security"] = {
            "is_encrypted": reader.is_encrypted,
            "permissions": get_permissions(reader) if not reader.is_encrypted else None
        }

        # If encrypted, try to provide more info
        if reader.is_encrypted:
            result["security"]["encryption_info"] = "Document is password protected"
            result["security"]["can_open"] = False
        else:
            result["security"]["can_open"] = True

    return result


def get_pdf_version(file_obj) -> Optional[str]:
    """
    Get PDF version from file header.

    Args:
        file_obj: File object

    Returns:
        PDF version string or None
    """
    try:
        file_obj.seek(0)
        header = file_obj.read(8).decode('latin-1')
        if header.startswith('%PDF-'):
            return header[5:8]
        return None
    except Exception:
        return None


def get_permissions(reader) -> Dict[str, bool]:
    """
    Extract PDF permissions.

    Args:
        reader: PdfReader instance

    Returns:
        Dictionary of permissions
    """
    permissions = {}

    try:
        # Try to get permissions from the reader
        if hasattr(reader, 'permissions'):
            perm = reader.permissions
            permissions = {
                "print": getattr(perm, 'print', True),
                "modify": getattr(perm, 'modify', True),
                "copy": getattr(perm, 'extract', True),
                "annotate": getattr(perm, 'annotate', True),
                "fill_forms": getattr(perm, 'fill_forms', True),
                "extract": getattr(perm, 'extract', True),
                "assemble": getattr(perm, 'assemble', True),
                "print_high_quality": getattr(perm, 'print_high_quality', True)
            }
        else:
            # Default to all allowed if no permission info available
            permissions = {
                "print": True,
                "modify": True,
                "copy": True,
                "annotate": True,
                "fill_forms": True,
                "extract": True,
                "assemble": True,
                "print_high_quality": True
            }
    except Exception:
        permissions = {
            "print": True,
            "modify": True,
            "copy": True,
            "annotate": True,
            "fill_forms": True,
            "extract": True,
            "assemble": True,
            "print_high_quality": True
        }

    return permissions


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def format_as_json(data: Dict[str, Any]) -> str:
    """Format metadata as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_text(data: Dict[str, Any]) -> str:
    """Format metadata as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("PDF METADATA")
    lines.append("=" * 60)

    # File info
    lines.append("\n--- File Information ---")
    file_info = data["file_info"]
    lines.append(f"Filename: {file_info['filename']}")
    lines.append(f"Path: {file_info['path']}")
    lines.append(f"Size: {file_info['size_human']} ({file_info['size_bytes']} bytes)")

    # Document info
    if data["document_info"]:
        lines.append("\n--- Document Information ---")
        for key, value in data["document_info"].items():
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")

    # Technical info
    lines.append("\n--- Technical Information ---")
    tech_info = data["technical_info"]
    lines.append(f"Page Count: {tech_info['page_count']}")
    if tech_info.get('pdf_version'):
        lines.append(f"PDF Version: {tech_info['pdf_version']}")
    lines.append(f"Linear (Fast Web View): {'Yes' if tech_info.get('is_linear') else 'No'}")
    lines.append(f"XMP Metadata: {'Yes' if tech_info.get('xmp_metadata') else 'No'}")

    # Security info
    lines.append("\n--- Security Information ---")
    security = data["security"]
    lines.append(f"Encrypted: {'Yes' if security['is_encrypted'] else 'No'}")

    if security.get('permissions'):
        lines.append("\nPermissions:")
        for key, value in security['permissions'].items():
            label = key.replace('_', ' ').title()
            lines.append(f"  {label}: {'Allowed' if value else 'Restricted'}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def format_as_markdown(data: Dict[str, Any]) -> str:
    """Format metadata as markdown."""
    lines = []
    lines.append(f"# PDF Metadata: {data['file_info']['filename']}")
    lines.append("")

    # File info
    lines.append("## File Information")
    lines.append("")
    file_info = data["file_info"]
    lines.append(f"| Property | Value |")
    lines.append(f"|----------|-------|")
    lines.append(f"| Filename | {file_info['filename']} |")
    lines.append(f"| Path | `{file_info['path']}` |")
    lines.append(f"| Size | {file_info['size_human']} ({file_info['size_bytes']} bytes) |")
    lines.append("")

    # Document info
    if data["document_info"]:
        lines.append("## Document Information")
        lines.append("")
        lines.append(f"| Property | Value |")
        lines.append(f"|----------|-------|")
        for key, value in data["document_info"].items():
            label = key.replace('_', ' ').title()
            lines.append(f"| {label} | {value} |")
        lines.append("")

    # Technical info
    lines.append("## Technical Information")
    lines.append("")
    tech_info = data["technical_info"]
    lines.append(f"| Property | Value |")
    lines.append(f"|----------|-------|")
    lines.append(f"| Page Count | {tech_info['page_count']} |")
    if tech_info.get('pdf_version'):
        lines.append(f"| PDF Version | {tech_info['pdf_version']} |")
    lines.append(f"| Linear (Fast Web View) | {'Yes' if tech_info.get('is_linear') else 'No'} |")
    lines.append(f"| XMP Metadata | {'Yes' if tech_info.get('xmp_metadata') else 'No'} |")
    lines.append("")

    # Security info
    lines.append("## Security Information")
    lines.append("")
    security = data["security"]
    lines.append(f"- **Encrypted:** {'Yes' if security['is_encrypted'] else 'No'}")

    if security.get('permissions'):
        lines.append("")
        lines.append("### Permissions")
        lines.append("")
        for key, value in security['permissions'].items():
            status = "Allowed" if value else "Restricted"
            lines.append(f"- **{key.replace('_', ' ').title()}:** {status}")

    return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract metadata from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf
    %(prog)s document.pdf -o metadata.json
    %(prog)s document.pdf --format markdown
    %(prog)s document.pdf --format text
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["json", "text", "markdown"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--check-encrypted",
        action="store_true",
        help="Only check if PDF is encrypted (exit 0 if not, 1 if encrypted)"
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
        metadata = extract_metadata(str(pdf_path))

        # Quick encryption check mode
        if args.check_encrypted:
            if metadata["security"]["is_encrypted"]:
                print("ENCRYPTED")
                sys.exit(1)
            else:
                print("NOT_ENCRYPTED")
                sys.exit(0)

        # Format output
        formatters = {
            "json": format_as_json,
            "text": format_as_text,
            "markdown": format_as_markdown
        }

        formatter = formatters.get(args.format, format_as_json)
        output = formatter(metadata)

        # Write or print output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"Metadata saved to: {output_path}")
        else:
            print(output)

    except Exception as e:
        print(f"Error extracting metadata: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
