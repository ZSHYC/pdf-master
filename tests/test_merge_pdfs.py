
"""
Tests for PDF Merge Functionality
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestMergePDFsUnit:
    """Unit tests for PDF merge functions."""

    @pytest.mark.unit
    def test_merge_pdfs_function_exists(self):
        pytest.importorskip("pypdf")
        from merge_pdfs import merge_pdfs
        assert callable(merge_pdfs)

    @pytest.mark.unit
    def test_merge_pdfs_missing_file(self, temp_dir):
        pytest.importorskip("pypdf")
        from merge_pdfs import merge_pdfs
        output_file = temp_dir / "merged.pdf"
        result = merge_pdfs(["nonexistent1.pdf", "nonexistent2.pdf"], str(output_file))
        assert result is False


class TestMergePDFsIntegration:
    """Integration tests for PDF merge."""

    @pytest.mark.integration
    def test_merge_two_pdfs(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf1 = temp_dir / "file1.pdf"
        pdf2 = temp_dir / "file2.pdf"
        
        c1 = canvas.Canvas(str(pdf1), pagesize=letter)
        c1.drawString(100, 750, "File 1 - Page 1")
        c1.save()
        
        c2 = canvas.Canvas(str(pdf2), pagesize=letter)
        c2.drawString(100, 750, "File 2 - Page 1")
        c2.save()
        
        output = temp_dir / "merged.pdf"
        result = merge_pdfs([str(pdf1), str(pdf2)], str(output))
        
        assert result is True
        assert output.exists()
        
        from pypdf import PdfReader
        reader = PdfReader(str(output))
        assert len(reader.pages) == 2

    @pytest.mark.integration
    def test_merge_multiple_pdfs(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_files = []
        for i in range(3):
            pdf_path = temp_dir / f"file{i+1}.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.drawString(100, 750, f"File {i+1}")
            c.save()
            pdf_files.append(str(pdf_path))
        
        output = temp_dir / "merged.pdf"
        result = merge_pdfs(pdf_files, str(output))
        
        assert result is True
        assert output.exists()

    @pytest.mark.integration
    def test_merge_with_empty_pdf(self, temp_dir, empty_pdf_path):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_with_content = temp_dir / "content.pdf"
        c = canvas.Canvas(str(pdf_with_content), pagesize=letter)
        c.drawString(100, 750, "Content Page")
        c.save()
        
        output = temp_dir / "merged.pdf"
        result = merge_pdfs([str(empty_pdf_path), str(pdf_with_content)], str(output))
        assert result is True

    @pytest.mark.integration
    def test_merge_preserves_order(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        files = []
        for i, label in enumerate(["First", "Second", "Third"]):
            pdf_path = temp_dir / f"{label.lower()}.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.drawString(100, 750, label)
            c.save()
            files.append(str(pdf_path))
        
        output = temp_dir / "merged.pdf"
        merge_pdfs(files, str(output))
        
        from pypdf import PdfReader
        reader = PdfReader(str(output))
        
        texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            texts.append(text)
        
        assert "First" in texts[0]
        assert "Second" in texts[1]
        assert "Third" in texts[2]


class TestMergePDFsEdgeCases:
    """Edge case tests for PDF merge."""

    @pytest.mark.integration
    def test_merge_single_file(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "single.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Single Page")
        c.save()
        
        output = temp_dir / "merged.pdf"
        result = merge_pdfs([str(pdf_path)], str(output))
        
        assert result is True
        assert output.exists()

    @pytest.mark.unit
    def test_merge_empty_list(self, temp_dir):
        pytest.importorskip("pypdf")
        from merge_pdfs import merge_pdfs
        output_file = temp_dir / "merged.pdf"
        result = merge_pdfs([], str(output_file))
        # Empty list creates an empty PDF (returns True)
        assert result is True
