
"""
Tests for PDF Encrypt and Decrypt Functionality
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestEncryptPDFUnit:
    """Unit tests for PDF encrypt functions."""

    @pytest.mark.unit
    def test_encrypt_pdf_function_exists(self):
        pytest.importorskip("pypdf")
        from encrypt_pdf import encrypt_pdf
        assert callable(encrypt_pdf)

    @pytest.mark.unit
    def test_encrypt_constants(self):
        pytest.importorskip("pypdf")
        import encrypt_pdf
        assert hasattr(encrypt_pdf, "encrypt_pdf")


class TestDecryptPDFUnit:
    """Unit tests for PDF decrypt functions."""

    @pytest.mark.unit
    def test_decrypt_pdf_function_exists(self):
        pytest.importorskip("pypdf")
        from decrypt_pdf import decrypt_pdf
        assert callable(decrypt_pdf)

    @pytest.mark.unit
    def test_is_encrypted_function_exists(self):
        pytest.importorskip("pypdf")
        from decrypt_pdf import is_encrypted
        assert callable(is_encrypted)


class TestEncryptDecryptIntegration:
    """Integration tests for PDF encrypt and decrypt."""

    @pytest.mark.integration
    def test_is_encrypted_false(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from decrypt_pdf import is_encrypted
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Content")
        c.save()
        
        result = is_encrypted(str(pdf_path))
        assert result is False

    @pytest.mark.integration
    def test_decrypt_unencrypted_pdf(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from decrypt_pdf import decrypt_pdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Content")
        c.save()
        
        output = str(temp_dir / "output.pdf")
        result = decrypt_pdf(str(pdf_path), output)
        assert result is True


class TestEncryptDecryptEdgeCases:
    """Edge case tests for PDF encrypt and decrypt."""

    @pytest.mark.integration
    def test_encrypt_file_not_found(self, temp_dir):
        pytest.importorskip("pypdf")
        from encrypt_pdf import encrypt_pdf
        output = str(temp_dir / "encrypted.pdf")
        result = encrypt_pdf("nonexistent.pdf", output, user_password="pass")
        assert result is False

    @pytest.mark.integration
    def test_decrypt_file_not_found(self, temp_dir):
        pytest.importorskip("pypdf")
        from decrypt_pdf import decrypt_pdf
        output = str(temp_dir / "decrypted.pdf")
        result = decrypt_pdf("nonexistent.pdf", output, password="pass")
        assert result is False

    @pytest.mark.integration
    def test_decrypt_missing_password(self, temp_dir):
        pytest.importorskip("pypdf")
        pytest.importorskip("reportlab")
        from encrypt_pdf import encrypt_pdf
        from decrypt_pdf import decrypt_pdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Content")
        c.save()
        
        encrypted = str(temp_dir / "encrypted.pdf")
        encrypt_pdf(str(pdf_path), encrypted, user_password="pass")
        
        decrypted = str(temp_dir / "decrypted.pdf")
        result = decrypt_pdf(encrypted, decrypted)
        assert result is False
