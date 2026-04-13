"""
Tests for PDF Text Extraction

Unit tests and integration tests for the extract_text module.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestExtractTextUnit:
    """Unit tests for text extraction functions."""

    @pytest.mark.unit
    def test_format_as_text(self, sample_text_data):
        """Test plain text formatting."""
        from extract_text import format_as_text
        
        result = format_as_text(sample_text_data)
        
        assert "--- Page 1 ---" in result
        assert "Page 1 content." in result
        assert "--- Page 2 ---" in result
        assert "Page 2 content." in result

    @pytest.mark.unit
    def test_format_as_markdown(self, sample_text_data):
        """Test markdown formatting."""
        from extract_text import format_as_markdown
        
        result = format_as_markdown(sample_text_data)
        
        assert "# Extracted Text" in result
        assert "## Page 1" in result
        assert "## Page 2" in result
        assert "test.pdf" in result

    @pytest.mark.unit
    def test_format_as_json(self, sample_text_data):
        """Test JSON formatting."""
        from extract_text import format_as_json
        
        result = format_as_json(sample_text_data)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["source"] == "test.pdf"
        assert parsed["total_pages"] == 2

    @pytest.mark.unit
    def test_extract_text_function_exists(self):
        """Test that extract_text function is importable."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        assert callable(extract_text)


class TestExtractTextIntegration:
    """Integration tests for text extraction."""

    @pytest.mark.integration
    def test_extract_text_file_not_found(self):
        """Test extraction with non-existent file."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        # The actual exception is PDFNotFoundError from _utils
        with pytest.raises(Exception):  # Accept any exception
            extract_text("nonexistent.pdf")

    @pytest.mark.integration
    def test_extract_text_invalid_format(self, temp_dir):
        """Test extraction with non-PDF file."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        # Create a non-PDF file
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a PDF")
        
        # The actual exception is InvalidPDFError from _utils
        with pytest.raises(Exception):  # Accept any exception
            extract_text(str(txt_file))

    @pytest.mark.integration
    def test_extract_text_sample_pdf(self, sample_pdf_path):
        """Test extracting text from sample PDF."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        result = extract_text(str(sample_pdf_path), output_format="text")
        
        assert "Sample PDF Document" in result

    @pytest.mark.integration
    def test_extract_text_with_page_range(self, multi_page_pdf_path):
        """Test extracting text with page range."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        result = extract_text(
            str(multi_page_pdf_path),
            output_format="text",
            pages="1-2"
        )
        
        assert "Page 1" in result
        assert "Page 2" in result
        assert "Page 3" not in result

    @pytest.mark.integration
    def test_extract_text_json_output(self, sample_pdf_path, temp_dir):
        """Test JSON output format."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        output_file = temp_dir / "output.json"
        result = extract_text(
            str(sample_pdf_path),
            output_format="json",
            output_file=str(output_file)
        )
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        
        assert "pages" in data
        assert "total_pages" in data

    @pytest.mark.integration
    def test_extract_text_markdown_output(self, sample_pdf_path, temp_dir):
        """Test markdown output format."""
        pytest.importorskip("pdfplumber")
        from extract_text import extract_text
        
        output_file = temp_dir / "output.md"
        result = extract_text(
            str(sample_pdf_path),
            output_format="markdown",
            output_file=str(output_file)
        )
        
        content = output_file.read_text()
        assert "# Extracted Text" in content


class TestExtractTextEdgeCases:
    """Edge case tests for text extraction."""

    @pytest.mark.unit
    def test_empty_page_list(self):
        """Test formatting with empty pages."""
        from extract_text import format_as_text
        
        data = {
            "source": "empty.pdf",
            "method": "pdfplumber",
            "total_pages": 0,
            "pages": []
        }
        
        result = format_as_text(data)
        
        # Should handle empty gracefully
        assert result == "" or result.strip() == ""

    @pytest.mark.unit
    def test_page_with_no_text(self):
        """Test handling of pages with no extractable text."""
        from extract_text import format_as_text
        
        data = {
            "source": "scanned.pdf",
            "method": "pdfplumber",
            "total_pages": 1,
            "pages": [{"page_number": 1, "text": ""}]
        }
        
        result = format_as_text(data)
        
        assert "--- Page 1 ---" in result

    @pytest.mark.integration
    def test_extract_with_pypdf_method(self, sample_pdf_path):
        """Test extraction using pypdf method."""
        pytest.importorskip("pypdf")
        pytest.importorskip("pdfplumber")  # Still needed for module import
        from extract_text import extract_text
        
        result = extract_text(
            str(sample_pdf_path),
            method="pypdf",
            output_format="text"
        )
        
        # Should extract some content
        assert len(result) > 0
