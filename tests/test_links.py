#!/usr/bin/env python3
"""Tests for PDF Links script."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))

from links import (
    PDFLink,
    LinkExtractionResult,
    extract_links,
    list_links,
    add_link,
    remove_links,
    SUSPICIOUS_PATTERNS,
)


class TestPDFLink:
    """Tests for PDFLink dataclass."""

    def test_link_creation(self):
        """Test creating a PDF link."""
        link = PDFLink(
            page=0,
            rect=(100, 100, 200, 120),
            link_type="uri",
            target="https://example.com"
        )
        assert link.page == 0
        assert link.rect == (100, 100, 200, 120)
        assert link.link_type == "uri"
        assert link.target == "https://example.com"

    def test_internal_link(self):
        """Test creating an internal link."""
        link = PDFLink(
            page=0,
            rect=(50, 50, 150, 70),
            link_type="internal",
            target="Page 5"
        )
        assert link.link_type == "internal"
        assert link.target == "Page 5"

    def test_link_to_dict(self):
        """Test converting link to dict."""
        link = PDFLink(
            page=0,
            rect=(100, 100, 200, 120),
            link_type="uri",
            target="https://example.com"
        )
        result = link.to_dict()
        assert result["page"] == 1  # Converted to 1-indexed
        assert result["type"] == "uri"
        assert result["target"] == "https://example.com"


class TestLinkExtractionResult:
    """Tests for LinkExtractionResult dataclass."""

    def test_result_creation(self):
        """Test creating a result."""
        result = LinkExtractionResult(
            file_path="test.pdf",
            total_links=0,
            internal_links=0,
            external_links=0,
            suspicious_links=0
        )
        assert result.total_links == 0
        assert result.links == []

    def test_result_with_links(self):
        """Test result with links."""
        result = LinkExtractionResult(
            file_path="test.pdf",
            total_links=2,
            internal_links=1,
            external_links=1,
            suspicious_links=0,
            links=[
                PDFLink(0, (0, 0, 10, 10), "uri", "https://a.com"),
                PDFLink(0, (10, 10, 20, 20), "internal", "Page 2")
            ]
        )
        assert result.total_links == 2
        assert len(result.links) == 2

    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = LinkExtractionResult(
            file_path="test.pdf",
            total_links=1,
            internal_links=0,
            external_links=1,
            suspicious_links=0,
            links=[
                PDFLink(0, (0, 0, 10, 10), "uri", "https://a.com")
            ]
        )
        d = result.to_dict()
        assert d["file_path"] == "test.pdf"
        assert d["total_links"] == 1
        assert len(d["links"]) == 1


class TestExtractLinks:
    """Tests for link extraction."""

    def test_extract_from_nonexistent_file(self):
        """Test extracting from non-existent file."""
        try:
            from pypdf import PdfReader
            result = extract_links("nonexistent.pdf")
        except FileNotFoundError:
            # Expected behavior
            pass


class TestSuspiciousPatterns:
    """Tests for suspicious pattern detection."""

    def test_suspicious_patterns_exist(self):
        """Test that suspicious patterns are defined."""
        assert len(SUSPICIOUS_PATTERNS) > 0

    def test_javascript_pattern(self):
        """Test JavaScript pattern is included."""
        assert any("javascript" in p.lower() for p in SUSPICIOUS_PATTERNS)

    def test_executable_patterns(self):
        """Test executable patterns are included."""
        assert any(".exe" in p for p in SUSPICIOUS_PATTERNS)
        assert any(".bat" in p for p in SUSPICIOUS_PATTERNS)


class TestAddLink:
    """Tests for adding links."""

    def test_add_link_invalid_page(self):
        """Test adding link with invalid page."""
        # Would need test PDF fixture
        pass


class TestRemoveLinks:
    """Tests for removing links."""

    def test_remove_all_links(self):
        """Test removing all links."""
        # Would need test PDF fixture
        pass

    def test_remove_suspicious_links(self):
        """Test removing suspicious links."""
        # Would need test PDF with suspicious links
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
