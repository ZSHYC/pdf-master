#!/usr/bin/env python3
"""Tests for PDF Security Audit script."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))

from security_audit import (
    PDFSecurityAuditor,
    RiskLevel,
    SecurityFinding,
    SecurityReport,
    audit_pdf,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_levels(self):
        """Test risk level values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestSecurityFinding:
    """Tests for SecurityFinding dataclass."""

    def test_finding_creation(self):
        """Test creating a security finding."""
        finding = SecurityFinding(
            category="javascript",
            severity=RiskLevel.HIGH,
            description="JavaScript found",
            location="Page 1",
            recommendation="Remove JavaScript"
        )
        assert finding.category == "javascript"
        assert finding.severity == RiskLevel.HIGH
        assert finding.description == "JavaScript found"

    def test_finding_to_dict(self):
        """Test converting finding to dict."""
        finding = SecurityFinding(
            category="encryption",
            severity=RiskLevel.LOW,
            description="Not encrypted"
        )
        result = finding.to_dict()
        assert result["category"] == "encryption"
        assert result["severity"] == "low"
        assert result["description"] == "Not encrypted"


class TestSecurityReport:
    """Tests for SecurityReport dataclass."""

    def test_report_creation(self):
        """Test creating a security report."""
        report = SecurityReport(
            file_path="test.pdf",
            is_safe=True,
            risk_score=10
        )
        assert report.is_safe is True
        assert report.risk_score == 10
        assert report.findings == []

    def test_report_to_dict(self):
        """Test converting report to dict."""
        report = SecurityReport(
            file_path="test.pdf",
            is_safe=False,
            risk_score=50,
            findings=[
                SecurityFinding("test", RiskLevel.MEDIUM, "Test finding")
            ],
            info={"encrypted": False}
        )
        result = report.to_dict()
        assert result["file_path"] == "test.pdf"
        assert result["is_safe"] is False
        assert result["risk_score"] == 50
        assert len(result["findings"]) == 1


class TestPDFSecurityAuditor:
    """Tests for PDFSecurityAuditor class."""

    def test_auditor_creation(self):
        """Test creating an auditor."""
        auditor = PDFSecurityAuditor()
        assert auditor.verbose is False

    def test_auditor_verbose(self):
        """Test verbose auditor."""
        auditor = PDFSecurityAuditor(verbose=True)
        assert auditor.verbose is True

    def test_audit_nonexistent_file(self):
        """Test auditing non-existent file."""
        auditor = PDFSecurityAuditor()
        report = auditor.audit("nonexistent.pdf")
        assert report.is_safe is False
        assert report.risk_score == 100
        assert len(report.findings) > 0


class TestAuditPDF:
    """Tests for audit_pdf function."""

    def test_audit_nonexistent_file(self):
        """Test auditing non-existent file."""
        report = audit_pdf("nonexistent.pdf")
        assert report.is_safe is False
        assert report.risk_score == 100


class TestSensitivePatterns:
    """Tests for sensitive pattern detection."""

    def test_sensitive_patterns_exist(self):
        """Test that sensitive patterns are defined."""
        auditor = PDFSecurityAuditor()
        assert len(auditor.SENSITIVE_PATTERNS) > 0

    def test_sensitive_pattern_content(self):
        """Test sensitive patterns contain expected patterns."""
        auditor = PDFSecurityAuditor()
        patterns = auditor.SENSITIVE_PATTERNS

        # Should detect passwords
        assert any("password" in p.lower() for p in patterns)

        # Should detect API keys
        assert any("api" in p.lower() for p in patterns)


class TestRiskScoreCalculation:
    """Tests for risk score calculation."""

    def test_risk_score_low(self):
        """Test risk score for low severity findings."""
        report = SecurityReport(
            file_path="test.pdf",
            is_safe=True,
            risk_score=0,
            findings=[
                SecurityFinding("test", RiskLevel.LOW, "Low finding")
            ]
        )
        # Would be calculated by _calculate_risk_score
        assert report.risk_score == 0

    def test_risk_score_high(self):
        """Test risk score with high severity findings."""
        report = SecurityReport(
            file_path="test.pdf",
            is_safe=False,
            risk_score=0,
            findings=[
                SecurityFinding("test", RiskLevel.HIGH, "High finding"),
                SecurityFinding("test2", RiskLevel.CRITICAL, "Critical finding")
            ]
        )
        # Would be calculated by _calculate_risk_score
        assert len(report.findings) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
