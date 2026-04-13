"""
Tests for Batch Processing Functionality
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestExpandPDFFiles:
    """Tests for expand_pdf_files function."""

    @pytest.mark.unit
    def test_expand_pdf_files_returns_list(self):
        from pdf_utils import expand_pdf_files
        result = expand_pdf_files("nonexistent_*.pdf")
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_expand_pdf_files_with_pdfs(self, temp_dir):
        from pdf_utils import expand_pdf_files
        for i in range(3):
            pdf = temp_dir / f"test{i}.pdf"
            pdf.write_bytes(b"%PDF-1.4 test")
        result = expand_pdf_files(str(temp_dir / "test*.pdf"))
        assert len(result) >= 3

    @pytest.mark.unit
    def test_expand_pdf_files_directory(self, temp_dir):
        from pdf_utils import expand_pdf_files
        for i in range(2):
            pdf = temp_dir / f"doc{i}.pdf"
            pdf.write_bytes(b"%PDF-1.4 test")
        result = expand_pdf_files(str(temp_dir))
        assert len(result) >= 2

    @pytest.mark.unit
    def test_expand_pdf_files_empty(self):
        from pdf_utils import expand_pdf_files
        result = expand_pdf_files("nonexistent_directory_xyz/*.pdf")
        assert result == []


class TestProgressReporter:
    """Tests for ProgressReporter class."""

    @pytest.mark.unit
    def test_progress_reporter_init(self):
        from pdf_utils import ProgressReporter
        reporter = ProgressReporter(100, "Processing")
        assert reporter.total == 100
        assert reporter.desc == "Processing"
        assert reporter.current == 0

    @pytest.mark.unit
    def test_progress_reporter_update(self):
        from pdf_utils import ProgressReporter
        reporter = ProgressReporter(100, "Test")
        reporter.update(50)
        assert reporter.current == 50

    @pytest.mark.unit
    def test_progress_reporter_finish(self, capsys):
        from pdf_utils import ProgressReporter
        reporter = ProgressReporter(100, "Test")
        reporter.update(100)
        reporter.finish()

    @pytest.mark.unit
    def test_progress_reporter_format_time(self):
        from pdf_utils import ProgressReporter
        reporter = ProgressReporter(100, "Test")
        result = reporter._format_time(65)
        assert "01:05" in result

    @pytest.mark.unit
    def test_progress_reporter_format_time_negative(self):
        from pdf_utils import ProgressReporter
        reporter = ProgressReporter(100, "Test")
        result = reporter._format_time(-10)
        assert "--:--" in result


class TestBatchOperations:
    """Tests for batch processing operations."""

    @pytest.mark.integration
    def test_batch_merge(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from merge_pdfs import merge_pdfs
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_files = []
        for i in range(5):
            pdf_path = temp_dir / f"batch_{i}.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.drawString(100, 750, f"Document {i}")
            c.save()
            pdf_files.append(str(pdf_path))
        
        output = str(temp_dir / "merged_batch.pdf")
        result = merge_pdfs(pdf_files, output)
        assert result is True

    @pytest.mark.integration
    def test_batch_split(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from split_pdf import extract_single_pages
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "batch_source.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        for i in range(3):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        c.save()
        
        output_dir = str(temp_dir / "split_pages")
        result = extract_single_pages(str(pdf_path), output_dir, verbose=False)
        assert result is True


class TestFileUtilities:
    """Tests for file utility functions."""

    @pytest.mark.unit
    def test_safe_filename_normal(self):
        from pdf_utils import safe_filename
        result = safe_filename("normal_file_name.pdf")
        assert result == "normal_file_name.pdf"

    @pytest.mark.unit
    def test_safe_filename_special_chars(self):
        from pdf_utils import safe_filename
        result = safe_filename('file<>:"/\|?*.pdf')
        illegal_chars = '<>:"/\|?*'
        for char in illegal_chars:
            assert char not in result

    @pytest.mark.unit
    def test_safe_filename_long(self):
        from pdf_utils import safe_filename
        long_name = "a" * 300 + ".pdf"
        result = safe_filename(long_name, max_length=100)
        assert len(result) <= 100

    @pytest.mark.unit
    def test_safe_filename_unicode(self):
        from pdf_utils import safe_filename
        result = safe_filename("file_chinese.pdf")
        assert result.endswith(".pdf")

    @pytest.mark.unit
    def test_print_error(self, capsys):
        from pdf_utils import print_error
        print_error("Test error message")
        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or captured.out != ""

    @pytest.mark.unit
    def test_print_warning(self, capsys):
        from pdf_utils import print_warning
        print_warning("Test warning")
        captured = capsys.readouterr()
        assert "warning" in captured.err.lower() or captured.out != ""

    @pytest.mark.unit
    def test_print_success(self, capsys):
        from pdf_utils import print_success
        print_success("Test success")
        captured = capsys.readouterr()
