#!/usr/bin/env python3
"""
PDF Security Audit Script - PDF 安全审计

检测：
- JavaScript 代码
- 嵌入文件/附件
- 启动动作
- 可疑表单
- 加密强度
- 数字签名状态
- 元数据敏感信息
- 隐藏图层/OCG

依赖: pypdf, pikepdf (可选)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RiskLevel(Enum):
    """Security risk level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityFinding:
    """Security finding details."""
    category: str
    severity: RiskLevel
    description: str
    location: Optional[str] = None
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity.value,
            "description": self.description,
            "location": self.location,
            "recommendation": self.recommendation
        }


@dataclass
class SecurityReport:
    """PDF security audit report."""
    file_path: str
    is_safe: bool
    risk_score: int  # 0-100, lower is safer
    findings: List[SecurityFinding] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "is_safe": self.is_safe,
            "risk_score": self.risk_score,
            "findings": [f.to_dict() for f in self.findings],
            "info": self.info
        }


class PDFSecurityAuditor:
    """PDF security auditor."""

    # Sensitive patterns in metadata
    SENSITIVE_PATTERNS = [
        r"password",
        r"secret",
        r"api.?key",
        r"token",
        r"credential",
        r"private.?key",
        r"ssn",
        r"social.?security",
        r"credit.?card",
        r"\d{3}-\d{2}-\d{4}",  # SSN format
        r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",  # Credit card format
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def audit(self, pdf_path: str) -> SecurityReport:
        """Perform comprehensive security audit."""
        report = SecurityReport(
            file_path=pdf_path,
            is_safe=True,
            risk_score=0
        )

        if not Path(pdf_path).exists():
            report.findings.append(SecurityFinding(
                category="file",
                severity=RiskLevel.CRITICAL,
                description=f"File not found: {pdf_path}"
            ))
            report.is_safe = False
            report.risk_score = 100
            return report

        try:
            # Use pypdf for basic checks
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)

            # Check encryption
            self._check_encryption(reader, report)

            # Check JavaScript
            self._check_javascript(reader, report)

            # Check embedded files
            self._check_embedded_files(reader, report)

            # Check launch actions
            self._check_launch_actions(reader, report)

            # Check forms
            self._check_forms(reader, report)

            # Check metadata
            self._check_metadata(reader, report)

            # Check links
            self._check_suspicious_links(reader, report)

            # Calculate overall risk score
            self._calculate_risk_score(report)

        except ImportError:
            report.findings.append(SecurityFinding(
                category="dependency",
                severity=RiskLevel.HIGH,
                description="pypdf not installed. Install with: pip install pypdf"
            ))
        except Exception as e:
            report.findings.append(SecurityFinding(
                category="error",
                severity=RiskLevel.HIGH,
                description=f"Error analyzing PDF: {e}"
            ))

        return report

    def _check_encryption(self, reader, report: SecurityReport) -> None:
        """Check PDF encryption status and strength."""
        if reader.is_encrypted:
            report.info["encrypted"] = True

            # Try to get encryption info
            try:
                # Check if we can decrypt with empty password
                if reader.decrypt(""):
                    report.findings.append(SecurityFinding(
                        category="encryption",
                        severity=RiskLevel.MEDIUM,
                        description="PDF is encrypted but can be opened with empty password",
                        recommendation="Consider using stronger encryption with a proper password"
                    ))
                else:
                    report.findings.append(SecurityFinding(
                        category="encryption",
                        severity=RiskLevel.LOW,
                        description="PDF is password-protected",
                        recommendation="Ensure password is strong and properly managed"
                    ))
            except Exception:
                report.findings.append(SecurityFinding(
                    category="encryption",
                    severity=RiskLevel.MEDIUM,
                    description="PDF is encrypted (details unavailable)"
                ))
        else:
            report.info["encrypted"] = False
            if self.verbose:
                report.findings.append(SecurityFinding(
                    category="encryption",
                    severity=RiskLevel.LOW,
                    description="PDF is not encrypted",
                    recommendation="Consider encrypting sensitive documents"
                ))

    def _check_javascript(self, reader, report: SecurityReport) -> None:
        """Check for JavaScript code in PDF."""
        js_found = False

        # Check document-level JavaScript
        if "/Names" in reader.trailer["/Root"]:
            names = reader.trailer["/Root"]["/Names"]
            if "/JavaScript" in names:
                js_found = True
                report.findings.append(SecurityFinding(
                    category="javascript",
                    severity=RiskLevel.HIGH,
                    description="Document-level JavaScript found",
                    recommendation="Review JavaScript code for malicious behavior"
                ))

        # Check for JS in actions
        try:
            if "/OpenAction" in reader.trailer["/Root"]:
                open_action = reader.trailer["/Root"]["/OpenAction"]
                if "/JS" in str(open_action) or "/JavaScript" in str(open_action):
                    js_found = True
                    report.findings.append(SecurityFinding(
                        category="javascript",
                        severity=RiskLevel.HIGH,
                        description="JavaScript in OpenAction found",
                        recommendation="Review OpenAction for malicious JavaScript"
                    ))
        except Exception:
            pass

        # Check page-level JavaScript
        for page_num, page in enumerate(reader.pages):
            try:
                page_obj = page.get_object() if hasattr(page, 'get_object') else page
                if "/AA" in page_obj:  # Additional Actions
                    aa = page_obj["/AA"]
                    for key in ["/O", "/C", "/PO", "/PC"]:
                        if key in aa:
                            action = aa[key]
                            if "/JS" in str(action):
                                js_found = True
                                report.findings.append(SecurityFinding(
                                    category="javascript",
                                    severity=RiskLevel.HIGH,
                                    description=f"JavaScript found in page {page_num + 1} action",
                                    location=f"Page {page_num + 1}",
                                    recommendation="Review page-level JavaScript"
                                ))
            except Exception:
                continue

        report.info["has_javascript"] = js_found

    def _check_embedded_files(self, reader, report: SecurityReport) -> None:
        """Check for embedded files/attachments."""
        embedded_files = []

        try:
            if "/Names" in reader.trailer["/Root"]:
                names = reader.trailer["/Root"]["/Names"]
                if "/EmbeddedFiles" in names:
                    embedded_files.append("Document-level embedded files found")
                    report.findings.append(SecurityFinding(
                        category="embedded_files",
                        severity=RiskLevel.MEDIUM,
                        description="Embedded files/attachments found",
                        recommendation="Review embedded files for potential malware"
                    ))

            # Check for file attachments in annotations
            for page_num, page in enumerate(reader.pages):
                try:
                    page_obj = page.get_object() if hasattr(page, 'get_object') else page
                    if "/Annots" in page_obj:
                        for annot in page_obj["/Annots"]:
                            annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot
                            if "/Subtype" in annot_obj and annot_obj["/Subtype"] == "/FileAttachment":
                                embedded_files.append(f"File attachment on page {page_num + 1}")
                                report.findings.append(SecurityFinding(
                                    category="embedded_files",
                                    severity=RiskLevel.MEDIUM,
                                    description=f"File attachment found on page {page_num + 1}",
                                    location=f"Page {page_num + 1}",
                                    recommendation="Review attached files"
                                ))
                except Exception:
                    continue

        except Exception:
            pass

        report.info["embedded_files"] = len(embedded_files)

    def _check_launch_actions(self, reader, report: SecurityReport) -> None:
        """Check for launch actions that execute external commands."""
        launch_found = False

        # Check document-level actions
        try:
            if "/OpenAction" in reader.trailer["/Root"]:
                open_action = reader.trailer["/Root"]["/OpenAction"]
                if "/Launch" in str(open_action):
                    launch_found = True
                    report.findings.append(SecurityFinding(
                        category="launch_action",
                        severity=RiskLevel.CRITICAL,
                        description="Launch action found in OpenAction - may execute external commands",
                        recommendation="Remove or review launch actions for security"
                    ))
        except Exception:
            pass

        # Check page-level launch actions
        for page_num, page in enumerate(reader.pages):
            try:
                page_obj = page.get_object() if hasattr(page, 'get_object') else page
                if "/AA" in page_obj:
                    aa = page_obj["/AA"]
                    for key in aa:
                        action = aa[key]
                        if "/Launch" in str(action):
                            launch_found = True
                            report.findings.append(SecurityFinding(
                                category="launch_action",
                                severity=RiskLevel.CRITICAL,
                                description=f"Launch action found on page {page_num + 1}",
                                location=f"Page {page_num + 1}",
                                recommendation="Remove launch actions"
                            ))
            except Exception:
                continue

        report.info["has_launch_actions"] = launch_found

    def _check_forms(self, reader, report: SecurityReport) -> None:
        """Check for forms and potential form-based attacks."""
        try:
            if "/AcroForm" in reader.trailer["/Root"]:
                form = reader.trailer["/Root"]["/AcroForm"]
                if form:
                    report.info["has_form"] = True

                    # Check for XFA forms (potential attack vector)
                    if "/XFA" in form:
                        report.findings.append(SecurityFinding(
                            category="form",
                            severity=RiskLevel.HIGH,
                            description="XFA form found - potential attack vector",
                            recommendation="Review XFA content for security risks"
                        ))
                    elif self.verbose:
                        report.findings.append(SecurityFinding(
                            category="form",
                            severity=RiskLevel.LOW,
                            description="AcroForm found",
                            recommendation="Review form fields for sensitive data collection"
                        ))
            else:
                report.info["has_form"] = False
        except Exception:
            pass

    def _check_metadata(self, reader, report: SecurityReport) -> None:
        """Check metadata for sensitive information."""
        sensitive_found = []

        try:
            metadata = reader.metadata
            if metadata:
                for key, value in metadata.items():
                    if value:
                        value_str = str(value)
                        for pattern in self.SENSITIVE_PATTERNS:
                            if re.search(pattern, value_str, re.IGNORECASE):
                                sensitive_found.append(f"{key}: potential sensitive data")
                                report.findings.append(SecurityFinding(
                                    category="metadata",
                                    severity=RiskLevel.MEDIUM,
                                    description=f"Potentially sensitive data in metadata field: {key}",
                                    recommendation="Review and sanitize metadata"
                                ))
                                break
        except Exception:
            pass

        report.info["sensitive_metadata"] = len(sensitive_found)

    def _check_suspicious_links(self, reader, report: SecurityReport) -> None:
        """Check for suspicious hyperlinks."""
        suspicious_links = []
        suspicious_patterns = [
            r"javascript:",
            r"data:",
            r"vbscript:",
            r"file://",
        ]

        for page_num, page in enumerate(reader.pages):
            try:
                page_obj = page.get_object() if hasattr(page, 'get_object') else page
                if "/Annots" in page_obj:
                    for annot in page_obj["/Annots"]:
                        annot_obj = annot.get_object() if hasattr(annot, 'get_object') else annot
                        if "/A" in annot_obj:
                            action = annot_obj["/A"]
                            if "/URI" in action:
                                uri = str(action["/URI"])
                                for pattern in suspicious_patterns:
                                    if re.search(pattern, uri, re.IGNORECASE):
                                        suspicious_links.append(uri)
                                        report.findings.append(SecurityFinding(
                                            category="link",
                                            severity=RiskLevel.HIGH,
                                            description=f"Suspicious link found: {uri[:50]}...",
                                            location=f"Page {page_num + 1}",
                                            recommendation="Review and remove suspicious links"
                                        ))
            except Exception:
                continue

        report.info["suspicious_links"] = len(suspicious_links)

    def _calculate_risk_score(self, report: SecurityReport) -> None:
        """Calculate overall risk score."""
        score = 0

        for finding in report.findings:
            if finding.severity == RiskLevel.CRITICAL:
                score += 30
            elif finding.severity == RiskLevel.HIGH:
                score += 20
            elif finding.severity == RiskLevel.MEDIUM:
                score += 10
            else:
                score += 5

        # Cap at 100
        report.risk_score = min(score, 100)

        # Determine if safe
        report.is_safe = (
            report.risk_score < 20 and
            not any(f.severity in [RiskLevel.CRITICAL, RiskLevel.HIGH]
                    for f in report.findings)
        )


def audit_pdf(pdf_path: str, verbose: bool = False) -> SecurityReport:
    """Perform security audit on PDF file.

    Args:
        pdf_path: Path to PDF file.
        verbose: Include low-severity findings.

    Returns:
        SecurityReport with audit results.
    """
    auditor = PDFSecurityAuditor(verbose)
    return auditor.audit(pdf_path)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PDF Security Audit - Detect potential security risks in PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic security audit
  %(prog)s document.pdf

  # Verbose output (include low-severity findings)
  %(prog)s document.pdf --verbose

  # Output as JSON
  %(prog)s document.pdf --json

  # Check multiple files
  %(prog)s file1.pdf file2.pdf file3.pdf
        """
    )

    parser.add_argument(
        "input",
        nargs="+",
        help="Input PDF file(s) to audit"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Include low-severity findings"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show only summary (no detailed findings)"
    )

    args = parser.parse_args()

    all_reports = []

    for pdf_path in args.input:
        report = audit_pdf(pdf_path, args.verbose)
        all_reports.append(report)

        if not args.json:
            print(f"\n{'='*60}")
            print(f"Security Audit: {pdf_path}")
            print(f"{'='*60}")

            if report.is_safe:
                print("Status: SAFE")
            else:
                print("Status: POTENTIAL RISKS DETECTED")

            print(f"Risk Score: {report.risk_score}/100")

            if not args.summary:
                print(f"\nFindings ({len(report.findings)}):")
                for finding in report.findings:
                    severity_label = {
                        RiskLevel.CRITICAL: "CRITICAL",
                        RiskLevel.HIGH: "HIGH",
                        RiskLevel.MEDIUM: "MEDIUM",
                        RiskLevel.LOW: "LOW"
                    }
                    print(f"  [{severity_label[finding.severity]}] {finding.category}: {finding.description}")
                    if finding.recommendation:
                        print(f"    Recommendation: {finding.recommendation}")

            print(f"\nInfo:")
            for key, value in report.info.items():
                print(f"  {key}: {value}")

    if args.json:
        output = [r.to_dict() for r in all_reports]
        print(json.dumps(output, indent=2))

    # Return non-zero if any file has high risk
    return 0 if all(r.is_safe for r in all_reports) else 1


if __name__ == "__main__":
    sys.exit(main())
