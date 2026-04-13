#!/usr/bin/env python3
"""Form Utilities - Form processing common module"""
from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pypdf import PdfReader

logger = logging.getLogger(__name__)

class FormOperationError(Exception):
    """Base exception for form operations"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

class FormNotFoundError(FormOperationError):
    """Raised when no form is found in PDF"""
    pass

class FieldNotFoundError(FormOperationError):
    """Raised when a field is not found"""
    def __init__(self, field_name: str, available: Optional[List[str]] = None) -> None:
        super().__init__(f"Field not found: {field_name}", {"field_name": field_name, "available": available or []})
        self.field_name = field_name

class InvalidFormDataError(FormOperationError):
    """Raised when form data is invalid"""
    def __init__(self, errors: List[str]) -> None:
        super().__init__(f"Validation failed: {len(errors)} error(s)", {"errors": errors})
        self.errors = errors

# Field type constants
FIELD_TYPE_TEXT = "text"
FIELD_TYPE_CHECKBOX = "checkbox"
FIELD_TYPE_RADIO = "radio"
FIELD_TYPE_BUTTON = "button"
FIELD_TYPE_DROPDOWN = "dropdown"
FIELD_TYPE_LIST = "list"
FIELD_TYPE_SIGNATURE = "signature"
FIELD_TYPE_UNKNOWN = "unknown"

# Field flags
FIELD_FLAG_READONLY = 0x01
FIELD_FLAG_REQUIRED = 0x02
FIELD_FLAG_NO_EXPORT = 0x04
FIELD_FLAG_MULTILINE = 0x1000
FIELD_FLAG_PASSWORD = 0x2000
FIELD_FLAG_RADIO = 0x8000
FIELD_FLAG_PUSH_BUTTON = 0x10000
FIELD_FLAG_COMBO = 0x20000
FIELD_FLAG_EDIT = 0x40000
FIELD_FLAG_MULTI_SELECT = 0x200000

def get_field_type(field: Dict[str, Any]) -> str:
    ft = field.get("/FT")
    if ft == "/Tx": return FIELD_TYPE_TEXT
    elif ft == "/Btn":
        flags = field.get("/Ff", 0)
        if isinstance(flags, int):
            if flags & FIELD_FLAG_PUSH_BUTTON: return FIELD_TYPE_BUTTON
            if flags & FIELD_FLAG_RADIO: return FIELD_TYPE_RADIO
        return FIELD_TYPE_CHECKBOX
    elif ft == "/Ch":
        flags = field.get("/Ff", 0)
        return FIELD_TYPE_DROPDOWN if isinstance(flags, int) and flags & FIELD_FLAG_COMBO else FIELD_TYPE_LIST
    elif ft == "/Sig": return FIELD_TYPE_SIGNATURE
    return FIELD_TYPE_UNKNOWN

def get_field_name(field: Dict[str, Any], parent: str = "") -> str:
    name = field.get("/T", "")
    if isinstance(name, bytes): name = name.decode("utf-8", errors="replace")
    if parent: return f"{parent}.{name}" if name else parent
    return name or "unnamed_field"

def decode_pdf_string(value: Any) -> Optional[str]:
    if value is None: return None
    if isinstance(value, str): return value
    if isinstance(value, bytes): return value.decode("utf-8", errors="replace")
    if hasattr(value, "name"): return value.name
    return str(value)

def get_field_value(field: Dict[str, Any]) -> Optional[str]:
    return decode_pdf_string(field.get("/V"))

def get_field_default_value(field: Dict[str, Any]) -> Optional[str]:
    return decode_pdf_string(field.get("/DV"))

def parse_field_flags(flags: int) -> Dict[str, bool]:
    return {
        "readonly": bool(flags & FIELD_FLAG_READONLY),
        "required": bool(flags & FIELD_FLAG_REQUIRED),
        "no_export": bool(flags & FIELD_FLAG_NO_EXPORT),
        "multiline": bool(flags & FIELD_FLAG_MULTILINE),
        "password": bool(flags & FIELD_FLAG_PASSWORD),
        "radio": bool(flags & FIELD_FLAG_RADIO),
        "push_button": bool(flags & FIELD_FLAG_PUSH_BUTTON),
        "combo": bool(flags & FIELD_FLAG_COMBO),
        "edit": bool(flags & FIELD_FLAG_EDIT),
        "multi_select": bool(flags & FIELD_FLAG_MULTI_SELECT),
    }

def is_field_readonly(field: Dict[str, Any]) -> bool:
    flags = field.get("/Ff", 0)
    return isinstance(flags, int) and bool(flags & FIELD_FLAG_READONLY)

def is_field_required(field: Dict[str, Any]) -> bool:
    flags = field.get("/Ff", 0)
    return isinstance(flags, int) and bool(flags & FIELD_FLAG_REQUIRED)

def get_field_options(field: Dict[str, Any]) -> List[Dict[str, str]]:
    options = []
    opt = field.get("/Opt")
    if not opt: return options
    try:
        for item in opt:
            if isinstance(item, str):
                options.append({"export": item, "display": item})
            elif isinstance(item, bytes):
                d = item.decode("utf-8", errors="replace")
                options.append({"export": d, "display": d})
            elif isinstance(item, list) and len(item) >= 2:
                e, d = decode_pdf_string(item[0]), decode_pdf_string(item[1])
                if e and d: options.append({"export": e, "display": d})
    except: pass
    return options

def get_field_rect(field: Dict[str, Any]) -> Optional[List[float]]:
    rect = field.get("/Rect")
    if not rect: return None
    try: return [float(c) for c in rect]
    except: return None

FORM_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "fields": {"type": "object"},
        "output": {"type": "string"},
        "flatten": {"type": "boolean", "default": False}
    },
    "required": ["fields"]
}

def validate_form_data_schema(data: Dict[str, Any]) -> List[str]:
    errors = []
    try:
        from jsonschema import validate, ValidationError
        validate(instance=data, schema=FORM_DATA_SCHEMA)
    except ImportError:
        if not isinstance(data, dict): errors.append("Data must be object")
        elif "fields" not in data: errors.append("Missing fields")
        elif not isinstance(data["fields"], dict): errors.append("fields must be object")
    except ValidationError as e:
        errors.append(str(e.message))
    return errors

def load_and_validate_json(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    errors = validate_form_data_schema(data)
    if errors:
        raise InvalidFormDataError(errors)
    return data

def check_pypdf_dependency() -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("Error: Missing pypdf. Install: pip install pypdf", file=sys.stderr)
        sys.exit(1)
