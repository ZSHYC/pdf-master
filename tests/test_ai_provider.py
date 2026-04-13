"""
Tests for AI Provider Interface

Unit tests for the unified AI provider interface using mocks.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestAIProviderUnit:
    """Unit tests for AI provider functions."""

    @pytest.mark.unit
    def test_provider_type_enum(self):
        """Test ProviderType enum values."""
        from ai_provider import ProviderType
        
        assert ProviderType.CLAUDE.value == "claude"
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.GEMINI.value == "gemini"
        assert ProviderType.OLLAMA.value == "ollama"

    @pytest.mark.unit
    def test_message_dataclass(self):
        """Test Message dataclass."""
        from ai_provider import Message
        
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"

    @pytest.mark.unit
    def test_chat_response_dataclass(self):
        """Test ChatResponse dataclass."""
        from ai_provider import ChatResponse
        
        response = ChatResponse(
            content="Test response",
            model="gpt-4",
            provider="openai",
            usage={"input_tokens": 10, "output_tokens": 5}
        )
        
        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.provider == "openai"


class TestAIProviderInit:
    """Tests for AI provider initialization."""

    @pytest.mark.unit
    def test_init_with_invalid_provider(self, clean_env):
        """Test initialization with invalid provider name."""
        from ai_provider import AIProvider
        
        with pytest.raises(ValueError):  # Match any ValueError
            AIProvider(provider="invalid_provider")

    @pytest.mark.unit
    def test_init_with_string_provider(self, clean_env):
        """Test initialization with string provider name."""
        from ai_provider import AIProvider, ProviderType
        
        provider = AIProvider(provider="openai")
        
        assert provider.provider_type == ProviderType.OPENAI


class TestClaudeProvider:
    """Tests for Claude provider."""

    @pytest.mark.unit
    def test_claude_chat(self, mock_anthropic, with_api_key):
        """Test Claude chat functionality."""
        mock_client, mock_instance = mock_anthropic
        
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="claude")
        response = provider.chat([
            {"role": "user", "content": "Hello"}
        ])
        
        assert response.content == "Test response."
        assert response.provider == "claude"


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    @pytest.mark.unit
    def test_openai_chat(self, mock_openai, clean_env):
        """Test OpenAI chat functionality."""
        mock_client, mock_instance = mock_openai
        
        import os
        os.environ["OPENAI_API_KEY"] = "test-key"
        
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="openai")
        response = provider.chat([
            {"role": "user", "content": "Hello"}
        ])
        
        assert response.content == "Test response."
        assert response.provider == "openai"


class TestOllamaProvider:
    """Tests for Ollama provider."""

    @pytest.mark.unit
    def test_ollama_chat(self, mock_ollama, clean_env):
        """Test Ollama chat functionality."""
        mock_client, mock_instance = mock_ollama
        
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="ollama")
        response = provider.chat([
            {"role": "user", "content": "Hello"}
        ])
        
        assert response.content == "Test response."
        assert provider.provider_name == "ollama"


class TestAIProviderMethods:
    """Tests for AI provider methods."""

    @pytest.mark.unit
    def test_summarize(self, mock_anthropic, with_api_key):
        """Test summarize method."""
        mock_client, mock_instance = mock_anthropic
        
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="claude")
        summary = provider.summarize("This is a long text to summarize.")
        
        assert summary == "Test response."

    @pytest.mark.unit
    def test_qa(self, mock_anthropic, with_api_key):
        """Test QA method."""
        mock_client, mock_instance = mock_anthropic
        
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="claude")
        answer = provider.qa(
            "What is this about?",
            "This is a test document about PDF processing."
        )
        
        assert answer == "Test response."


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.unit
    def test_get_ai_provider(self, clean_env):
        """Test get_ai_provider helper function."""
        import os
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        
        from ai_provider import get_ai_provider
        
        provider = get_ai_provider("claude")
        
        assert provider is not None
        assert provider.provider_name == "claude"

    @pytest.mark.unit
    def test_list_providers(self):
        """Test list_providers function."""
        from ai_provider import list_providers
        
        providers = list_providers()
        
        assert len(providers) > 0
        provider_names = [p["name"] for p in providers]
        assert "claude" in provider_names
        assert "openai" in provider_names


class TestProviderAvailability:
    """Tests for provider availability checks."""

    @pytest.mark.unit
    def test_claude_availability_with_key(self, with_api_key):
        """Test Claude availability with API key."""
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="claude")
        
        assert provider.is_available() is True

    @pytest.mark.unit
    def test_claude_availability_without_key(self, clean_env):
        """Test Claude availability without API key."""
        from ai_provider import AIProvider
        
        provider = AIProvider(provider="claude")
        
        assert provider.is_available() is False
