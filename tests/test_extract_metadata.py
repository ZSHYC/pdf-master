"""
Tests for PDF Metadata Extraction
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestExtractMetadataUnit:
    """Unit tests for metadata extraction functions."""

    @pytest.mark.unit
    def test_parse_pdf_date_valid(self):
        from extract_metadata import parse_pdf_date
        result = parse_pdf_date("D:20240115120000")
        assert "2024-01-15" in result

    @pytest.mark.unit
    def test_parse_pdf_date_none(self):
        from extract_metadata import parse_pdf_date
        result = parse_pdf_date(None)
        assert result is None

    @pytest.mark.unit
    def test_parse_pdf_date_empty(self):
        from extract_metadata import parse_pdf_date
        result = parse_pdf_date("")
        assert result is None or result == ""

    @pytest.mark.unit
    def test_format_file_size_bytes(self):
        from extract_metadata import format_file_size
        result = format_file_size(500)
        assert "B" in result

    @pytest.mark.unit
    def test_format_file_size_kb(self):
        from extract_metadata import format_file_size
        result = format_file_size(1024)
        assert "KB" in result

    @pytest.mark.unit
    def test_format_file_size_mb(self):
        from extract_metadata import format_file_size
        result = format_file_size(1048576)
        assert "MB" in result

    @pytest.mark.unit
    def test_format_as_json(self):
        from extract_metadata import format_as_json
        data = {"test": "value"}
        result = format_as_json(data)
        parsed = json.loads(result)
        assert parsed["test"] == "value"

    @pytest.mark.unit
    def test_format_as_text(self):
        from extract_metadata import format_as_text
        data = {"file_info": {"filename": "test.pdf", "path": "/test", "size_bytes": 100, "size_human": "100 B"}, "document_info": {}, "technical_info": {"page_count": 1}, "security": {"is_encrypted": False}}
        result = format_as_text(data)
        assert "test.pdf" in result

    @pytest.mark.unit
    def test_format_as_markdown(self):
        from extract_metadata import format_as_markdown
        data = {"file_info": {"filename": "test.pdf", "path": "/test", "size_bytes": 100, "size_human": "100 B"}, "document_info": {}, "technical_info": {"page_count": 1}, "security": {"is_encrypted": False}}
        result = format_as_markdown(data)
        assert "#" in result

    @pytest.mark.unit
    def test_extract_metadata_function_exists(self):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        assert callable(extract_metadata)


class TestExtractMetadataIntegration:
    """Integration tests for metadata extraction."""

    @pytest.mark.integration
    def test_extract_metadata_file_not_found(self):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        with pytest.raises(Exception):
            extract_metadata("nonexistent.pdf")

    @pytest.mark.integration
    def test_extract_metadata_sample_pdf(self, sample_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(sample_pdf_path))
        assert "file_info" in result
        assert "document_info" in result
        assert "technical_info" in result
        assert "security" in result

    @pytest.mark.integration
    def test_extract_metadata_page_count(self, sample_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(sample_pdf_path))
        assert result["technical_info"]["page_count"] >= 1

    @pytest.mark.integration
    def test_extract_metadata_encryption_status(self, sample_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(sample_pdf_path))
        assert "is_encrypted" in result["security"]

    @pytest.mark.integration
    def test_extract_metadata_file_info(self, sample_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(sample_pdf_path))
        assert "filename" in result["file_info"]
        assert "size_bytes" in result["file_info"]


class TestExtractMetadataEdgeCases:
    """Edge case tests for metadata extraction."""

    @pytest.mark.unit
    def test_parse_pdf_date_partial(self):
        from extract_metadata import parse_pdf_date
        result = parse_pdf_date("D:20240115")
        assert result is not None

    @pytest.mark.unit
    def test_format_file_size_zero(self):
        from extract_metadata import format_file_size
        result = format_file_size(0)
        assert "0" in result

    @pytest.mark.unit
    def test_format_file_size_large(self):
        from extract_metadata import format_file_size
        result = format_file_size(1073741824)
        assert "GB" in result

    @pytest.mark.integration
    def test_extract_metadata_empty_pdf(self, empty_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(empty_pdf_path))
        assert result["technical_info"]["page_count"] == 0

    @pytest.mark.integration
    def test_extract_metadata_multi_page(self, multi_page_pdf_path):
        pytest.importorskip("pypdf")
        from extract_metadata import extract_metadata
        result = extract_metadata(str(multi_page_pdf_path))
        assert result["technical_info"]["page_count"] == 3
