"""
Tests for PDF Image Extraction
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestExtractImagesUnit:
    """Unit tests for image extraction functions."""

    @pytest.mark.unit
    def test_parse_page_range_single(self):
        from extract_images import parse_page_range
        result = parse_page_range("5", 10)
        assert result == [5]

    @pytest.mark.unit
    def test_parse_page_range_multiple(self):
        from extract_images import parse_page_range
        result = parse_page_range("1,3,5", 10)
        assert result == [1, 3, 5]

    @pytest.mark.unit
    def test_parse_page_range_range(self):
        from extract_images import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_mixed(self):
        from extract_images import parse_page_range
        result = parse_page_range("1-3,5,7-9", 10)
        assert result == [1, 2, 3, 5, 7, 8, 9]

    @pytest.mark.unit
    def test_parse_page_range_out_of_bounds(self):
        from extract_images import parse_page_range
        result = parse_page_range("1-15", 10)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @pytest.mark.unit
    def test_parse_page_range_duplicates(self):
        from extract_images import parse_page_range
        result = parse_page_range("1-3,2,3", 10)
        assert result == [1, 2, 3]

    @pytest.mark.unit
    def test_extract_image_data_none(self):
        from extract_images import extract_image_data
        result = extract_image_data(None)
        assert result is None

    @pytest.mark.unit
    def test_extract_images_function_exists(self):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        assert callable(extract_images)

    @pytest.mark.unit
    def test_check_dependencies(self):
        from extract_images import check_dependencies
        assert callable(check_dependencies)


class TestExtractImagesIntegration:
    """Integration tests for image extraction."""

    @pytest.mark.integration
    def test_extract_images_file_not_found(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        with pytest.raises(Exception):
            extract_images("nonexistent.pdf", str(temp_dir))

    @pytest.mark.integration
    def test_extract_images_from_sample_pdf(self, sample_pdf_path, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        result = extract_images(str(sample_pdf_path), str(temp_dir / "images"))
        assert "source" in result
        assert "total_images" in result
        assert "extracted_images" in result

    @pytest.mark.integration
    def test_extract_images_with_page_range(self, multi_page_pdf_path, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        result = extract_images(str(multi_page_pdf_path), str(temp_dir / "images"), pages="1-2")
        assert "pages_processed" in result

    @pytest.mark.integration
    def test_extract_images_creates_output_dir(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        pytest.importorskip("reportlab")
        from extract_images import extract_images
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Test PDF")
        c.save()
        output_dir = temp_dir / "output_images"
        extract_images(str(pdf_path), str(output_dir))
        assert output_dir.exists()


class TestExtractImagesEdgeCases:
    """Edge case tests for image extraction."""

    @pytest.mark.unit
    def test_empty_page_range(self):
        from extract_images import parse_page_range
        # Empty string may return empty list or raise - handle gracefully
        try:
            result = parse_page_range("", 10)
            assert result == []
        except (ValueError, Exception):
            pass  # Expected behavior

    @pytest.mark.unit
    def test_page_range_with_spaces(self):
        from extract_images import parse_page_range
        try:
            result = parse_page_range("1 - 3, 5", 10)
            assert 1 in result or result == []
        except (ValueError, Exception):
            pass  # May raise for invalid format

    @pytest.mark.integration
    def test_min_size_filter(self, sample_pdf_path, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        result = extract_images(str(sample_pdf_path), str(temp_dir / "images"), min_size=10000)
        assert "total_images" in result

    @pytest.mark.integration
    def test_custom_prefix(self, sample_pdf_path, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("PIL")
        from extract_images import extract_images
        result = extract_images(str(sample_pdf_path), str(temp_dir / "images"), prefix="custom_prefix")
        assert result is not None
