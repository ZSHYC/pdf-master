#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing pypdf"); sys.exit(1)

def validate_pdf(pdf_path: str, verbose: bool = False) -> Dict[str, Any]:
    path = Path(pdf_path)
    result = {"file": str(path), "valid": True, "errors": [], "warnings": [], "info": {}}
    if not path.exists():
        result["valid"] = False
        result["errors"].append("File does not exist")
        return result
    try:
        with open(path, "rb") as f:
            reader = PdfReader(f)
            result["info"]["page_count"] = len(reader.pages)
            result["info"]["encrypted"] = reader.is_encrypted
            for i, page in enumerate(reader.pages):
                try: pass
                except Exception as e:
                    result["errors"].append(f"Page {i+1} error: {e}")
                    result["valid"] = False
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Parse error: {e}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Validate PDF files")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_pdf(args.input)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "VALID" if result["valid"] else "INVALID"
        print(f"Status: {status}")
        if result["errors"]:
            for e in result["errors"]: print(f"  Error: {e}")
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__": main()