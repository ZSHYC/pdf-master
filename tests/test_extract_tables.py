"""
Tests for PDF Table Extraction

Unit tests and integration tests for the extract_tables module.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestExtractTablesUnit:
    """Unit tests for table extraction functions."""

    @pytest.mark.unit
    def test_format_as_json(self, sample_table_data):
        """Test JSON formatting for tables."""
        from extract_tables import format_as_json
        
        result = format_as_json(sample_table_data)
        
        parsed = json.loads(result)
        assert parsed["total_tables"] == 1
        assert len(parsed["pages"]) == 1

    @pytest.mark.unit
    def test_format_as_csv(self, sample_table_data):
        """Test CSV formatting for tables."""
        from extract_tables import format_as_csv
        
        result = format_as_csv(sample_table_data)
        
        # CSV should contain the data
        assert "Name" in result
        assert "John" in result or "30" in result

    @pytest.mark.unit
    def test_extract_tables_function_exists(self):
        """Test that extract_tables function exists."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_tables
        
        assert callable(extract_tables)


class TestExtractTablesIntegration:
    """Integration tests for table extraction."""

    @pytest.mark.integration
    def test_extract_tables_file_not_found(self):
        """Test extraction with non-existent file."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_and_save
        
        with pytest.raises(FileNotFoundError):
            extract_and_save("nonexistent.pdf")

    @pytest.mark.integration
    def test_extract_tables_invalid_format(self, temp_dir):
        """Test extraction with non-PDF file."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_and_save
        
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a PDF")
        
        with pytest.raises(ValueError):
            extract_and_save(str(txt_file))

    @pytest.mark.integration
    def test_extract_tables_sample_pdf(self, sample_pdf_path):
        """Test extracting tables from sample PDF."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_tables
        
        result = extract_tables(sample_pdf_path)
        
        assert "source" in result
        assert "pages" in result
        assert "total_tables" in result

    @pytest.mark.integration
    def test_extract_tables_json_output(self, sample_pdf_path, temp_dir):
        """Test JSON output for tables."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_and_save
        
        output_file = temp_dir / "tables.json"
        result = extract_and_save(
            str(sample_pdf_path),
            output_format="json",
            output_file=str(output_file)
        )
        
        assert output_file.exists()
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert "total_tables" in data

    @pytest.mark.integration
    def test_extract_tables_csv_output(self, sample_pdf_path, temp_dir):
        """Test CSV output for tables."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_and_save
        
        output_file = temp_dir / "tables.csv"
        result = extract_and_save(
            str(sample_pdf_path),
            output_format="csv",
            output_file=str(output_file)
        )
        
        assert output_file.exists()

    @pytest.mark.integration
    def test_extract_tables_excel_output(self, sample_pdf_path, temp_dir):
        """Test Excel output for tables."""
        pytest.importorskip("pdfplumber")
        pytest.importorskip("pandas")
        from extract_tables import extract_and_save
        
        output_file = temp_dir / "tables.xlsx"
        result = extract_and_save(
            str(sample_pdf_path),
            output_format="excel",
            output_file=str(output_file)
        )
        
        assert output_file.exists()


class TestExtractTablesEdgeCases:
    """Edge case tests for table extraction."""

    @pytest.mark.unit
    def test_empty_table_data(self):
        """Test handling of empty table data."""
        from extract_tables import format_as_json
        
        data = {
            "source": "empty.pdf",
            "total_tables": 0,
            "pages": []
        }
        
        result = format_as_json(data)
        
        parsed = json.loads(result)
        assert parsed["total_tables"] == 0

    @pytest.mark.unit
    def test_extract_tables_callable(self):
        """Test that extract_tables is callable."""
        pytest.importorskip("pdfplumber")
        from extract_tables import extract_tables
        
        # Verify the function signature
        assert callable(extract_tables)
