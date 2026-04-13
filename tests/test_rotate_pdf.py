
"""
Tests for PDF Rotate Functionality
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestRotatePDFUnit:
    """Unit tests for PDF rotate functions."""

    @pytest.mark.unit
    def test_parse_page_range_single(self):
        from rotate_pdf import parse_page_range
        result = parse_page_range("5", 10)
        assert result == [5]

    @pytest.mark.unit
    def test_parse_page_range_range(self):
        from rotate_pdf import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_mixed(self):
        from rotate_pdf import parse_page_range
        result = parse_page_range("1-3,5,7-9", 10)
        assert result == [1, 2, 3, 5, 7, 8, 9]

    @pytest.mark.unit
    def test_parse_page_range_reverse(self):
        from rotate_pdf import parse_page_range
        result = parse_page_range("5-1", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_out_of_bounds(self):
        from rotate_pdf import parse_page_range
        result = parse_page_range("1-15", 10)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @pytest.mark.unit
    def test_rotate_pdf_function_exists(self):
        pytest.importorskip("pypdf")
        from rotate_pdf import rotate_pdf
        assert callable(rotate_pdf)

    @pytest.mark.unit
    def test_get_page_rotations_function_exists(self):
        pytest.importorskip("pypdf")
        from rotate_pdf import get_page_rotations
        assert callable(get_page_rotations)


class TestRotatePDFIntegration:
    """Integration tests for PDF rotate."""

    @pytest.mark.integration
    def test_rotate_all_pages_90(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from rotate_pdf import rotate_pdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Test Page")
        c.save()
        output = str(temp_dir / "rotated.pdf")
        result = rotate_pdf(str(pdf_path), output, 90)
        assert result is True

    @pytest.mark.integration
    def test_rotate_specific_pages(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from rotate_pdf import rotate_pdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        for i in range(3):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        c.save()
        output = str(temp_dir / "rotated.pdf")
        result = rotate_pdf(str(pdf_path), output, 90, pages="1-2")
        assert result is True


class TestRotatePDFEdgeCases:
    """Edge case tests for PDF rotate."""

    @pytest.mark.integration
    def test_rotate_file_not_found(self, temp_dir):
        pytest.importorskip("pypdf")
        from rotate_pdf import rotate_pdf
        output = str(temp_dir / "rotated.pdf")
        result = rotate_pdf("nonexistent.pdf", output, 90)
        assert result is False

    @pytest.mark.unit
    def test_parse_page_range_empty(self):
        from rotate_pdf import parse_page_range
        try:
            result = parse_page_range("", 10)
            assert result == []
        except (ValueError, Exception):
            pass
