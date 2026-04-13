
"""
Tests for PDF Watermark Functionality
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestWatermarkPDFUnit:
    """Unit tests for PDF watermark functions."""

    @pytest.mark.unit
    def test_add_watermark_function_exists(self):
        pytest.importorskip("pypdf")
        from watermark_pdf import add_watermark
        assert callable(add_watermark)

    @pytest.mark.unit
    def test_has_pil_flag(self):
        from watermark_pdf import HAS_PIL
        assert isinstance(HAS_PIL, bool)


class TestWatermarkPDFEdgeCases:
    """Edge case tests for PDF watermark."""

    @pytest.mark.integration
    def test_add_watermark_file_not_found(self, temp_dir):
        pytest.importorskip("pypdf")
        from watermark_pdf import add_watermark
        output = str(temp_dir / "watermarked.pdf")
        result = add_watermark("nonexistent.pdf", output, watermark_text="TEST")
        assert result is False

    @pytest.mark.integration
    def test_add_watermark_no_watermark_specified(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from watermark_pdf import add_watermark
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Test Page")
        c.save()
        
        output = str(temp_dir / "watermarked.pdf")
        result = add_watermark(str(pdf_path), output)
        assert result is False


class TestWatermarkPDFUnitFunctions:
    """Unit tests for watermark helper functions."""

    @pytest.mark.unit
    def test_watermark_module_imports(self):
        pytest.importorskip("pypdf")
        import watermark_pdf
        assert hasattr(watermark_pdf, "add_watermark")
