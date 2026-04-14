#!/usr/bin/env python3
"""
Tests for PDF Digital Signature functionality
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add skills path to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills' / 'pdf' / 'scripts'))


class TestSignatureInfo:
    """Tests for SignatureInfo class"""

    def test_signature_info_init(self):
        """Test SignatureInfo initialization"""
        from sign_pdf import SignatureInfo

        info = SignatureInfo()

        assert info.signer_name == ""
        assert info.signer_email == ""
        assert info.signing_time is None
        assert info.issuer == ""
        assert info.serial_number == ""
        assert info.algorithm == ""
        assert info.is_valid is False
        assert info.is_trusted is False
        assert info.error_message == ""

    def test_signature_info_repr(self):
        """Test SignatureInfo representation"""
        from sign_pdf import SignatureInfo
        from datetime import datetime

        info = SignatureInfo()
        info.signer_name = "John Doe"
        info.signing_time = datetime(2024, 1, 1)
        info.is_valid = True

        repr_str = repr(info)
        assert "John Doe" in repr_str
        assert "valid=True" in repr_str


class TestCertificateLoading:
    """Tests for certificate loading functions"""

    def test_load_certificate_not_found(self):
        """Test loading non-existent certificate"""
        from sign_pdf import load_certificate

        with pytest.raises(FileNotFoundError):
            load_certificate("/nonexistent/cert.pem")

    def test_load_private_key_not_found(self):
        """Test loading non-existent private key"""
        from sign_pdf import load_private_key

        with pytest.raises(FileNotFoundError):
            load_private_key("/nonexistent/key.pem")

    def test_load_pkcs12_not_found(self):
        """Test loading non-existent PKCS#12 file"""
        from sign_pdf import load_pkcs12

        with pytest.raises(FileNotFoundError):
            load_pkcs12("/nonexistent/cert.p12", "password")


class TestCheckPdfSigned:
    """Tests for check_pdf_signed function"""

    def test_check_unsigned_pdf(self, tmp_path):
        """Test checking an unsigned PDF"""
        # Create a simple unsigned PDF
        from pypdf import PdfWriter

        pdf_path = tmp_path / "unsigned.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        from sign_pdf import check_pdf_signed

        result = check_pdf_signed(str(pdf_path))
        assert result is False

    def test_check_pdf_nonexistent(self):
        """Test checking a non-existent PDF"""
        from sign_pdf import check_pdf_signed

        result = check_pdf_signed("/nonexistent/file.pdf")
        assert result is False


class TestGenerateSelfSignedCertificate:
    """Tests for self-signed certificate generation"""

    def test_generate_certificate(self, tmp_path):
        """Test generating a self-signed certificate"""
        from sign_pdf import generate_self_signed_certificate

        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"

        result = generate_self_signed_certificate(
            common_name="Test User",
            output_cert=str(cert_path),
            output_key=str(key_path),
            days_valid=365,
            verbose=False
        )

        assert result is True
        assert cert_path.exists()
        assert key_path.exists()

        # Verify certificate content
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        assert b"BEGIN CERTIFICATE" in cert_data

        # Verify key content
        with open(key_path, 'rb') as f:
            key_data = f.read()
        assert b"BEGIN PRIVATE KEY" in key_data

    def test_generate_certificate_with_password(self, tmp_path):
        """Test generating a certificate with password-protected key"""
        from sign_pdf import generate_self_signed_certificate

        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"

        result = generate_self_signed_certificate(
            common_name="Test User",
            output_cert=str(cert_path),
            output_key=str(key_path),
            password="testpassword",
            verbose=False
        )

        assert result is True
        assert cert_path.exists()
        assert key_path.exists()

        # Verify key is encrypted
        with open(key_path, 'rb') as f:
            key_data = f.read()
        assert b"ENCRYPTED" in key_data

    def test_generate_certificate_with_options(self, tmp_path):
        """Test generating a certificate with all options"""
        from sign_pdf import generate_self_signed_certificate

        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"

        result = generate_self_signed_certificate(
            common_name="Test Organization",
            output_cert=str(cert_path),
            output_key=str(key_path),
            key_size=4096,
            days_valid=730,
            country="US",
            state="California",
            locality="San Francisco",
            organization="Test Corp",
            email="test@example.com",
            verbose=True
        )

        assert result is True


class TestSignPdf:
    """Tests for PDF signing functions"""

    @pytest.fixture
    def test_pdf(self, tmp_path):
        """Create a test PDF file"""
        from pypdf import PdfWriter

        pdf_path = tmp_path / "test.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        return str(pdf_path)

    @pytest.fixture
    def test_cert_and_key(self, tmp_path):
        """Generate test certificate and key"""
        from sign_pdf import generate_self_signed_certificate

        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"

        generate_self_signed_certificate(
            common_name="Test Signer",
            output_cert=str(cert_path),
            output_key=str(key_path),
            verbose=False
        )

        return str(cert_path), str(key_path)

    def test_sign_pdf_basic(self, test_pdf, test_cert_and_key, tmp_path):
        """Test basic PDF signing"""
        cert_path, key_path = test_cert_and_key
        output_path = tmp_path / "signed.pdf"

        from sign_pdf import sign_pdf

        result = sign_pdf(
            input_file=test_pdf,
            output_file=str(output_path),
            cert_path=cert_path,
            key_path=key_path,
            reason="Test signature",
            verbose=True
        )

        assert result is True
        assert output_path.exists()

    def test_sign_pdf_with_location(self, test_pdf, test_cert_and_key, tmp_path):
        """Test PDF signing with location"""
        cert_path, key_path = test_cert_and_key
        output_path = tmp_path / "signed.pdf"

        from sign_pdf import sign_pdf

        result = sign_pdf(
            input_file=test_pdf,
            output_file=str(output_path),
            cert_path=cert_path,
            key_path=key_path,
            reason="Test signature",
            location="Beijing, China",
            contact_info="test@example.com",
            verbose=False
        )

        assert result is True

    def test_sign_pdf_with_different_algorithms(self, test_pdf, test_cert_and_key, tmp_path):
        """Test PDF signing with different digest algorithms"""
        cert_path, key_path = test_cert_and_key

        algorithms = ['sha1', 'sha256', 'sha384', 'sha512']

        for algo in algorithms:
            output_path = tmp_path / f"signed_{algo}.pdf"

            from sign_pdf import sign_pdf

            result = sign_pdf(
                input_file=test_pdf,
                output_file=str(output_path),
                cert_path=cert_path,
                key_path=key_path,
                digest_algorithm=algo,
                verbose=False
            )

            assert result is True, f"Failed with algorithm {algo}"

    def test_sign_pdf_nonexistent_input(self, tmp_path, test_cert_and_key):
        """Test signing with non-existent input file"""
        cert_path, key_path = test_cert_and_key
        output_path = tmp_path / "signed.pdf"

        from sign_pdf import sign_pdf

        result = sign_pdf(
            input_file="/nonexistent/input.pdf",
            output_file=str(output_path),
            cert_path=cert_path,
            key_path=key_path,
            verbose=False
        )

        assert result is False

    def test_sign_pdf_nonexistent_cert(self, test_pdf, tmp_path):
        """Test signing with non-existent certificate"""
        output_path = tmp_path / "signed.pdf"

        from sign_pdf import sign_pdf

        result = sign_pdf(
            input_file=test_pdf,
            output_file=str(output_path),
            cert_path="/nonexistent/cert.pem",
            key_path="/nonexistent/key.pem",
            verbose=False
        )

        assert result is False


class TestExtractSignatureInfo:
    """Tests for signature information extraction"""

    def test_extract_from_unsigned_pdf(self, tmp_path):
        """Test extracting from unsigned PDF"""
        from pypdf import PdfWriter

        pdf_path = tmp_path / "unsigned.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        from sign_pdf import extract_signature_info

        result = extract_signature_info(str(pdf_path), verbose=True)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_json_format(self, tmp_path):
        """Test extracting with JSON format"""
        from pypdf import PdfWriter

        pdf_path = tmp_path / "unsigned.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        from sign_pdf import extract_signature_info

        result = extract_signature_info(
            str(pdf_path),
            output_format='json',
            verbose=False
        )

        assert isinstance(result, list)

    def test_extract_nonexistent_file(self):
        """Test extracting from non-existent file"""
        from sign_pdf import extract_signature_info

        result = extract_signature_info("/nonexistent/file.pdf")
        assert result == []


class TestVerifyPdfSignature:
    """Tests for PDF signature verification"""

    def test_verify_unsigned_pdf(self, tmp_path):
        """Test verifying an unsigned PDF"""
        from pypdf import PdfWriter

        pdf_path = tmp_path / "unsigned.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        from sign_pdf import verify_pdf_signature

        result = verify_pdf_signature(str(pdf_path))

        assert isinstance(result, list)

    def test_verify_nonexistent_file(self):
        """Test verifying a non-existent file"""
        from sign_pdf import verify_pdf_signature

        result = verify_pdf_signature("/nonexistent/file.pdf")

        assert isinstance(result, list)


class TestSignPdfPkcs12:
    """Tests for PKCS#12 signing"""

    def test_sign_with_nonexistent_p12(self, tmp_path):
        """Test signing with non-existent PKCS#12 file"""
        from pypdf import PdfWriter

        pdf_path = tmp_path / "test.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        output_path = tmp_path / "signed.pdf"

        from sign_pdf import sign_pdf_pkcs12

        result = sign_pdf_pkcs12(
            input_file=str(pdf_path),
            output_file=str(output_path),
            p12_path="/nonexistent/cert.p12",
            password="test"
        )

        assert result is False


class TestIntegration:
    """Integration tests for complete signing workflow"""

    @pytest.fixture
    def test_environment(self, tmp_path):
        """Set up a complete test environment"""
        from pypdf import PdfWriter
        from sign_pdf import generate_self_signed_certificate

        # Create test PDF
        pdf_path = tmp_path / "document.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

        # Generate test certificate
        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"
        generate_self_signed_certificate(
            common_name="Integration Test",
            output_cert=str(cert_path),
            output_key=str(key_path),
            verbose=False
        )

        return {
            'pdf': str(pdf_path),
            'cert': str(cert_path),
            'key': str(key_path),
            'output': str(tmp_path / "signed.pdf")
        }

    def test_complete_signing_workflow(self, test_environment):
        """Test complete signing and verification workflow"""
        from sign_pdf import sign_pdf, check_pdf_signed, extract_signature_info

        env = test_environment

        # Step 1: Check unsigned
        assert check_pdf_signed(env['pdf']) is False

        # Step 2: Sign the document
        result = sign_pdf(
            input_file=env['pdf'],
            output_file=env['output'],
            cert_path=env['cert'],
            key_path=env['key'],
            reason="Integration test signature",
            location="Test Lab",
            verbose=True
        )
        assert result is True
        assert Path(env['output']).exists()

        # Step 3: Check signed
        assert check_pdf_signed(env['output']) is True

        # Step 4: Extract signature info
        signatures = extract_signature_info(env['output'])
        # Note: The signature extraction depends on how the PDF was signed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
