#!/usr/bin/env python3
"""
PDF Fillable Fields Check Script

Check if a PDF has fillable form fields (AcroForm).
Lists all field names and types.

Usage:
    python check_fillable_fields.py input.pdf
    python check_fillable_fields.py input.pdf -o fields.json
    python check_fillable_fields.py input.pdf --format text
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, TYPE_CHECKING

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


def get_field_type(field: Dict[str, Any]) -> str:
    """
    Get the type of a form field.

    Args:
        field: Form field dictionary

    Returns:
        Field type string
    """
    ft = field.get("/FT")
    if ft == "/Tx":
        return "text"
    elif ft == "/Btn":
        # Determine button subtype
        flags = field.get("/Ff", 0)
        if isinstance(flags, int):
            if flags & 0x10000:  # Push button
                return "button"
            elif flags & 0x8000:  # Radio button
                return "radio"
            else:  # Checkbox
                return "checkbox"
        return "button"
    elif ft == "/Ch":
        # Choice field (dropdown or list)
        flags = field.get("/Ff", 0)
        if isinstance(flags, int) and flags & 0x20000:  # Combo box
            return "dropdown"
        else:  # List box
            return "list"
    elif ft == "/Sig":
        return "signature"
    else:
        return "unknown"


def get_field_name(field: Dict[str, Any], parent_name: str = "") -> str:
    """
    Get the full name of a form field.

    Args:
        field: Form field dictionary
        parent_name: Parent field name for hierarchical fields

    Returns:
        Full field name
    """
    name = field.get("/T", "")
    if isinstance(name, bytes):
        name = name.decode('utf-8', errors='replace')

    if parent_name:
        return f"{parent_name}.{name}" if name else parent_name
    return name or "unnamed_field"


def get_field_value(field: Dict[str, Any]) -> Optional[str]:
    """
    Get the current value of a form field.

    Args:
        field: Form field dictionary

    Returns:
        Field value or None
    """
    v = field.get("/V")
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, bytes):
        return v.decode('utf-8', errors='replace')
    if hasattr(v, 'name'):
        return v.name
    return str(v)


def get_field_options(field: Dict[str, Any]) -> List[str]:
    """
    Get options for choice fields (dropdown, list, radio).

    Args:
        field: Form field dictionary

    Returns:
        List of options
    """
    options = []
    opt = field.get("/Opt")
    if opt is None:
        return options

    try:
        for item in opt:
            if isinstance(item, str):
                options.append(item)
            elif isinstance(item, list) and len(item) >= 2:
                # Format: [export_value, display_value]
                display = item[1] if len(item) > 1 else item[0]
                if isinstance(display, bytes):
                    display = display.decode('utf-8', errors='replace')
                options.append(str(display))
            elif isinstance(item, bytes):
                options.append(item.decode('utf-8', errors='replace'))
    except Exception:
        pass

    return options


def is_field_readonly(field: Dict[str, Any]) -> bool:
    """
    Check if a field is read-only.

    Args:
        field: Form field dictionary

    Returns:
        True if read-only
    """
    flags = field.get("/Ff", 0)
    if isinstance(flags, int):
        return bool(flags & 0x01)  # Read-only flag
    return False


def is_field_required(field: Dict[str, Any]) -> bool:
    """
    Check if a field is required.

    Args:
        field: Form field dictionary

    Returns:
        True if required
    """
    flags = field.get("/Ff", 0)
    if isinstance(flags, int):
        return bool(flags & 0x02)  # Required flag
    return False


def extract_field_info(field: Dict[str, Any], parent_name: str = "") -> Dict[str, Any]:
    """
    Extract detailed information from a form field.

    Args:
        field: Form field dictionary
        parent_name: Parent field name

    Returns:
        Dictionary with field information
    """
    info = {
        "name": get_field_name(field, parent_name),
        "type": get_field_type(field),
        "value": get_field_value(field),
        "readonly": is_field_readonly(field),
        "required": is_field_required(field)
    }

    # Add options for choice fields
    if info["type"] in ("dropdown", "list", "radio"):
        info["options"] = get_field_options(field)

    # Add flags if present
    flags = field.get("/Ff")
    if flags is not None:
        info["flags"] = flags

    return info


def get_fields_recursive(fields: List, parent_name: str = "") -> List[Dict[str, Any]]:
    """
    Recursively extract all form fields.

    Args:
        fields: List of field dictionaries
        parent_name: Parent field name

    Returns:
        List of field information dictionaries
    """
    result = []

    for field in fields:
        field_dict = dict(field) if hasattr(field, '__iter__') else {}

        # Extract field info
        info = extract_field_info(field_dict, parent_name)
        result.append(info)

        # Check for child fields
        kids = field.get("/Kids")
        if kids:
            child_name = get_field_name(field_dict, parent_name)
            child_fields = get_fields_recursive(kids, child_name)
            result.extend(child_fields)

    return result


def check_fillable_fields(pdf_path: str) -> Dict[str, Any]:
    """
    Check if a PDF has fillable form fields.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with form field information
    """
    pdf_path = Path(pdf_path)
    result = {
        "file_info": {
            "filename": pdf_path.name,
            "path": str(pdf_path.absolute())
        },
        "has_form": False,
        "field_count": 0,
        "fields": []
    }

    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)

        # Check for AcroForm
        if "/AcroForm" in reader.trailer.get("/Root", {}):
            result["has_form"] = True

            # Get form fields
            form = reader.trailer["/Root"]["/AcroForm"]
            fields = form.get("/Fields", [])

            if fields:
                result["fields"] = get_fields_recursive(fields)
                result["field_count"] = len(result["fields"])

        # Alternative: check reader fields directly
        if not result["has_form"] and hasattr(reader, 'get_fields'):
            try:
                reader_fields = reader.get_fields()
                if reader_fields:
                    result["has_form"] = True
                    for name, field in reader_fields.items():
                        info = extract_field_info(field)
                        info["name"] = name
                        result["fields"].append(info)
                    result["field_count"] = len(result["fields"])
            except Exception:
                pass

    return result


def format_as_json(data: Dict[str, Any]) -> str:
    """Format results as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_text(data: Dict[str, Any]) -> str:
    """Format results as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("PDF FORM FIELDS CHECK")
    lines.append("=" * 60)

    # File info
    lines.append(f"\nFile: {data['file_info']['filename']}")
    lines.append(f"Path: {data['file_info']['path']}")

    # Form status
    lines.append(f"\nHas Fillable Form: {'Yes' if data['has_form'] else 'No'}")
    lines.append(f"Total Fields: {data['field_count']}")

    if data['fields']:
        lines.append("\n--- Form Fields ---")
        for i, field in enumerate(data['fields'], 1):
            lines.append(f"\n[{i}] {field['name']}")
            lines.append(f"    Type: {field['type']}")
            if field.get('value'):
                lines.append(f"    Current Value: {field['value']}")
            if field.get('options'):
                lines.append(f"    Options: {', '.join(field['options'][:10])}")
                if len(field['options']) > 10:
                    lines.append(f"             ... and {len(field['options']) - 10} more")
            flags = []
            if field.get('readonly'):
                flags.append("readonly")
            if field.get('required'):
                flags.append("required")
            if flags:
                lines.append(f"    Flags: {', '.join(flags)}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_as_markdown(data: Dict[str, Any]) -> str:
    """Format results as markdown."""
    lines = []
    lines.append(f"# PDF Form Fields: {data['file_info']['filename']}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Has Fillable Form:** {'Yes' if data['has_form'] else 'No'}")
    lines.append(f"- **Total Fields:** {data['field_count']}")
    lines.append("")

    if data['fields']:
        lines.append("## Fields")
        lines.append("")
        lines.append("| # | Name | Type | Value | Flags |")
        lines.append("|---|------|------|-------|-------|")

        for i, field in enumerate(data['fields'], 1):
            flags = []
            if field.get('readonly'):
                flags.append("readonly")
            if field.get('required'):
                flags.append("required")
            flags_str = ", ".join(flags) if flags else "-"
            value = field.get('value', '-') or '-'
            lines.append(f"| {i} | `{field['name']}` | {field['type']} | {value} | {flags_str} |")

        # Add options for choice fields
        choice_fields = [f for f in data['fields'] if f.get('options')]
        if choice_fields:
            lines.append("")
            lines.append("### Field Options")
            lines.append("")
            for field in choice_fields:
                lines.append(f"**{field['name']}:**")
                for opt in field['options'][:20]:
                    lines.append(f"  - {opt}")
                if len(field['options']) > 20:
                    lines.append(f"  - ... and {len(field['options']) - 20} more")
                lines.append("")

    return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Check if PDF has fillable form fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf
    %(prog)s document.pdf -o fields.json
    %(prog)s document.pdf --format text
    %(prog)s document.pdf --format markdown
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
        "--check-only",
        action="store_true",
        help="Only check if form exists (exit 0 if has form, 1 if not)"
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
        result = check_fillable_fields(str(pdf_path))

        # Quick check mode
        if args.check_only:
            if result["has_form"]:
                print("HAS_FORM")
                sys.exit(0)
            else:
                print("NO_FORM")
                sys.exit(1)

        # Format output
        formatters = {
            "json": format_as_json,
            "text": format_as_text,
            "markdown": format_as_markdown
        }

        formatter = formatters.get(args.format, format_as_json)
        output = formatter(result)

        # Write or print output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"Results saved to: {output_path}")
        else:
            print(output)

    except Exception as e:
        print(f"Error checking form fields: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
