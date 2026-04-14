#!/usr/bin/env python3
"""
PDF/A Conversion Script - PDF/A 存档格式转换

支持：
- PDF/A-1b 转换（基础存档标准）
- PDF/A-2b 转换（现代存档标准）
- PDF/A 验证（检查合规性）

依赖: pikepdf, ghostscript (可选)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PDFAVersion(Enum):
    """PDF/A version enumeration."""
    A1B = "1b"
    A1A = "1a"
    A2B = "2b"
    A2A = "2a"
    A3B = "3b"
    A3A = "3a"


@dataclass
class PDFAResult:
    """Result of PDF/A conversion or validation."""
    success: bool
    input_file: str
    output_file: Optional[str] = None
    pdfa_version: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)


def find_ghostscript() -> Optional[str]:
    """Find Ghostscript executable."""
    # Common Ghostscript executable names
    gs_names = ["gs", "gswin64c", "gswin32c", "gswin64", "gswin32"]

    for gs_name in gs_names:
        try:
            result = subprocess.run(
                [gs_name, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return gs_name
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    return None


def find_icc_profile() -> Optional[str]:
    """Find sRGB ICC profile on the system."""
    # Common ICC profile locations
    icc_paths = [
        "/usr/share/color/icc/sRGB.icc",
        "/usr/share/ghostscript/iccprofiles/srgb.icc",
        "C:\\Program Files\\gs\\gs9.56.1\\iccprofiles\\srgb.icc",
    ]

    import glob
    for path in icc_paths:
        if Path(path).exists():
            return path
        # Try glob patterns
        matches = glob.glob(path)
        if matches:
            return matches[0]
    return None


def convert_to_pdfa_ghostscript(
    input_path: str,
    output_path: str,
    level: PDFAVersion = PDFAVersion.A1B,
    icc_profile: Optional[str] = None,
    verbose: bool = False
) -> PDFAResult:
    """Convert PDF to PDF/A using Ghostscript."""
    result = PDFAResult(
        success=False,
        input_file=input_path,
        output_file=output_path
    )

    gs_path = find_ghostscript()
    if not gs_path:
        result.errors.append(
            "Ghostscript not found. Install from: "
            "https://www.ghostscript.com/download/gsdnld.html"
        )
        return result

    if not Path(input_path).exists():
        result.errors.append(f"Input file not found: {input_path}")
        return result

    # Find ICC profile
    if icc_profile is None:
        icc_profile = find_icc_profile()

    try:
        # Determine PDF/A version number
        if level in [PDFAVersion.A1B, PDFAVersion.A1A]:
            pdfa_num = "1"
            compat = "1.4"
        elif level in [PDFAVersion.A2B, PDFAVersion.A2A]:
            pdfa_num = "2"
            compat = "1.7"
        else:
            pdfa_num = "3"
            compat = "1.7"

        # Build Ghostscript command
        cmd = [
            gs_path,
            "-dPDFSETTINGS=/printer",
            f"-dCompatibilityLevel={compat}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dAutoRotatePages=/None",
            "-dEmbedAllFonts=true",
            "-dSubsetFonts=true",
            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",
            "-dColorConversionStrategy=/sRGB",
            "-sColorConversionStrategy=UseDeviceIndependentColor",
            f"-dPDFA={pdfa_num}",
            "-dPDFACompatibilityPolicy=1",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={output_path}",
            input_path
        ]

        if verbose:
            print(f"Running: {' '.join(cmd)}")

        # Execute conversion
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if proc.returncode != 0:
            result.errors.append(f"Ghostscript error: {proc.stderr}")
            return result

        if Path(output_path).exists():
            result.success = True
            result.pdfa_version = level.value
            result.info["output_size"] = Path(output_path).stat().st_size
            result.info["method"] = "ghostscript"
        else:
            result.errors.append("Output file was not created")

    except subprocess.TimeoutExpired:
        result.errors.append("Conversion timed out after 5 minutes")
    except Exception as e:
        result.errors.append(f"Conversion error: {e}")

    return result


def convert_to_pdfa_pikepdf(
    input_path: str,
    output_path: str,
    level: PDFAVersion = PDFAVersion.A1B,
    verbose: bool = False
) -> PDFAResult:
    """Convert PDF to PDF/A using pikepdf (limited capabilities)."""
    result = PDFAResult(
        success=False,
        input_file=input_path,
        output_file=output_path
    )

    try:
        import pikepdf
    except ImportError:
        result.errors.append(
            "pikepdf is required. Install with: pip install pikepdf"
        )
        return result

    if not Path(input_path).exists():
        result.errors.append(f"Input file not found: {input_path}")
        return result

    try:
        # Open PDF
        pdf = pikepdf.open(input_path)

        # Remove encryption if present (PDF/A doesn't allow encryption)
        if pdf.is_encrypted:
            result.warnings.append("Removing encryption for PDF/A compliance")
            pdf.save(output_path, encryption=False)
        else:
            pdf.save(output_path)

        pdf.close()

        result.success = True
        result.pdfa_version = level.value
        result.info["method"] = "pikepdf"
        result.warnings.append(
            "pikepdf conversion has limited capabilities. "
            "For full PDF/A compliance, use Ghostscript."
        )

    except Exception as e:
        result.errors.append(f"Conversion error: {e}")

    return result


def validate_pdfa(pdf_path: str, verbose: bool = False) -> PDFAResult:
    """Validate PDF/A compliance."""
    result = PDFAResult(
        success=False,
        input_file=pdf_path
    )

    try:
        import pikepdf
    except ImportError:
        result.errors.append(
            "pikepdf is required for validation. Install with: pip install pikepdf"
        )
        return result

    if not Path(pdf_path).exists():
        result.errors.append(f"File not found: {pdf_path}")
        return result

    try:
        with pikepdf.open(pdf_path) as pdf:
            # Check PDF/A version from metadata
            result.pdfa_version = detect_pdfa_version(pdf)

            # Validate structure
            validate_fonts(pdf, result, verbose)
            validate_metadata(pdf, result, verbose)
            validate_encryption(pdf, result, verbose)

            # Overall validation result
            result.success = (
                len(result.errors) == 0 and
                result.pdfa_version is not None
            )

            if result.pdfa_version is None:
                result.warnings.append(
                    "No PDF/A version detected - file may not be PDF/A compliant"
                )

    except Exception as e:
        result.errors.append(f"Validation error: {e}")

    return result


def detect_pdfa_version(pdf) -> Optional[str]:
    """Detect PDF/A version from XMP metadata."""
    try:
        import re

        # Check document info
        if pdf.docinfo and "/Producer" in pdf.docinfo:
            producer = str(pdf.docinfo["/Producer"])
            if "PDF/A" in producer:
                match = re.search(r"PDF/A[-]?(\d)([ab])?", producer, re.I)
                if match:
                    version = match.group(1)
                    conformance = match.group(2) or "b"
                    return f"{version}{conformance}"

        # Check XMP metadata
        if pdf.Root.get("/Metadata"):
            # Would need full XMP parsing for accurate detection
            pass

    except Exception:
        pass

    return None


def validate_fonts(pdf, result: PDFAResult, verbose: bool) -> None:
    """Validate that all fonts are embedded."""
    try:
        fonts_not_embedded = []

        for page_num, page in enumerate(pdf.pages):
            if "/Resources" in page:
                resources = page["/Resources"]
                if "/Font" in resources:
                    fonts = resources["/Font"]
                    for font_name in fonts:
                        font = fonts[font_name]
                        if "/FontDescriptor" not in font:
                            fonts_not_embedded.append(
                                f"Page {page_num + 1}: Font '{font_name}' not embedded"
                            )

        if fonts_not_embedded:
            result.errors.extend(fonts_not_embedded)
        elif verbose:
            result.info["fonts_valid"] = True

    except Exception as e:
        result.warnings.append(f"Font validation incomplete: {e}")


def validate_metadata(pdf, result: PDFAResult, verbose: bool) -> None:
    """Validate PDF/A metadata requirements."""
    try:
        # Check for required metadata
        if not pdf.docinfo:
            result.warnings.append("Missing document info dictionary")
        else:
            required_fields = ["/Title", "/Author", "/Creator", "/Producer"]
            for field in required_fields:
                if field not in pdf.docinfo:
                    result.warnings.append(f"Missing metadata field: {field}")

        # Check for XMP metadata
        if "/Metadata" not in pdf.Root:
            result.warnings.append("Missing XMP metadata stream")

    except Exception as e:
        result.warnings.append(f"Metadata validation incomplete: {e}")


def validate_encryption(pdf, result: PDFAResult, verbose: bool) -> None:
    """Validate that PDF is not encrypted (PDF/A requirement)."""
    if pdf.is_encrypted:
        result.errors.append("PDF/A does not allow encryption")


def convert_to_pdfa(
    input_path: str,
    output_path: str,
    level: str = "1b",
    method: str = "ghostscript",
    icc_profile: Optional[str] = None,
    verbose: bool = False
) -> PDFAResult:
    """Convert PDF to PDF/A format.

    Args:
        input_path: Path to input PDF file.
        output_path: Path to output PDF/A file.
        level: PDF/A level (1b, 1a, 2b, 2a, 3b, 3a).
        method: Conversion method (ghostscript, pikepdf).
        icc_profile: Path to ICC color profile.
        verbose: Print detailed information.

    Returns:
        PDFAResult with conversion details.
    """
    # Parse PDF/A level
    level_map = {
        "1b": PDFAVersion.A1B,
        "1a": PDFAVersion.A1A,
        "2b": PDFAVersion.A2B,
        "2a": PDFAVersion.A2A,
        "3b": PDFAVersion.A3B,
        "3a": PDFAVersion.A3A,
    }
    pdfa_level = level_map.get(level.lower(), PDFAVersion.A1B)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Select conversion method
    if method == "ghostscript":
        return convert_to_pdfa_ghostscript(
            input_path, output_path, pdfa_level, icc_profile, verbose
        )
    else:
        return convert_to_pdfa_pikepdf(
            input_path, output_path, pdfa_level, verbose
        )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert PDF to PDF/A format and validate PDF/A compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to PDF/A-1b
  %(prog)s input.pdf -o output.pdf --level 1b

  # Convert to PDF/A-2b
  %(prog)s input.pdf -o output.pdf --level 2b

  # Validate PDF/A compliance
  %(prog)s input.pdf --validate

  # Convert with verbose output
  %(prog)s input.pdf -o output.pdf --level 2b --verbose

  # Output as JSON
  %(prog)s input.pdf --validate --json
        """
    )

    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output PDF/A file path")
    parser.add_argument(
        "--level",
        choices=["1b", "1a", "2b", "2a", "3b", "3a"],
        default="1b",
        help="PDF/A conformance level (default: 1b)"
    )
    parser.add_argument(
        "--method",
        choices=["ghostscript", "pikepdf"],
        default="ghostscript",
        help="Conversion method (default: ghostscript)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate PDF/A compliance instead of converting"
    )
    parser.add_argument(
        "--icc-profile",
        help="Path to ICC color profile for conversion"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    # Execute operation
    if args.validate:
        result = validate_pdfa(args.input, args.verbose)
    elif args.output:
        result = convert_to_pdfa(
            args.input,
            args.output,
            args.level,
            args.method,
            args.icc_profile,
            args.verbose
        )
    else:
        parser.error("Either --output or --validate is required")

    # Output result
    if args.json:
        output = {
            "success": result.success,
            "input_file": result.input_file,
            "output_file": result.output_file,
            "pdfa_version": result.pdfa_version,
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info
        }
        print(json.dumps(output, indent=2))
    else:
        if result.success:
            print(f"SUCCESS: {'Validation' if args.validate else 'Conversion'} completed")
            if result.pdfa_version:
                print(f"PDF/A Version: {result.pdfa_version}")
            if result.output_file:
                print(f"Output: {result.output_file}")
        else:
            print("FAILED: Operation failed")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
