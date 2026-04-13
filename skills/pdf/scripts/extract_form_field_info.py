#!/usr/bin/env python3
"""
PDF Form Field Information Extraction Script

Extract detailed information about form fields from PDF files.
Outputs field name, type, position, options, etc. in JSON format.

Usage:
    python extract_form_field_info.py input.pdf
    python extract_form_field_info.py input.pdf -o fields.json
    python extract_form_field_info.py input.pdf --format text
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, TYPE_CHECKING

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
        flags = field.get("/Ff", 0)
        if isinstance(flags, int):
            if flags & 0x10000:
                return "button"
            elif flags & 0x8000:
                return "radio"
            else:
                return "checkbox"
        return "button"
    elif ft == "/Ch":
        flags = field.get("/Ff", 0)
        if isinstance(flags, int) and flags & 0x20000:
            return "dropdown"
        else:
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


def decode_pdf_string(value: Any) -> Optional[str]:
    """
    Decode a PDF string value.

    Args:
        value: PDF value

    Returns:
        Decoded string or None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if hasattr(value, 'name'):
        return value.name
    return str(value)


def get_field_value(field: Dict[str, Any]) -> Optional[str]:
    """
    Get the current value of a form field.

    Args:
        field: Form field dictionary

    Returns:
        Field value or None
    """
    return decode_pdf_string(field.get("/V"))


def get_field_default_value(field: Dict[str, Any]) -> Optional[str]:
    """
    Get the default value of a form field.

    Args:
        field: Form field dictionary

    Returns:
        Default value or None
    """
    return decode_pdf_string(field.get("/DV"))


def get_field_options(field: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Get options for choice fields (dropdown, list, radio).

    Args:
        field: Form field dictionary

    Returns:
        List of option dictionaries with export and display values
    """
    options = []
    opt = field.get("/Opt")
    if opt is None:
        return options

    try:
        for item in opt:
            if isinstance(item, str):
                options.append({"export": item, "display": item})
            elif isinstance(item, bytes):
                decoded = item.decode('utf-8', errors='replace')
                options.append({"export": decoded, "display": decoded})
            elif isinstance(item, list) and len(item) >= 2:
                export_val = decode_pdf_string(item[0])
                display_val = decode_pdf_string(item[1]) if len(item) > 1 else export_val
                options.append({"export": export_val, "display": display_val})
            elif isinstance(item, list) and len(item) == 1:
                val = decode_pdf_string(item[0])
                options.append({"export": val, "display": val})
    except Exception:
        pass

    return options


def parse_field_flags(flags: int) -> Dict[str, bool]:
    """
    Parse field flags into human-readable properties.

    Args:
        flags: Field flags integer

    Returns:
        Dictionary of flag properties
    """
    return {
        "readonly": bool(flags & 0x01),
        "required": bool(flags & 0x02),
        "no_export": bool(flags & 0x04),
        # Text field specific
        "multiline": bool(flags & 0x1000),
        "password": bool(flags & 0x2000),
        # Button specific
        "no_toggle_off": bool(flags & 0x4000),
        "radio": bool(flags & 0x8000),
        "push_button": bool(flags & 0x10000),
        # Choice specific
        "combo": bool(flags & 0x20000),
        "edit": bool(flags & 0x40000),
        "sort": bool(flags & 0x80000),
        "multi_select": bool(flags & 0x200000)
    }


def get_field_rect(field: Dict[str, Any]) -> Optional[List[float]]:
    """
    Get the rectangle (position) of a form field.

    Args:
        field: Form field dictionary

    Returns:
        List [x1, y1, x2, y2] or None
    """
    rect = field.get("/Rect")
    if rect is None:
        return None

    try:
        return [float(coord) for coord in rect]
    except Exception:
        return None


def get_field_page(field: Dict[str, Any], reader: "PdfReader") -> Optional[int]:
    """
    Get the page number of a form field.

    Args:
        field: Form field dictionary
        reader: PdfReader instance

    Returns:
        Page number (0-indexed) or None
    """
    # Try to find the field's page by checking annotations
    rect = get_field_rect(field)
    if rect is None:
        return None

    try:
        for page_num, page in enumerate(reader.pages):
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot
                    if annot_obj.get("/T") == field.get("/T"):
                        return page_num
                    # Also check by rectangle
                    annot_rect = annot_obj.get("/Rect")
                    if annot_rect and rect == [float(c) for c in annot_rect]:
                        return page_num
    except Exception:
        pass

    return None


def get_field_actions(field: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Get actions associated with a form field.

    Args:
        field: Form field dictionary

    Returns:
        Dictionary of action types and their values
    """
    actions = {}
    aa = field.get("/AA")
    if aa is None:
        return actions

    action_map = {
        "/K": "keystroke",
        "/V": "validate",
        "/F": "format",
        "/C": "calculate",
        "/E": "enter",
        "/X": "exit",
        "/D": "down",
        "/U": "up",
        "/Fo": "focus",
        "/Bl": "blur"
    }

    try:
        for action_key, action_name in action_map.items():
            if action_key in aa:
                action_obj = aa[action_key]
                if hasattr(action_obj, 'get'):
                    action_type = action_obj.get("/S")
                    if action_type:
                        actions[action_name] = [action_type]
    except Exception:
        pass

    return actions


def extract_field_info(field: Dict[str, Any], reader: "PdfReader", parent_name: str = "") -> Dict[str, Any]:
    """
    Extract detailed information from a form field.

    Args:
        field: Form field dictionary
        reader: PdfReader instance
        parent_name: Parent field name

    Returns:
        Dictionary with field information
    """
    field_type = get_field_type(field)

    info = {
        "name": get_field_name(field, parent_name),
        "type": field_type,
        "value": get_field_value(field),
        "default_value": get_field_default_value(field)
    }

    # Position
    rect = get_field_rect(field)
    if rect:
        info["position"] = {
            "x1": rect[0],
            "y1": rect[1],
            "x2": rect[2],
            "y2": rect[3],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1]
        }

    # Page
    page = get_field_page(field, reader)
    if page is not None:
        info["page"] = page

    # Flags
    flags = field.get("/Ff", 0)
    if isinstance(flags, int):
        info["flags"] = parse_field_flags(flags)

    # Options for choice fields
    if field_type in ("dropdown", "list", "radio"):
        options = get_field_options(field)
        if options:
            info["options"] = options

    # Maximum length for text fields
    max_len = field.get("/MaxLen")
    if max_len is not None:
        info["max_length"] = int(max_len)

    # Actions
    actions = get_field_actions(field)
    if actions:
        info["actions"] = actions

    # Additional properties
    if "/TU" in field:
        info["alternate_name"] = decode_pdf_string(field["/TU"])
    if "/TM" in field:
        info["mapping_name"] = decode_pdf_string(field["/TM"])

    return info


def get_fields_recursive(fields: List, reader: "PdfReader", parent_name: str = "") -> List[Dict[str, Any]]:
    """
    Recursively extract all form fields.

    Args:
        fields: List of field dictionaries
        reader: PdfReader instance
        parent_name: Parent field name

    Returns:
        List of field information dictionaries
    """
    result = []

    for field in fields:
        field_dict = dict(field) if hasattr(field, '__iter__') else {}

        # Extract field info
        info = extract_field_info(field_dict, reader, parent_name)
        result.append(info)

        # Check for child fields
        kids = field.get("/Kids")
        if kids:
            child_name = get_field_name(field_dict, parent_name)
            child_fields = get_fields_recursive(kids, reader, child_name)
            result.extend(child_fields)

    return result


def extract_form_field_info(pdf_path: str) -> Dict[str, Any]:
    """
    Extract detailed form field information from a PDF file.

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
        "fields": [],
        "field_types": {},
        "summary": {}
    }

    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)

        # Check for AcroForm
        if "/AcroForm" in reader.trailer.get("/Root", {}):
            result["has_form"] = True

            form = reader.trailer["/Root"]["/AcroForm"]
            fields = form.get("/Fields", [])

            if fields:
                result["fields"] = get_fields_recursive(fields, reader)
                result["field_count"] = len(result["fields"])

        # Alternative method
        if not result["has_form"] and hasattr(reader, 'get_fields'):
            try:
                reader_fields = reader.get_fields()
                if reader_fields:
                    result["has_form"] = True
                    for name, field in reader_fields.items():
                        info = extract_field_info(field, reader)
                        info["name"] = name
                        result["fields"].append(info)
                    result["field_count"] = len(result["fields"])
            except Exception:
                pass

        # Calculate field type summary
        if result["fields"]:
            type_counts = {}
            readonly_count = 0
            required_count = 0

            for field in result["fields"]:
                field_type = field.get("type", "unknown")
                type_counts[field_type] = type_counts.get(field_type, 0) + 1

                if field.get("flags", {}).get("readonly"):
                    readonly_count += 1
                if field.get("flags", {}).get("required"):
                    required_count += 1

            result["field_types"] = type_counts
            result["summary"] = {
                "total_fields": result["field_count"],
                "readonly_fields": readonly_count,
                "required_fields": required_count
            }

    return result


def format_as_json(data: Dict[str, Any]) -> str:
    """Format results as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_text(data: Dict[str, Any]) -> str:
    """Format results as plain text."""
    lines = []
    lines.append("=" * 70)
    lines.append("PDF FORM FIELD INFORMATION")
    lines.append("=" * 70)

    # File info
    lines.append(f"\nFile: {data['file_info']['filename']}")
    lines.append(f"Path: {data['file_info']['path']}")

    # Summary
    lines.append(f"\nHas Form: {'Yes' if data['has_form'] else 'No'}")
    if data['field_count'] > 0:
        lines.append(f"Total Fields: {data['field_count']}")
        if data.get('summary'):
            lines.append(f"Readonly Fields: {data['summary'].get('readonly_fields', 0)}")
            lines.append(f"Required Fields: {data['summary'].get('required_fields', 0)}")

        if data.get('field_types'):
            lines.append("\nField Types:")
            for ftype, count in data['field_types'].items():
                lines.append(f"  - {ftype}: {count}")

    if data['fields']:
        lines.append("\n" + "-" * 70)
        lines.append("FIELD DETAILS")
        lines.append("-" * 70)

        for i, field in enumerate(data['fields'], 1):
            lines.append(f"\n[{i}] {field['name']}")
            lines.append(f"    Type: {field['type']}")

            if field.get('value') is not None:
                lines.append(f"    Value: {field['value']}")
            if field.get('default_value') is not None:
                lines.append(f"    Default: {field['default_value']}")

            if field.get('position'):
                pos = field['position']
                lines.append(f"    Position: ({pos['x1']:.1f}, {pos['y1']:.1f}) to ({pos['x2']:.1f}, {pos['y2']:.1f})")
                lines.append(f"    Size: {pos['width']:.1f} x {pos['height']:.1f}")

            if field.get('page') is not None:
                lines.append(f"    Page: {field['page'] + 1}")

            if field.get('max_length'):
                lines.append(f"    Max Length: {field['max_length']}")

            if field.get('options'):
                lines.append(f"    Options ({len(field['options'])}):")
                for opt in field['options'][:10]:
                    if opt['export'] == opt['display']:
                        lines.append(f"      - {opt['export']}")
                    else:
                        lines.append(f"      - {opt['display']} (export: {opt['export']})")
                if len(field['options']) > 10:
                    lines.append(f"      ... and {len(field['options']) - 10} more")

            flags = field.get('flags', {})
            flag_strs = [k for k, v in flags.items() if v and k not in ('readonly', 'required')]
            if flags.get('readonly'):
                flag_strs.insert(0, 'readonly')
            if flags.get('required'):
                flag_strs.insert(0, 'required')
            if flag_strs:
                lines.append(f"    Flags: {', '.join(flag_strs)}")

            if field.get('alternate_name'):
                lines.append(f"    Alternate Name: {field['alternate_name']}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def format_as_markdown(data: Dict[str, Any]) -> str:
    """Format results as markdown."""
    lines = []
    lines.append(f"# PDF Form Field Information: {data['file_info']['filename']}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| Has Form | {'Yes' if data['has_form'] else 'No'} |")
    lines.append(f"| Total Fields | {data['field_count']} |")

    if data.get('summary'):
        lines.append(f"| Readonly Fields | {data['summary'].get('readonly_fields', 0)} |")
        lines.append(f"| Required Fields | {data['summary'].get('required_fields', 0)} |")
    lines.append("")

    # Field types
    if data.get('field_types'):
        lines.append("### Field Types")
        lines.append("")
        lines.append("| Type | Count |")
        lines.append("|------|-------|")
        for ftype, count in data['field_types'].items():
            lines.append(f"| {ftype} | {count} |")
        lines.append("")

    # Fields
    if data['fields']:
        lines.append("## Fields")
        lines.append("")

        for i, field in enumerate(data['fields'], 1):
            lines.append(f"### {i}. `{field['name']}`")
            lines.append("")
            lines.append(f"- **Type:** {field['type']}")

            if field.get('value') is not None:
                lines.append(f"- **Value:** `{field['value']}`")
            if field.get('default_value') is not None:
                lines.append(f"- **Default:** `{field['default_value']}`")
            if field.get('page') is not None:
                lines.append(f"- **Page:** {field['page'] + 1}")
            if field.get('max_length'):
                lines.append(f"- **Max Length:** {field['max_length']}")

            if field.get('position'):
                pos = field['position']
                lines.append(f"- **Position:** ({pos['x1']:.1f}, {pos['y1']:.1f}) to ({pos['x2']:.1f}, {pos['y2']:.1f})")

            flags = field.get('flags', {})
            active_flags = [k for k, v in flags.items() if v]
            if active_flags:
                lines.append(f"- **Flags:** {', '.join(active_flags)}")

            if field.get('options'):
                lines.append("")
                lines.append("**Options:**")
                lines.append("")
                for opt in field['options'][:20]:
                    if opt['export'] == opt['display']:
                        lines.append(f"- {opt['export']}")
                    else:
                        lines.append(f"- {opt['display']} (`{opt['export']}`)")
                if len(field['options']) > 20:
                    lines.append(f"- ... and {len(field['options']) - 20} more")

            lines.append("")

    return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract detailed form field information from PDF files",
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
        "--include-actions",
        action="store_true",
        help="Include field actions in output"
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
        result = extract_form_field_info(str(pdf_path))

        # Filter actions if not requested
        if not args.include_actions:
            for field in result.get("fields", []):
                field.pop("actions", None)

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
            print(f"Form field information saved to: {output_path}")
        else:
            print(output)

    except Exception as e:
        print(f"Error extracting form field information: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
