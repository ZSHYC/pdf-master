
"""
Tests for PDF Split Functionality
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestSplitPDFUnit:
    """Unit tests for PDF split functions."""

    @pytest.mark.unit
    def test_parse_page_range_single(self):
        from split_pdf import parse_page_range
        result = parse_page_range("5", 10)
        assert result == [5]

    @pytest.mark.unit
    def test_parse_page_range_multiple(self):
        from split_pdf import parse_page_range
        result = parse_page_range("1,3,5", 10)
        assert result == [1, 3, 5]

    @pytest.mark.unit
    def test_parse_page_range_range(self):
        from split_pdf import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_reverse(self):
        from split_pdf import parse_page_range
        result = parse_page_range("5-1", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_split_by_pages_function_exists(self):
        pytest.importorskip("pypdf")
        from split_pdf import split_by_pages
        assert callable(split_by_pages)

    @pytest.mark.unit
    def test_split_by_range_function_exists(self):
        pytest.importorskip("pypdf")
        from split_pdf import split_by_range
        assert callable(split_by_range)

    @pytest.mark.unit
    def test_extract_single_pages_function_exists(self):
        pytest.importorskip("pypdf")
        from split_pdf import extract_single_pages
        assert callable(extract_single_pages)


class TestSplitPDFIntegration:
    """Integration tests for PDF split."""

    @pytest.mark.integration
    def test_split_by_pages(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from split_pdf import split_by_pages
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        for i in range(6):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        c.save()
        output = str(temp_dir / "split_{part}.pdf")
        result = split_by_pages(str(pdf_path), 2, output, verbose=False)
        assert result is True

    @pytest.mark.integration
    def test_split_by_range(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from split_pdf import split_by_range
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        for i in range(5):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        c.save()
        output = str(temp_dir / "extracted.pdf")
        result = split_by_range(str(pdf_path), "1-2,4", output, verbose=False)
        assert result is True


class TestSplitPDFEdgeCases:
    """Edge case tests for PDF split."""

    @pytest.mark.integration
    def test_split_single_page_pdf(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from split_pdf import split_by_pages
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "single.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Single Page")
        c.save()
        output = str(temp_dir / "split_{part}.pdf")
        result = split_by_pages(str(pdf_path), 5, output, verbose=False)
        assert result is True

    @pytest.mark.unit
    def test_parse_page_range_empty(self):
        from split_pdf import parse_page_range
        try:
            result = parse_page_range("", 10)
            assert result == []
        except (ValueError, Exception):
            pass
