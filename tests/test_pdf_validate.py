"""
Tests for PDF Validation Functionality
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestPDFValidation:
    """Tests for PDF validation functions."""

    @pytest.mark.unit
    def test_validate_pdf_path_exists(self, sample_pdf_path):
        from _utils import validate_pdf_path
        result = validate_pdf_path(str(sample_pdf_path))
        assert result.exists()

    @pytest.mark.unit
    def test_validate_pdf_path_not_found(self):
        from _utils import validate_pdf_path, PDFNotFoundError
        with pytest.raises(PDFNotFoundError):
            validate_pdf_path("nonexistent.pdf")

    @pytest.mark.unit
    def test_validate_pdf_path_invalid_extension(self, temp_dir):
        from _utils import validate_pdf_path, InvalidPDFError
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a PDF")
        with pytest.raises(InvalidPDFError):
            validate_pdf_path(str(txt_file))

    @pytest.mark.unit
    def test_validate_output_path(self, temp_dir):
        from _utils import validate_output_path
        result = validate_output_path(str(temp_dir / "output" / "test.pdf"))
        assert result.parent.exists()

    @pytest.mark.unit
    def test_parse_page_range_valid(self):
        from _utils import parse_page_range
        result = parse_page_range("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_parse_page_range_invalid(self):
        from _utils import parse_page_range, PageRangeError
        with pytest.raises(PageRangeError):
            parse_page_range("invalid", 10)

    @pytest.mark.unit
    def test_parse_page_range_empty(self):
        from _utils import parse_page_range, PageRangeError
        with pytest.raises(PageRangeError):
            parse_page_range("", 10)

    @pytest.mark.unit
    def test_parse_page_range_zero(self):
        from _utils import parse_page_range, PageRangeError
        with pytest.raises(PageRangeError):
            parse_page_range("0", 10)

    @pytest.mark.unit
    def test_parse_page_range_negative(self):
        from _utils import parse_page_range, PageRangeError
        with pytest.raises(PageRangeError):
            parse_page_range("-1", 10)


class TestPDFUtilsValidation:
    """Tests for pdf_utils validation functions."""

    @pytest.mark.unit
    def test_validate_pdf_file_exists(self, sample_pdf_path):
        from pdf_utils import validate_pdf_file
        result = validate_pdf_file(str(sample_pdf_path))
        assert result.exists()

    @pytest.mark.unit
    def test_validate_pdf_file_not_found(self):
        from pdf_utils import validate_pdf_file
        with pytest.raises(FileNotFoundError):
            validate_pdf_file("nonexistent.pdf")

    @pytest.mark.unit
    def test_validate_pdf_file_invalid_extension(self, temp_dir):
        from pdf_utils import validate_pdf_file
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a PDF")
        with pytest.raises(ValueError):
            validate_pdf_file(str(txt_file))

    @pytest.mark.unit
    def test_safe_filename_removes_illegal_chars(self):
        from pdf_utils import safe_filename
        illegal_chars = '<>:"/\|?*'
        result = safe_filename('test_file.pdf')
        for char in illegal_chars:
            assert char not in result

    @pytest.mark.unit
    def test_safe_filename_preserves_valid(self):
        from pdf_utils import safe_filename
        result = safe_filename("valid_filename.pdf")
        assert result == "valid_filename.pdf"

    @pytest.mark.unit
    def test_safe_filename_limits_length(self):
        from pdf_utils import safe_filename
        long_name = "a" * 300
        result = safe_filename(long_name, max_length=100)
        assert len(result) <= 100


class TestDependencyValidation:
    """Tests for dependency validation."""

    @pytest.mark.unit
    def test_check_dependencies_returns_list(self):
        from _utils import check_dependencies
        result = check_dependencies(["os"])
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_check_dependencies_missing(self):
        from _utils import check_dependencies
        result = check_dependencies(["nonexistent_package_xyz123"])
        assert "nonexistent_package_xyz123" in result

    @pytest.mark.unit
    def test_require_dependencies_missing(self):
        from _utils import require_dependencies, DependencyError
        with pytest.raises(DependencyError):
            require_dependencies(["nonexistent_package_xyz123"])

    @pytest.mark.unit
    def test_require_dependencies_available(self):
        from _utils import require_dependencies
        require_dependencies(["os", "sys"])


class TestOutputValidation:
    """Tests for output path validation."""

    @pytest.mark.unit
    def test_validate_output_path_creates_dirs(self, temp_dir):
        from _utils import validate_output_path
        output = temp_dir / "subdir" / "output.pdf"
        result = validate_output_path(str(output), create_dirs=True)
        assert result.parent.exists()

    @pytest.mark.unit
    def test_validate_output_path_no_create(self, temp_dir):
        from _utils import validate_output_path
        output = temp_dir / "subdir" / "output.pdf"
        result = validate_output_path(str(output), create_dirs=False)
        assert result is not None
