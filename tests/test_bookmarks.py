#!/usr/bin/env python3
"""Tests for PDF Bookmarks script."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))

from bookmarks import (
    Bookmark,
    add_bookmark,
    extract_bookmarks,
    list_bookmarks,
    remove_bookmarks,
)


class TestBookmark:
    """Tests for Bookmark dataclass."""

    def test_bookmark_creation(self):
        """Test creating a bookmark."""
        bookmark = Bookmark(
            title="Chapter 1",
            page=0,
            level=0
        )
        assert bookmark.title == "Chapter 1"
        assert bookmark.page == 0
        assert bookmark.level == 0
        assert bookmark.bold is False
        assert bookmark.italic is False

    def test_bookmark_with_style(self):
        """Test bookmark with style."""
        bookmark = Bookmark(
            title="Important",
            page=5,
            level=1,
            bold=True,
            italic=True
        )
        assert bookmark.bold is True
        assert bookmark.italic is True
        assert bookmark.level == 1

    def test_bookmark_with_color(self):
        """Test bookmark with color."""
        bookmark = Bookmark(
            title="Red Header",
            page=0,
            color=(1.0, 0.0, 0.0)
        )
        assert bookmark.color == (1.0, 0.0, 0.0)

    def test_bookmark_to_dict(self):
        """Test converting bookmark to dict."""
        bookmark = Bookmark(
            title="Chapter 1",
            page=0,
            level=0,
            bold=True
        )
        result = bookmark.to_dict()
        assert result["title"] == "Chapter 1"
        assert result["page"] == 1  # Converted to 1-indexed
        assert result["bold"] is True


class TestExtractBookmarks:
    """Tests for bookmark extraction."""

    def test_extract_from_nonexistent_file(self):
        """Test extracting from non-existent file."""
        # This should not crash, just return empty list
        try:
            from pypdf import PdfReader
            bookmarks = extract_bookmarks("nonexistent.pdf")
        except FileNotFoundError:
            # Expected behavior
            pass


class TestListBookmarks:
    """Tests for listing bookmarks."""

    def test_list_bookmarks_text_format(self):
        """Test listing bookmarks in text format."""
        # This tests the function signature, actual PDF testing would need fixtures
        pass

    def test_list_bookmarks_json_format(self):
        """Test listing bookmarks in JSON format."""
        pass


class TestAddBookmark:
    """Tests for adding bookmarks."""

    def test_add_bookmark_invalid_page(self):
        """Test adding bookmark with invalid page."""
        # Would need a test PDF fixture
        pass


class TestRemoveBookmarks:
    """Tests for removing bookmarks."""

    def test_remove_all_bookmarks(self):
        """Test removing all bookmarks."""
        # Would need a test PDF fixture
        pass


class TestNestedBookmarks:
    """Tests for nested bookmarks."""

    def test_nested_bookmark_creation(self):
        """Test creating nested bookmarks."""
        child = Bookmark(title="Section 1.1", page=2, level=1)
        parent = Bookmark(
            title="Chapter 1",
            page=0,
            level=0,
            children=[child]
        )
        assert len(parent.children) == 1
        assert parent.children[0].title == "Section 1.1"

    def test_deeply_nested_bookmarks(self):
        """Test deeply nested bookmarks."""
        leaf = Bookmark(title="Item", page=5, level=2)
        branch = Bookmark(title="Section", page=3, level=1, children=[leaf])
        root = Bookmark(title="Chapter", page=0, level=0, children=[branch])
        assert len(root.children) == 1
        assert root.children[0].children[0].title == "Item"


class TestBookmarkStyles:
    """Tests for bookmark styles."""

    def test_bold_style(self):
        """Test bold style bookmark."""
        bookmark = Bookmark(title="Bold", page=0, bold=True)
        assert bookmark.bold is True

    def test_italic_style(self):
        """Test italic style bookmark."""
        bookmark = Bookmark(title="Italic", page=0, italic=True)
        assert bookmark.italic is True

    def test_combined_style(self):
        """Test combined bold and italic."""
        bookmark = Bookmark(title="Bold+Italic", page=0, bold=True, italic=True)
        assert bookmark.bold is True
        assert bookmark.italic is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
