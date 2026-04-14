#!/usr/bin/env python3
"""Tests for PDF/A conversion script."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))

from pdfa_convert import (
    PDFAVersion,
    PDFAResult,
    convert_to_pdfa_pikepdf,
    detect_pdfa_version,
    find_ghostscript,
    find_icc_profile,
    validate_pdfa,
)


class TestPDFALevels:
    """Tests for PDF/A version handling."""

    def test_pdfa_version_enum(self):
        """Test PDFAVersion enum values."""
        assert PDFAVersion.A1B.value == "1b"
        assert PDFAVersion.A1A.value == "1a"
        assert PDFAVersion.A2B.value == "2b"
        assert PDFAVersion.A2A.value == "2a"
        assert PDFAVersion.A3B.value == "3b"
        assert PDFAVersion.A3A.value == "3a"


class TestPDFAResult:
    """Tests for PDFAResult dataclass."""

    def test_result_creation(self):
        """Test creating a PDFAResult."""
        result = PDFAResult(
            success=True,
            input_file="test.pdf",
            output_file="output.pdf",
            pdfa_version="1b"
        )
        assert result.success is True
        assert result.input_file == "test.pdf"
        assert result.output_file == "output.pdf"
        assert result.pdfa_version == "1b"
        assert result.errors == []
        assert result.warnings == []

    def test_result_with_errors(self):
        """Test result with errors."""
        result = PDFAResult(
            success=False,
            input_file="test.pdf",
            errors=["Error 1", "Error 2"]
        )
        assert result.success is False
        assert len(result.errors) == 2


class TestFindGhostscript:
    """Tests for Ghostscript detection."""

    def test_find_ghostscript(self):
        """Test Ghostscript detection."""
        gs_path = find_ghostscript()
        # Result depends on system installation
        assert gs_path is None or isinstance(gs_path, str)


class TestFindICCProfile:
    """Tests for ICC profile detection."""

    def test_find_icc_profile(self):
        """Test ICC profile detection."""
        profile = find_icc_profile()
        # Result depends on system
        assert profile is None or isinstance(profile, str)


class TestValidatePDFA:
    """Tests for PDF/A validation."""

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        result = validate_pdfa("nonexistent.pdf")
        assert result.success is False
        assert len(result.errors) > 0

    def test_validate_invalid_file(self, tmp_path):
        """Test validation of non-PDF file."""
        # Create a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("Not a PDF")

        result = validate_pdfa(str(text_file))
        assert result.success is False


class TestConvertToPDFA:
    """Tests for PDF/A conversion."""

    def test_convert_nonexistent_file(self):
        """Test conversion of non-existent file."""
        result = convert_to_pdfa_pikepdf(
            "nonexistent.pdf",
            "output.pdf"
        )
        assert result.success is False
        assert len(result.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
