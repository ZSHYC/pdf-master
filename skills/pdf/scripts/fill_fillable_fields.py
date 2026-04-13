#!/usr/bin/env python3
"""
PDF Form Fill Script

Fill PDF form fields from a JSON file.
Supports text fields, checkboxes, radio buttons, and dropdowns.

Usage:
    python fill_fillable_fields.py input.pdf -d data.json -o output.pdf
    python fill_fillable_fields.py input.pdf --data data.json --output output.pdf
    python fill_fillable_fields.py input.pdf --set "field_name=value"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pypdf import PdfReader, PdfWriter

# Dependency check
MISSING_DEPS = []

try:
    from pypdf import PdfReader, PdfWriter
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


def encode_pdf_string(value: str) -> Any:
    """
    Encode a string for PDF.

    Args:
        value: String value

    Returns:
        PDF string object
    """
    try:
        from pypdf.generic import create_string_object
        return create_string_object(value)
    except ImportError:
        return value


def set_text_field(field: Dict[str, Any], value: str) -> bool:
    """
    Set the value of a text field.

    Args:
        field: Form field dictionary
        value: Text value

    Returns:
        True if successful
    """
    try:
        field[NameObject("/V")] = encode_pdf_string(str(value))
        return True
    except Exception:
        return False


def set_checkbox_field(field: Dict[str, Any], value: Any) -> bool:
    """
    Set the value of a checkbox field.

    Args:
        field: Form field dictionary
        value: Boolean or string value (True/False, "Yes"/"No", "On"/"Off")

    Returns:
        True if successful
    """
    try:
        # Determine the appearance state
        if isinstance(value, bool):
            state = "/Yes" if value else "/Off"
        elif isinstance(value, str):
            if value.lower() in ("true", "yes", "on", "1", "checked"):
                state = "/Yes"
            elif value.lower() in ("false", "no", "off", "0", "unchecked"):
                state = "/Off"
            else:
                state = value if value.startswith("/") else f"/{value}"
        else:
            state = "/Yes" if value else "/Off"

        field[NameObject("/V")] = NameObject(state)
        field[NameObject("/AS")] = NameObject(state)
        return True
    except Exception:
        return False


def set_radio_field(field: Dict[str, Any], value: str) -> bool:
    """
    Set the value of a radio button field.

    Args:
        field: Form field dictionary
        value: Selected option value

    Returns:
        True if successful
    """
    try:
        state = value if value.startswith("/") else f"/{value}"
        field[NameObject("/V")] = NameObject(state)
        field[NameObject("/AS")] = NameObject(state)
        return True
    except Exception:
        return False


def set_choice_field(field: Dict[str, Any], value: str) -> bool:
    """
    Set the value of a choice field (dropdown/list).

    Args:
        field: Form field dictionary
        value: Selected option value

    Returns:
        True if successful
    """
    try:
        field[NameObject("/V")] = encode_pdf_string(str(value))
        return True
    except Exception:
        return False


def find_field_by_name(fields: List, name: str) -> Optional[Dict[str, Any]]:
    """
    Find a field by its name.

    Args:
        fields: List of field dictionaries
        name: Field name to find

    Returns:
        Field dictionary or None
    """
    for field in fields:
        field_name = field.get("/T", "")
        if isinstance(field_name, bytes):
            field_name = field_name.decode('utf-8', errors='replace')

        if field_name == name:
            return field

        # Check kids
        kids = field.get("/Kids")
        if kids:
            found = find_field_by_name(kids, name)
            if found:
                return found

    return None


def fill_field(field: Dict[str, Any], value: Any, field_type: str) -> bool:
    """
    Fill a form field with a value.

    Args:
        field: Form field dictionary
        value: Value to set
        field_type: Field type

    Returns:
        True if successful
    """
    if field_type == "text":
        return set_text_field(field, str(value) if value is not None else "")
    elif field_type == "checkbox":
        return set_checkbox_field(field, value)
    elif field_type == "radio":
        return set_radio_field(field, str(value))
    elif field_type in ("dropdown", "list"):
        return set_choice_field(field, str(value))
    elif field_type == "signature":
        # Signatures require special handling
        return False
    else:
        # Try text field as fallback
        return set_text_field(field, str(value) if value is not None else "")


def get_all_fields(fields: List, result: List = None) -> List[Dict[str, Any]]:
    """
    Get all fields recursively.

    Args:
        fields: List of field dictionaries
        result: Accumulated result list

    Returns:
        List of all fields
    """
    if result is None:
        result = []

    for field in fields:
        result.append(field)
        kids = field.get("/Kids")
        if kids:
            get_all_fields(kids, result)

    return result


def fill_pdf_form(
    input_path: str,
    field_values: Dict[str, Any],
    output_path: str,
    flatten: bool = False
) -> Dict[str, Any]:
    """
    Fill a PDF form with values.

    Args:
        input_path: Path to input PDF
        field_values: Dictionary of field names and values
        output_path: Path to output PDF
        flatten: Whether to flatten form fields after filling

    Returns:
        Dictionary with results
    """
    result = {
        "success": True,
        "fields_filled": 0,
        "fields_failed": [],
        "fields_not_found": [],
        "total_fields": 0
    }

    try:
        from pypdf.generic import NameObject
    except ImportError:
        result["success"] = False
        result["error"] = "Failed to import NameObject from pypdf"
        return result

    # Read input PDF
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Copy pages
    for page in reader.pages:
        writer.add_page(page)

    # Get form fields
    if "/AcroForm" not in reader.trailer.get("/Root", {}):
        result["success"] = False
        result["error"] = "PDF does not have a form"
        return result

    root = reader.trailer["/Root"]
    if "/AcroForm" not in root:
        result["success"] = False
        result["error"] = "PDF does not have an AcroForm"
        return result

    form = root["/AcroForm"]
    fields = form.get("/Fields", [])

    all_fields = get_all_fields(fields)
    result["total_fields"] = len(all_fields)

    # Track which fields were found
    found_fields = set()

    # Fill fields
    for field in all_fields:
        field_name = field.get("/T", "")
        if isinstance(field_name, bytes):
            field_name = field_name.decode('utf-8', errors='replace')

        if not field_name:
            continue

        if field_name in field_values:
            found_fields.add(field_name)
            value = field_values[field_name]
            field_type = get_field_type(field)

            if fill_field(field, value, field_type):
                result["fields_filled"] += 1
            else:
                result["fields_failed"].append({
                    "name": field_name,
                    "type": field_type,
                    "value": value
                })

    # Check for fields not found in PDF
    for field_name in field_values:
        if field_name not in found_fields:
            result["fields_not_found"].append(field_name)

    # Update the form in writer
    if hasattr(writer, 'root_object'):
        writer.root_object.update({
            NameObject("/AcroForm"): form
        })

    # Flatten if requested
    if flatten:
        try:
            for page in writer.pages:
                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot
                        # Mark as hidden by setting flags
                        if "/F" in annot_obj:
                            flags = annot_obj["/F"]
                            annot_obj[NameObject("/F")] = flags | 0x02  # Hidden flag
        except Exception as e:
            result["flatten_warning"] = str(e)

    # Write output
    with open(output_path, 'wb') as f:
        writer.write(f)

    return result


def parse_field_value(value_str: str) -> Any:
    """
    Parse a field value from string.

    Args:
        value_str: String representation of value

    Returns:
        Parsed value
    """
    # Boolean
    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    # Number
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # String
    return value_str


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Fill PDF form fields from JSON or command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s input.pdf -d data.json -o output.pdf
    %(prog)s form.pdf --data values.json --output filled.pdf
    %(prog)s form.pdf --set "name=John Doe" --set "email=john@example.com" -o filled.pdf
    %(prog)s form.pdf -d data.json -o output.pdf --flatten

JSON Data Format:
    {
        "field_name": "value",
        "checkbox_field": true,
        "radio_field": "option1"
    }
        """
    )

    parser.add_argument(
        "input",
        help="Input PDF file path"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output PDF file path"
    )

    parser.add_argument(
        "-d", "--data",
        help="JSON file containing field values"
    )

    parser.add_argument(
        "--set",
        action="append",
        metavar="FIELD=VALUE",
        help="Set a field value (can be used multiple times)"
    )

    parser.add_argument(
        "--flatten",
        action="store_true",
        help="Flatten form fields after filling (make non-editable)"
    )

    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue even if some fields fail to fill"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be filled without creating output file"
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: PDF file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: Not a PDF file: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Collect field values
    field_values = {}

    # Load from JSON file
    if args.data:
        data_path = Path(args.data)
        if not data_path.exists():
            print(f"Error: JSON file not found: {data_path}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                field_values.update(json.load(f))
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {data_path}: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse --set arguments
    if args.set:
        for set_arg in args.set:
            if '=' not in set_arg:
                print(f"Error: Invalid --set format: '{set_arg}'. Expected FIELD=VALUE", file=sys.stderr)
                sys.exit(1)

            field_name, value_str = set_arg.split('=', 1)
            field_values[field_name.strip()] = parse_pdf_value(value_str.strip())

    if not field_values:
        print("Error: No field values provided. Use --data or --set options.", file=sys.stderr)
        sys.exit(1)

    # Validate output path
    output_path = Path(args.output)
    if output_path.exists() and not args.dry_run:
        print(f"Warning: Output file already exists and will be overwritten: {output_path}")

    try:
        # Import NameObject here after dependency check
        from pypdf.generic import NameObject

        if args.dry_run:
            # Just show what would be done
            print("Dry run - would fill the following fields:")
            for name, value in field_values.items():
                print(f"  {name}: {value}")
            sys.exit(0)

        result = fill_pdf_form(
            str(input_path),
            field_values,
            str(output_path),
            flatten=args.flatten
        )

        # Print results
        print(f"Form filling {'completed' if result['success'] else 'failed'}")
        print(f"Fields filled: {result['fields_filled']}/{result['total_fields']}")

        if result['fields_failed']:
            print(f"\nFailed to fill {len(result['fields_failed'])} field(s):")
            for failed in result['fields_failed']:
                print(f"  - {failed['name']} (type: {failed['type']}, value: {failed['value']})")

        if result['fields_not_found']:
            print(f"\nFields not found in PDF ({len(result['fields_not_found'])}):")
            for name in result['fields_not_found']:
                print(f"  - {name}")

        if not result['success']:
            print(f"\nError: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

        if result['fields_failed'] and not args.ignore_errors:
            sys.exit(1)

        print(f"\nOutput saved to: {output_path}")

    except Exception as e:
        print(f"Error filling form: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def parse_pdf_value(value_str: str) -> Any:
    """
    Parse a value string for PDF forms.

    Args:
        value_str: String value

    Returns:
        Parsed value
    """
    # Boolean
    if value_str.lower() in ("true", "yes", "on"):
        return True
    if value_str.lower() in ("false", "no", "off"):
        return False

    # Number
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # String (keep as-is)
    return value_str


if __name__ == "__main__":
    main()
