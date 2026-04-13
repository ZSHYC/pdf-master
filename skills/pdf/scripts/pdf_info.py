#!/usr/bin/env python3
"""PDF Info Script - View detailed PDF information

Features:
- Display basic PDF info (pages, size, encryption status)
- Display metadata
- Display font information
- Display image information
- JSON output support

Dependencies: pypdf, Pillow (optional, for image info)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing pypdf library")
    print("Run: pip install pypdf")
    sys.exit(1)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def parse_pdf_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    try:
        if date_str.startswith("D:"):
            date_str = date_str[2:]
        from datetime import datetime
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


def get_basic_info(pdf_path: Path, reader) -> Dict[str, Any]:
    file_stat = pdf_path.stat()
    return {
        "filename": pdf_path.name,
        "path": str(pdf_path.absolute()),
        "size_bytes": file_stat.st_size,
        "size_human": format_file_size(file_stat.st_size),
        "page_count": len(reader.pages),
    }


def get_metadata(reader) -> Dict[str, Any]:
    if not reader.metadata:
        return {}
    metadata = reader.metadata
    result = {}
    fields = {"title": "/Title", "author": "/Author", "subject": "/Subject", "keywords": "/Keywords", "creator": "/Creator", "producer": "/Producer"}
    for key, pdf_key in fields.items():
        value = metadata.get(pdf_key)
        if value:
            result[key] = value
    creation_date = metadata.get("/CreationDate")
    if creation_date:
        result["creation_date"] = parse_pdf_date(creation_date)
    mod_date = metadata.get("/ModDate")
    if mod_date:
        result["modification_date"] = parse_pdf_date(mod_date)
    return result


def get_technical_info(reader) -> Dict[str, Any]:
    result = {"is_encrypted": reader.is_encrypted, "is_linear": getattr(reader, "is_linear", False), "xmp_metadata": reader.xmp_metadata is not None}
    try:
        if hasattr(reader, "pdf_header"):
            result["pdf_version"] = reader.pdf_header.strip()
    except Exception:
        pass
    if reader.pages:
        first_page = reader.pages[0]
        mediabox = first_page.mediabox
        result["page_size"] = {"width": float(mediabox.width), "height": float(mediabox.height)}
    return result

def get_font_info(reader, verbose: bool = False) -> List[Dict[str, Any]]:
    fonts = []
    seen_fonts = set()
    for page_num, page in enumerate(reader.pages):
        try:
            if "/Resources" in page and "/Font" in page["/Resources"]:
                font_dict = page["/Resources"]["/Font"]
                if hasattr(font_dict, "get_object"):
                    font_dict = font_dict.get_object()
                for font_name, font_obj in font_dict.items():
                    try:
                        if hasattr(font_obj, "get_object"):
                            font_obj = font_obj.get_object()
                        font_info = {"name": str(font_name), "page": page_num + 1}
                        if "/BaseFont" in font_obj:
                            font_info["base_font"] = str(font_obj["/BaseFont"])
                        if "/Subtype" in font_obj:
                            font_info["subtype"] = str(font_obj["/Subtype"])
                        font_key = (font_info.get("base_font", font_info["name"]), font_info.get("subtype", "Unknown"))
                        if font_key not in seen_fonts:
                            seen_fonts.add(font_key)
                            fonts.append(font_info)
                    except Exception as e:
                        if verbose:
                            print(f"  Warning: Failed to parse font - {e}")
        except Exception as e:
            if verbose:
                print(f"  Warning: Failed to parse fonts on page {page_num + 1} - {e}")
    return fonts


def get_image_info(reader, verbose: bool = False) -> List[Dict[str, Any]]:
    images = []
    if not HAS_PIL:
        return images
    for page_num, page in enumerate(reader.pages):
        try:
            if "/Resources" in page and "/XObject" in page["/Resources"]:
                xobject = page["/Resources"]["/XObject"]
                if hasattr(xobject, "get_object"):
                    xobject = xobject.get_object()
                for obj_name, obj in xobject.items():
                    try:
                        if hasattr(obj, "get_object"):
                            obj = obj.get_object()
                        if obj.get("/Subtype") == "/Image":
                            img_info = {"name": str(obj_name), "page": page_num + 1}
                            if "/Width" in obj and "/Height" in obj:
                                img_info["width"] = int(obj["/Width"])
                                img_info["height"] = int(obj["/Height"])
                            if "/ColorSpace" in obj:
                                img_info["colorspace"] = str(obj["/ColorSpace"])
                            if "/BitsPerComponent" in obj:
                                img_info["bits_per_component"] = int(obj["/BitsPerComponent"])
                            if "/Filter" in obj:
                                filter_val = obj["/Filter"]
                                if isinstance(filter_val, list):
                                    img_info["filter"] = [str(f) for f in filter_val]
                                else:
                                    img_info["filter"] = str(filter_val)
                            images.append(img_info)
                    except Exception as e:
                        if verbose:
                            print(f"  Warning: Failed to parse image - {e}")
        except Exception as e:
            if verbose:
                print(f"  Warning: Failed to parse images on page {page_num + 1} - {e}")
    return images

def get_pdf_info(pdf_path: str, include_fonts: bool = True, include_images: bool = True, verbose: bool = False) -> Dict[str, Any]:
    path = Path(pdf_path)
    with open(path, "rb") as f:
        reader = PdfReader(f)
        if verbose:
            print(f"Reading PDF: {pdf_path}")
        result = {
            "basic": get_basic_info(path, reader),
            "metadata": get_metadata(reader),
            "technical": get_technical_info(reader),
        }
        if include_fonts:
            if verbose:
                print("Analyzing fonts...")
            result["fonts"] = get_font_info(reader, verbose)
        if include_images:
            if verbose:
                print("Analyzing images...")
            result["images"] = get_image_info(reader, verbose)
    return result


def format_as_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_text(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("PDF INFO")
    lines.append("=" * 60)
    basic = data["basic"]
    lines.append("")
    lines.append("[Basic Info]")
    lines.append(f"  Filename: {basic['filename']}")
    lines.append(f"  Path: {basic['path']}")
    lines.append(f"  Size: {basic['size_human']} ({basic['size_bytes']} bytes)")
    lines.append(f"  Pages: {basic['page_count']}")
    if data["metadata"]:
        lines.append("")
        lines.append("[Metadata]")
        for key, value in data["metadata"].items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label}: {value}")
    tech = data["technical"]
    lines.append("")
    lines.append("[Technical Info]")
    lines.append(f"  Encrypted: {'Yes' if tech['is_encrypted'] else 'No'}")
    lines.append(f"  Linear: {'Yes' if tech.get('is_linear') else 'No'}")
    lines.append(f"  XMP Metadata: {'Yes' if tech.get('xmp_metadata') else 'No'}")
    if tech.get("pdf_version"):
        lines.append(f"  PDF Version: {tech['pdf_version']}")
    if tech.get("page_size"):
        lines.append(f"  Page Size: {tech['page_size']['width']} x {tech['page_size']['height']}")
    if "fonts" in data and data["fonts"]:
        lines.append("")
        lines.append(f"[Fonts] ({len(data['fonts'])} found)")
        for font in data["fonts"][:10]:
            name = font.get("base_font", font.get("name", "Unknown"))
            subtype = font.get("subtype", "Unknown")
            lines.append(f"  - {name} ({subtype})")
        if len(data["fonts"]) > 10:
            lines.append(f"  ... and {len(data['fonts']) - 10} more")
    if "images" in data and data["images"]:
        lines.append("")
        lines.append(f"[Images] ({len(data['images'])} found)")
        for img in data["images"][:10]:
            size = f"{img.get('width', '?')}x{img.get('height', '?')}"
            lines.append(f"  - Page {img['page']}: {img['name']} ({size})")
        if len(data["images"]) > 10:
            lines.append(f"  ... and {len(data['images']) - 10} more")
    lines.append("")
    lines.append("=" * 60)
    return chr(10).join(lines)

def main():
    parser = argparse.ArgumentParser(description="View detailed PDF information")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--no-fonts", action="store_true", help="Skip font analysis")
    parser.add_argument("--no-images", action="store_true", help="Skip image analysis")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    args = parser.parse_args()
    pdf_path = Path(args.input)
    if not pdf_path.exists():
        print(f"Error: File not found - {args.input}", file=sys.stderr)
        sys.exit(1)
    try:
        info = get_pdf_info(str(pdf_path), include_fonts=not args.no_fonts, include_images=not args.no_images, verbose=args.verbose)
        if args.json:
            output = format_as_json(info)
        else:
            output = format_as_text(info)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Info saved to: {args.output}")
        else:
            print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
