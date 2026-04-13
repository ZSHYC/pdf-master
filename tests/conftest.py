"""
Pytest Configuration and Shared Fixtures
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "pdf" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")


@pytest.fixture
def temp_dir():
    dir_path = Path(tempfile.mkdtemp())
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf_path(fixtures_dir):
    pdf_path = fixtures_dir / "sample.pdf"
    if not pdf_path.exists():
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, "Sample PDF Document")
            c.drawString(100, 720, "This is a test PDF file.")
            c.drawString(100, 640, "Name        Age    City")
            c.drawString(100, 620, "John Doe    30     New York")
            c.drawString(100, 600, "Jane Smith  25     Los Angeles")
            c.save()
        except ImportError:
            pytest.skip("reportlab not installed")
    return pdf_path


@pytest.fixture
def empty_pdf_path(temp_dir):
    pdf_path = temp_dir / "empty.pdf"
    try:
        from pypdf import PdfWriter
        writer = PdfWriter()
        with open(pdf_path, "wb") as f:
            writer.write(f)
    except ImportError:
        pytest.skip("pypdf not installed")
    return pdf_path


@pytest.fixture
def multi_page_pdf_path(temp_dir):
    pdf_path = temp_dir / "multi_page.pdf"
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        for page_num in range(1, 4):
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"Page {page_num}")
            c.drawString(100, 720, f"This is page {page_num}.")
            c.showPage()
        c.save()
    except ImportError:
        pytest.skip("reportlab not installed")
    return pdf_path


@pytest.fixture
def mock_anthropic():
    with patch("anthropic.Anthropic") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response.")]
        mock_response.model = "claude-3-5-sonnet"
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)
        mock_response.stop_reason = "end_turn"
        mock_instance.messages.create.return_value = mock_response
        yield mock_client, mock_instance


@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response."
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4o"
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20)
        mock_instance.chat.completions.create.return_value = mock_response
        yield mock_client, mock_instance


@pytest.fixture
def mock_ollama():
    with patch("ollama.Client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.return_value = {
            "message": {"content": "Test response."},
            "model": "llama3.2"
        }
        mock_instance.list.return_value = []
        yield mock_client, mock_instance


@pytest.fixture
def sample_text_data():
    return {
        "source": "test.pdf",
        "method": "pdfplumber",
        "total_pages": 2,
        "pages": [
            {"page_number": 1, "text": "Page 1 content."},
            {"page_number": 2, "text": "Page 2 content."}
        ]
    }


@pytest.fixture
def sample_table_data():
    return {
        "source": "test.pdf",
        "total_tables": 1,
        "pages": [{
            "page_number": 1,
            "tables": [{
                "table_number": 1,
                "rows": 3,
                "columns": 3,
                "data": [["Name", "Age", "City"], ["John", "30", "NYC"], ["Jane", "25", "LA"]]
            }]
        }]
    }


@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]


@pytest.fixture
def clean_env():
    env_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY",
                "DEEPSEEK_API_KEY", "QWEN_API_KEY", "ZHIPU_API_KEY",
                "MOONSHOT_API_KEY", "OLLAMA_BASE_URL", "PDF_MASTER_AI_PROVIDER"]
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    yield
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def with_api_key(clean_env):
    os.environ["ANTHROPIC_API_KEY"] = "test-api-key-12345"
    yield
