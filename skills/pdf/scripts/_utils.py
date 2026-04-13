#!/usr/bin/env python3
"""
PDF Extraction Utilities
"""

import logging
import sys
import warnings
from pathlib import Path
from typing import List, Optional, Set


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors."""
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.file_path:
            return f"{self.message}: {self.file_path}"
        return self.message


class PDFNotFoundError(PDFExtractionError):
    """Raised when PDF file does not exist."""
    pass


class InvalidPDFError(PDFExtractionError):
    """Raised when file is not a valid PDF."""
    pass


class PageRangeError(PDFExtractionError):
    """Raised when page range specification is invalid."""
    pass


class DependencyError(PDFExtractionError):
    """Raised when required dependencies are missing."""
    pass


def setup_logging(verbose: bool = False, quiet: bool = False, name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    if quiet:
        logger.setLevel(logging.ERROR)
    elif verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    return logger


def validate_pdf_path(pdf_path: str) -> Path:
    path = Path(pdf_path)
    if not path.exists():
        raise PDFNotFoundError("PDF file not found", str(path))
    if not path.is_file():
        raise InvalidPDFError("Path is not a file", str(path))
    if path.suffix.lower() != ".pdf":
        raise InvalidPDFError("Not a PDF file (expected .pdf extension)", str(path))
    return path


def validate_output_path(output_path: str, create_dirs: bool = True) -> Path:
    path = Path(output_path)
    if create_dirs:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise PDFExtractionError(f"Cannot create output directory: {e}", str(path.parent))
    return path


def parse_page_range(page_spec: str, total_pages: int, allow_empty: bool = False) -> List[int]:
    if not page_spec or not page_spec.strip():
        if allow_empty:
            return []
        raise PageRangeError("Empty page specification")
    pages: Set[int] = set()
    for part in page_spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            if "-" in part:
                range_parts = part.split("-", 1)
                if len(range_parts) != 2:
                    raise PageRangeError(f"Invalid range format: {part}")
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start < 1:
                    raise PageRangeError(f"Page number must be >= 1, got {start}")
                if start > end:
                    raise PageRangeError(f"Invalid range: start ({start}) > end ({end})")
                pages.update(range(start, end + 1))
            else:
                page_num = int(part)
                if page_num < 1:
                    raise PageRangeError(f"Page number must be >= 1, got {page_num}")
                pages.add(page_num)
        except ValueError as e:
            raise PageRangeError(f"Invalid page number in specification: {part}") from e
    valid_pages = sorted(p for p in pages if 1 <= p <= total_pages)
    invalid_pages = sorted(p for p in pages if p < 1 or p > total_pages)
    if invalid_pages:
        warnings.warn(f"Page numbers out of range (1-{total_pages}): {invalid_pages}", UserWarning)
    if not valid_pages and not allow_empty:
        raise PageRangeError(f"No valid pages in range 1-{total_pages} from specification: {page_spec}")
    return valid_pages


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes}m {remaining:.1f}s"


def check_dependencies(required: List[str]) -> List[str]:
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return missing


def require_dependencies(required: List[str]) -> None:
    missing = check_dependencies(required)
    if missing:
        raise DependencyError(f"Missing required dependencies: {', '.join(missing)}. Install with: pip install {' '.join(missing)}")
