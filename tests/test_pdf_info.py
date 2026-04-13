
"""
Tests for PDF Info and Validation Functionality
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestPDFExtractionError:
    """Tests for PDF extraction error classes."""

    @pytest.mark.unit
    def test_pdf_extraction_error_creation(self):
        from _utils import PDFExtractionError
        error = PDFExtractionError("Test error")
        assert str(error) == "Test error"

    @pytest.mark.unit
    def test_pdf_extraction_error_with_file(self):
        from _utils import PDFExtractionError
        error = PDFExtractionError("Test error", file_path="test.pdf")
        assert "test.pdf" in str(error)

    @pytest.mark.unit
    def test_pdf_not_found_error(self):
        from _utils import PDFNotFoundError
        error = PDFNotFoundError("File not found", file_path="missing.pdf")
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_invalid_pdf_error(self):
        from _utils import InvalidPDFError
        error = InvalidPDFError("Not a PDF")
        assert "Not a PDF" in str(error)

    @pytest.mark.unit
    def test_page_range_error(self):
        from _utils import PageRangeError
        error = PageRangeError("Invalid range")
        assert "Invalid range" in str(error)


class TestValidatePDFPath:
    """Tests for PDF path validation."""

    @pytest.mark.unit
    def test_validate_pdf_path_exists(self, sample_pdf_path):
        from _utils import validate_pdf_path
        result = validate_pdf_path(str(sample_pdf_path))
        assert result.exists()

    @pytest.mark.unit
    def test_validate_pdf_path_not_found(self):
        from _utils import validate_pdf_path, PDFNotFoundError
        with pytest.raises(PDFNotFoundError):
            validate_pdf_path("nonexistent.pdf")


class TestParsePageRange:
    """Tests for page range parsing."""

    @pytest.mark.unit
    def test_parse_page_range_single(self):
        from _utils import parse_page_range
        result = parse_page_range("5", 10)
        assert result == [5]

    @pytest.mark.unit
    def test_parse_page_range_range(self):
        from _utils import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_multiple(self):
        from _utils import parse_page_range
        result = parse_page_range("1,3,5", 10)
        assert result == [1, 3, 5]

    @pytest.mark.unit
    def test_parse_page_range_out_of_bounds(self):
        from _utils import parse_page_range
        result = parse_page_range("1-15", 10)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class TestFormatFunctions:
    """Tests for formatting functions."""

    @pytest.mark.unit
    def test_format_file_size_bytes(self):
        from _utils import format_file_size
        result = format_file_size(500)
        assert "B" in result

    @pytest.mark.unit
    def test_format_file_size_kb(self):
        from _utils import format_file_size
        result = format_file_size(1024)
        assert "KB" in result

    @pytest.mark.unit
    def test_format_duration_seconds(self):
        from _utils import format_duration
        result = format_duration(30.5)
        assert "s" in result


class TestDependencyCheck:
    """Tests for dependency checking."""

    @pytest.mark.unit
    def test_check_dependencies_all_available(self):
        from _utils import check_dependencies
        result = check_dependencies(["os", "sys"])
        assert result == []

    @pytest.mark.unit
    def test_require_dependencies_passes(self):
        from _utils import require_dependencies
        require_dependencies(["os", "sys"])
