"""
Tests for PDF Form Fields Functionality

Tests for check_fillable_fields and fill_fillable_fields modules.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestCheckFillableFieldsUnit:
    """Unit tests for checking form fields."""

    @pytest.mark.unit
    def test_get_field_type_text(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Tx"}
        result = get_field_type(field)
        assert result == "text"

    @pytest.mark.unit
    def test_get_field_type_checkbox(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Btn", "/Ff": 0}
        result = get_field_type(field)
        assert result == "checkbox"

    @pytest.mark.unit
    def test_get_field_type_radio(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Btn", "/Ff": 0x8000}
        result = get_field_type(field)
        assert result == "radio"

    @pytest.mark.unit
    def test_get_field_type_dropdown(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Ch", "/Ff": 0x20000}
        result = get_field_type(field)
        assert result == "dropdown"

    @pytest.mark.unit
    def test_get_field_type_signature(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Sig"}
        result = get_field_type(field)
        assert result == "signature"

    @pytest.mark.unit
    def test_get_field_name(self):
        from check_fillable_fields import get_field_name
        field = {"/T": "field_name"}
        result = get_field_name(field)
        assert result == "field_name"

    @pytest.mark.unit
    def test_get_field_value(self):
        from check_fillable_fields import get_field_value
        field = {"/V": "test_value"}
        result = get_field_value(field)
        assert result == "test_value"

    @pytest.mark.unit
    def test_is_field_readonly_true(self):
        from check_fillable_fields import is_field_readonly
        field = {"/Ff": 0x01}
        result = is_field_readonly(field)
        assert result is True

    @pytest.mark.unit
    def test_is_field_required_true(self):
        from check_fillable_fields import is_field_required
        field = {"/Ff": 0x02}
        result = is_field_required(field)
        assert result is True

    @pytest.mark.unit
    def test_check_fillable_fields_function_exists(self):
        pytest.importorskip("pypdf")
        from check_fillable_fields import check_fillable_fields
        assert callable(check_fillable_fields)


class TestFillFillableFieldsUnit:
    """Unit tests for filling form fields."""

    @pytest.mark.unit
    def test_get_field_type_text(self):
        from fill_fillable_fields import get_field_type
        field = {"/FT": "/Tx"}
        result = get_field_type(field)
        assert result == "text"

    @pytest.mark.unit
    def test_get_field_type_checkbox(self):
        from fill_fillable_fields import get_field_type
        field = {"/FT": "/Btn", "/Ff": 0}
        result = get_field_type(field)
        assert result == "checkbox"

    @pytest.mark.unit
    def test_parse_field_value_boolean(self):
        from fill_fillable_fields import parse_field_value
        result = parse_field_value("true")
        assert result is True
        result = parse_field_value("false")
        assert result is False

    @pytest.mark.unit
    def test_parse_field_value_number(self):
        from fill_fillable_fields import parse_field_value
        result = parse_field_value("42")
        assert result == 42
        result = parse_field_value("3.14")
        assert result == 3.14

    @pytest.mark.unit
    def test_parse_field_value_string(self):
        from fill_fillable_fields import parse_field_value
        result = parse_field_value("hello")
        assert result == "hello"

    @pytest.mark.unit
    def test_fill_pdf_form_function_exists(self):
        pytest.importorskip("pypdf")
        from fill_fillable_fields import fill_pdf_form
        assert callable(fill_pdf_form)


class TestFormFieldsIntegration:
    """Integration tests for form fields."""

    @pytest.mark.integration
    def test_check_fillable_fields_no_form(self, sample_pdf_path):
        pytest.importorskip("pypdf")
        from check_fillable_fields import check_fillable_fields
        result = check_fillable_fields(str(sample_pdf_path))
        assert "has_form" in result
        assert "field_count" in result
        assert "fields" in result

    @pytest.mark.integration
    def test_check_fillable_fields_file_not_found(self):
        pytest.importorskip("pypdf")
        from check_fillable_fields import check_fillable_fields
        with pytest.raises(Exception):
            check_fillable_fields("nonexistent.pdf")

    @pytest.mark.integration
    def test_format_as_json(self):
        from check_fillable_fields import format_as_json
        data = {"has_form": False, "field_count": 0, "fields": [], "file_info": {"filename": "test.pdf", "path": "/test"}}
        result = format_as_json(data)
        import json
        parsed = json.loads(result)
        assert parsed["has_form"] is False

    @pytest.mark.integration
    def test_format_as_text(self):
        from check_fillable_fields import format_as_text
        data = {"has_form": False, "field_count": 0, "fields": [], "file_info": {"filename": "test.pdf", "path": "/test"}}
        result = format_as_text(data)
        assert "test.pdf" in result

    @pytest.mark.integration
    def test_format_as_markdown(self):
        from check_fillable_fields import format_as_markdown
        data = {"has_form": False, "field_count": 0, "fields": [], "file_info": {"filename": "test.pdf", "path": "/test"}}
        result = format_as_markdown(data)
        assert "#" in result


class TestFormFieldsEdgeCases:
    """Edge case tests for form fields."""

    @pytest.mark.unit
    def test_get_field_type_unknown(self):
        from check_fillable_fields import get_field_type
        field = {"/FT": "/Unknown"}
        result = get_field_type(field)
        assert result == "unknown"

    @pytest.mark.unit
    def test_get_field_value_none(self):
        from check_fillable_fields import get_field_value
        field = {}
        result = get_field_value(field)
        assert result is None

    @pytest.mark.unit
    def test_get_field_name_bytes(self):
        from check_fillable_fields import get_field_name
        field = {"/T": b"bytes_name"}
        result = get_field_name(field)
        assert "name" in result.lower() or result != ""

    @pytest.mark.unit
    def test_is_field_readonly_false(self):
        from check_fillable_fields import is_field_readonly
        field = {"/Ff": 0}
        result = is_field_readonly(field)
        assert result is False

    @pytest.mark.integration
    def test_check_fillable_fields_empty_pdf(self, empty_pdf_path):
        pytest.importorskip("pypdf")
        from check_fillable_fields import check_fillable_fields
        result = check_fillable_fields(str(empty_pdf_path))
        assert result["field_count"] == 0
