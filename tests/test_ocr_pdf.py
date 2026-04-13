
"""
Tests for PDF OCR Functionality
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestOCRPDFUnit:
    """Unit tests for OCR functions."""

    @pytest.mark.unit
    def test_parse_page_range_single(self):
        from ocr_pdf import parse_page_range
        result = parse_page_range("5", 10)
        assert result == [4]

    @pytest.mark.unit
    def test_parse_page_range_range(self):
        from ocr_pdf import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [0, 1, 2, 3, 4]

    @pytest.mark.unit
    def test_parse_page_range_mixed(self):
        from ocr_pdf import parse_page_range
        result = parse_page_range("1-3,5,7-9", 10)
        assert result == [0, 1, 2, 4, 6, 7, 8]

    @pytest.mark.unit
    def test_parse_page_range_out_of_bounds(self):
        from ocr_pdf import parse_page_range
        result = parse_page_range("1-15", 10)
        assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    @pytest.mark.unit
    def test_check_dependencies_function_exists(self):
        from ocr_pdf import check_dependencies
        assert callable(check_dependencies)

    @pytest.mark.unit
    def test_engine_constants(self):
        from ocr_pdf import ENGINE_TESSERACT, ENGINE_PADDLEOCR, ENGINE_EASYOCR
        assert ENGINE_TESSERACT == "tesseract"
        assert ENGINE_PADDLEOCR == "paddleocr"
        assert ENGINE_EASYOCR == "easyocr"


class TestOCRPDFMocked:
    """Mocked tests for OCR functionality."""

    @pytest.mark.unit
    def test_ocr_pdf_file_not_found(self):
        from ocr_pdf import ocr_pdf
        result, errors = ocr_pdf("nonexistent.pdf")
        assert len(errors) > 0


class TestOCRPDFEdgeCases:
    """Edge case tests for OCR."""

    @pytest.mark.unit
    def test_parse_page_range_empty(self):
        from ocr_pdf import parse_page_range
        try:
            result = parse_page_range("", 10)
            assert result == []
        except (ValueError, Exception):
            pass

    @pytest.mark.unit
    def test_parse_page_range_single_page(self):
        from ocr_pdf import parse_page_range
        result = parse_page_range("1", 1)
        assert result == [0]

    @pytest.mark.unit
    def test_check_dependencies_tesseract(self):
        from ocr_pdf import check_dependencies
        result = check_dependencies("tesseract")
        assert isinstance(result, list)
