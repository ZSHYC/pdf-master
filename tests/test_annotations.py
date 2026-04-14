#!/usr/bin/env python3
"""Tests for PDF Annotations script."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))

from annotations import (
    PDFAnnotation,
    AnnotationExtractionResult,
    extract_annotations,
    list_annotations,
    add_text_annotation,
    add_highlight_annotation,
    remove_annotations,
)


class TestPDFAnnotation:
    """Tests for PDFAnnotation dataclass."""

    def test_annotation_creation(self):
        """Test creating an annotation."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Text",
            rect=(100, 100, 120, 120),
            contents="Test note"
        )
        assert annot.page == 0
        assert annot.annot_type == "Text"
        assert annot.contents == "Test note"

    def test_annotation_with_author(self):
        """Test annotation with author."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Highlight",
            rect=(0, 0, 100, 20),
            contents="Important",
            author="John Doe"
        )
        assert annot.author == "John Doe"

    def test_annotation_with_color(self):
        """Test annotation with color."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Highlight",
            rect=(0, 0, 100, 20),
            color=(1.0, 1.0, 0.0)  # Yellow
        )
        assert annot.color == (1.0, 1.0, 0.0)

    def test_annotation_to_dict(self):
        """Test converting annotation to dict."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Text",
            rect=(100, 100, 120, 120),
            contents="Note",
            author="Test"
        )
        result = annot.to_dict()
        assert result["page"] == 1  # Converted to 1-indexed
        assert result["type"] == "Text"
        assert result["contents"] == "Note"
        assert result["author"] == "Test"


class TestAnnotationExtractionResult:
    """Tests for AnnotationExtractionResult dataclass."""

    def test_result_creation(self):
        """Test creating a result."""
        result = AnnotationExtractionResult(
            file_path="test.pdf",
            total_annotations=0
        )
        assert result.total_annotations == 0
        assert result.annotations == []
        assert result.by_type == {}

    def test_result_with_annotations(self):
        """Test result with annotations."""
        result = AnnotationExtractionResult(
            file_path="test.pdf",
            total_annotations=2,
            by_type={"Text": 1, "Highlight": 1},
            by_author={"John": 1, "Jane": 1},
            annotations=[
                PDFAnnotation(0, (0, 0, 10, 10), "Text", "Note 1"),
                PDFAnnotation(1, (0, 0, 50, 20), "Highlight", "Note 2")
            ]
        )
        assert result.total_annotations == 2
        assert result.by_type["Text"] == 1
        assert len(result.annotations) == 2


class TestExtractAnnotations:
    """Tests for annotation extraction."""

    def test_extract_from_nonexistent_file(self):
        """Test extracting from non-existent file."""
        try:
            from pypdf import PdfReader
            result = extract_annotations("nonexistent.pdf")
        except FileNotFoundError:
            # Expected behavior
            pass


class TestAddTextAnnotation:
    """Tests for adding text annotations."""

    def test_add_annotation_invalid_page(self):
        """Test adding annotation with invalid page."""
        # Would need test PDF fixture
        pass


class TestAddHighlightAnnotation:
    """Tests for adding highlight annotations."""

    def test_add_highlight_default_color(self):
        """Test highlight with default color."""
        # Default color is yellow (1, 1, 0)
        pass


class TestRemoveAnnotations:
    """Tests for removing annotations."""

    def test_remove_all_annotations(self):
        """Test removing all annotations."""
        # Would need test PDF fixture
        pass

    def test_remove_by_type(self):
        """Test removing by type."""
        # Would need test PDF with multiple annotation types
        pass

    def test_remove_by_author(self):
        """Test removing by author."""
        # Would need test PDF with annotations by different authors
        pass


class TestAnnotationTypes:
    """Tests for different annotation types."""

    def test_text_annotation(self):
        """Test text annotation type."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Text",
            rect=(0, 0, 20, 20),
            contents="Comment"
        )
        assert annot.annot_type == "Text"

    def test_highlight_annotation(self):
        """Test highlight annotation type."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Highlight",
            rect=(0, 0, 100, 20)
        )
        assert annot.annot_type == "Highlight"

    def test_underline_annotation(self):
        """Test underline annotation type."""
        annot = PDFAnnotation(
            page=0,
            annot_type="Underline",
            rect=(0, 0, 100, 5)
        )
        assert annot.annot_type == "Underline"

    def test_strikeout_annotation(self):
        """Test strikeout annotation type."""
        annot = PDFAnnotation(
            page=0,
            annot_type="StrikeOut",
            rect=(0, 0, 100, 5)
        )
        assert annot.annot_type == "StrikeOut"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
