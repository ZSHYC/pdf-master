#!/usr/bin/env python3
"""
Tests for PDF Batch Rename Script

Tests cover:
- Naming rules (metadata, content, date, custom)
- Template formatting
- Filename sanitization
- Conflict resolution
- Batch operations
"""

import json
import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rename_pdf import (
    NamingRule,
    MetadataNamingRule,
    ContentNamingRule,
    DateNamingRule,
    CustomNamingRule,
    parse_pdf_date,
    sanitize_filename,
    generate_unique_name,
    batch_rename,
)


class TestParsePdfDate:
    """Tests for parse_pdf_date function."""

    def test_parse_standard_date(self):
        """Test parsing standard PDF date format."""
        result = parse_pdf_date("D:20231215143000")
        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0

    def test_parse_date_without_prefix(self):
        """Test parsing date without D: prefix."""
        result = parse_pdf_date("20231215143000")
        assert result is not None
        assert result.year == 2023

    def test_parse_partial_date(self):
        """Test parsing partial date."""
        result = parse_pdf_date("D:202312")
        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 1

    def test_parse_none(self):
        """Test parsing None value."""
        assert parse_pdf_date(None) is None

    def test_parse_invalid(self):
        """Test parsing invalid date string."""
        assert parse_pdf_date("invalid") is None


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_remove_invalid_chars(self):
        """Test removal of invalid characters."""
        assert sanitize_filename('file<>:"/\\|?*name') == "filename"

    def test_replace_spaces(self):
        """Test replacement of multiple spaces."""
        assert sanitize_filename("file   name") == "file_name"

    def test_trim_underscores(self):
        """Test trimming of leading/trailing underscores."""
        assert sanitize_filename("_filename_") == "filename"

    def test_truncate_long_name(self):
        """Test truncation of long filenames."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 200


class TestGenerateUniqueName:
    """Tests for generate_unique_name function."""

    def test_no_conflict(self):
        """Test when no conflict exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            result = generate_unique_name(target_dir, "new_file.pdf")
            assert result == "new_file.pdf"

    def test_conflict_unique(self):
        """Test unique name generation on conflict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            (target_dir / "existing.pdf").touch()
            result = generate_unique_name(target_dir, "existing.pdf")
            assert result == "existing_1.pdf"

    def test_multiple_conflicts(self):
        """Test unique name with multiple conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            (target_dir / "existing.pdf").touch()
            (target_dir / "existing_1.pdf").touch()
            result = generate_unique_name(target_dir, "existing.pdf")
            assert result == "existing_2.pdf"


class TestMetadataNamingRule:
    """Tests for MetadataNamingRule class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rule = MetadataNamingRule("{title}")

    @patch('rename_pdf.PdfReader')
    def test_extract_metadata(self, mock_reader_class):
        """Test metadata extraction from PDF."""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock()]
        mock_reader.metadata = {
            '/Title': 'Test Document',
            '/Author': 'Test Author',
            '/CreationDate': 'D:20231215143000'
        }
        mock_reader_class.return_value = mock_reader

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            info = self.rule.extract_info(tmp_path)
            assert info['title'] == 'Test Document'
            assert info['author'] == 'Test Author'
            assert info['creation_date'] is not None
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_format_template_simple(self):
        """Test simple template formatting."""
        info = {
            'title': 'Test Document',
            'author': 'Test Author'
        }
        result = self.rule._format_template(
            "{author} - {title}",
            info,
            Path("test.pdf")
        )
        assert result == "Test_Author_-_Test_Document.pdf"


class TestContentNamingRule:
    """Tests for ContentNamingRule class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rule = ContentNamingRule("{title}")

    def test_clean_title(self):
        """Test title cleaning."""
        result = self.rule._clean_title('Test<>:"Title')
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result

    def test_looks_like_title(self):
        """Test title detection heuristic."""
        assert self.rule._looks_like_title("Introduction to PDF")
        assert not self.rule._looks_like_title("lowercase title")
        assert not self.rule._looks_like_title("a")
        assert not self.rule._looks_like_title("This is a sentence.")


class TestDateNamingRule:
    """Tests for DateNamingRule class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rule = DateNamingRule("{date:%Y-%m-%d}_{filename}")

    def test_extract_date_components(self):
        """Test date component extraction."""
        info = {
            'date': datetime(2023, 12, 15),
            'year': 2023,
            'month': '12',
            'day': '15'
        }
        result = self.rule._format_template(
            "{year}-{month}-{day}",
            info,
            Path("test.pdf")
        )
        assert result == "2023-12-15.pdf"


class TestCustomNamingRule:
    """Tests for CustomNamingRule class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rule = CustomNamingRule(
            "{doc_id}",
            patterns={'doc_id': r'DOC-(\d+)'}
        )

    def test_extract_from_filename(self):
        """Test pattern extraction from filename."""
        info = self.rule.extract_info(Path("/path/DOC-12345_report.pdf"))
        assert info.get('doc_id') == '12345'


class TestBatchRename:
    """Tests for batch_rename function."""

    def test_dry_run(self):
        """Test dry run mode (no actual rename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test PDF files
            files = []
            for i in range(3):
                pdf_path = Path(tmpdir) / f"test_{i}.pdf"
                pdf_path.touch()
                files.append(pdf_path)

            rule = CustomNamingRule("renamed_{counter:02d}.pdf")

            results = batch_rename(
                files=files,
                rule=rule,
                dry_run=True
            )

            assert results['total'] == 3
            assert results['renamed'] == 3
            # Files should not be renamed
            for f in files:
                assert f.exists()

    def test_actual_rename(self):
        """Test actual rename operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test PDF file
            pdf_path = Path(tmpdir) / "original.pdf"
            pdf_path.touch()

            rule = CustomNamingRule("renamed.pdf")

            results = batch_rename(
                files=[pdf_path],
                rule=rule,
                dry_run=False
            )

            assert results['renamed'] == 1
            assert not pdf_path.exists()
            assert (Path(tmpdir) / "renamed.pdf").exists()

    def test_missing_file(self):
        """Test handling of missing file."""
        rule = CustomNamingRule("test.pdf")

        results = batch_rename(
            files=[Path("/nonexistent/file.pdf")],
            rule=rule,
            dry_run=True
        )

        assert results['errors'] == 1

    def test_output_directory(self):
        """Test renaming to different output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            output_dir = Path(tmpdir) / "output"
            source_dir.mkdir()

            pdf_path = source_dir / "original.pdf"
            pdf_path.touch()

            rule = CustomNamingRule("moved.pdf")

            results = batch_rename(
                files=[pdf_path],
                rule=rule,
                output_dir=output_dir,
                dry_run=False
            )

            assert results['renamed'] == 1
            assert not pdf_path.exists()
            assert (output_dir / "moved.pdf").exists()


class TestTemplateFormatting:
    """Tests for template formatting features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rule = NamingRule("")

    def test_date_formatting(self):
        """Test date formatting in template."""
        info = {
            'date': datetime(2023, 12, 15, 14, 30)
        }
        result = self.rule._format_template(
            "{date:%Y-%m-%d}",
            info,
            Path("test.pdf")
        )
        assert result == "2023-12-15.pdf"

    def test_counter_formatting(self):
        """Test counter formatting in template."""
        info = {'counter': 42}
        result = self.rule._format_template(
            "doc_{counter:04d}",
            info,
            Path("test.pdf")
        )
        assert result == "doc_0042.pdf"

    def test_multiple_placeholders(self):
        """Test multiple placeholders in template."""
        info = {
            'author': 'John Doe',
            'title': 'Test Document',
            'year': 2023
        }
        result = self.rule._format_template(
            "{year}_{author}_{title}",
            info,
            Path("test.pdf")
        )
        assert "John_Doe" in result
        assert "Test_Document" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
