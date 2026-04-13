"""
Tests for AI Provider Manager

Extended tests for the ai_provider module.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pdf" / "scripts"))


class TestProviderTypeEnum:
    """Tests for ProviderType enum."""

    @pytest.mark.unit
    def test_provider_type_values(self):
        from ai_provider import ProviderType
        assert ProviderType.CLAUDE.value == "claude"
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.GEMINI.value == "gemini"
        assert ProviderType.DEEPSEEK.value == "deepseek"
        assert ProviderType.QWEN.value == "qwen"
        assert ProviderType.ZHIPU.value == "zhipu"
        assert ProviderType.MOONSHOT.value == "moonshot"
        assert ProviderType.OLLAMA.value == "ollama"

    @pytest.mark.unit
    def test_provider_type_count(self):
        from ai_provider import ProviderType
        assert len(list(ProviderType)) >= 8


class TestMessageDataclass:
    """Tests for Message dataclass."""

    @pytest.mark.unit
    def test_message_creation(self):
        from ai_provider import Message
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    @pytest.mark.unit
    def test_message_roles(self):
        from ai_provider import Message
        for role in ["system", "user", "assistant"]:
            msg = Message(role=role, content="test")
            assert msg.role == role


class TestChatResponseDataclass:
    """Tests for ChatResponse dataclass."""

    @pytest.mark.unit
    def test_chat_response_creation(self):
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
        assert response.usage["input_tokens"] == 10

    @pytest.mark.unit
    def test_chat_response_optional_fields(self):
        from ai_provider import ChatResponse
        response = ChatResponse(
            content="Test",
            model="model",
            provider="provider"
        )
        assert response.usage is None
        assert response.finish_reason is None


class TestProviderRegistry:
    """Tests for provider registry."""

    @pytest.mark.unit
    def test_providers_dict_exists(self):
        from ai_provider import PROVIDERS
        assert isinstance(PROVIDERS, dict)
        assert len(PROVIDERS) >= 8

    @pytest.mark.unit
    def test_core_providers_registered(self):
        from ai_provider import PROVIDERS, ProviderType
        core_providers = [ProviderType.CLAUDE, ProviderType.OPENAI, ProviderType.OLLAMA]
        for pt in core_providers:
            assert pt in PROVIDERS


class TestAIProviderInit:
    """Tests for AIProvider initialization."""

    @pytest.mark.unit
    def test_init_with_string_provider(self, clean_env):
        from ai_provider import AIProvider, ProviderType
        provider = AIProvider(provider="openai")
        assert provider.provider_type == ProviderType.OPENAI

    @pytest.mark.unit
    def test_init_with_enum_provider(self, clean_env):
        from ai_provider import AIProvider, ProviderType
        provider = AIProvider(provider=ProviderType.CLAUDE)
        assert provider.provider_type == ProviderType.CLAUDE

    @pytest.mark.unit
    def test_init_invalid_provider(self, clean_env):
        from ai_provider import AIProvider
        with pytest.raises(ValueError):
            AIProvider(provider="invalid_provider_name")


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.unit
    def test_get_ai_provider_returns_instance(self, clean_env):
        import os
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        from ai_provider import get_ai_provider, AIProvider
        provider = get_ai_provider("claude")
        assert isinstance(provider, AIProvider)

    @pytest.mark.unit
    def test_list_providers_returns_list(self):
        from ai_provider import list_providers
        providers = list_providers()
        assert isinstance(providers, list)
        assert len(providers) >= 8

    @pytest.mark.unit
    def test_list_providers_has_required_fields(self):
        from ai_provider import list_providers
        providers = list_providers()
        for p in providers:
            assert "name" in p
            assert "default_model" in p


class TestProviderMethods:
    """Tests for AIProvider methods."""

    @pytest.mark.unit
    def test_summarize_method(self, mock_anthropic, with_api_key):
        mock_client, mock_instance = mock_anthropic
        from ai_provider import AIProvider
        provider = AIProvider(provider="claude")
        summary = provider.summarize("This is a long text to summarize.")
        assert summary == "Test response."

    @pytest.mark.unit
    def test_qa_method(self, mock_anthropic, with_api_key):
        mock_client, mock_instance = mock_anthropic
        from ai_provider import AIProvider
        provider = AIProvider(provider="claude")
        answer = provider.qa("What is this?", "This is a test document.")
        assert answer == "Test response."

    @pytest.mark.unit
    def test_translate_method(self, mock_anthropic, with_api_key):
        mock_client, mock_instance = mock_anthropic
        from ai_provider import AIProvider
        provider = AIProvider(provider="claude")
        translated = provider.translate("Hello", "Chinese")
        assert translated == "Test response."

    @pytest.mark.unit
    def test_model_property(self, clean_env):
        import os
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        from ai_provider import AIProvider
        provider = AIProvider(provider="claude")
        assert provider.model is not None

    @pytest.mark.unit
    def test_provider_name_property(self, clean_env):
        import os
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        from ai_provider import AIProvider
        provider = AIProvider(provider="claude")
        assert provider.provider_name == "claude"


class TestOllamaProvider:
    """Tests for Ollama provider."""

    @pytest.mark.unit
    def test_ollama_init(self, clean_env):
        from ai_provider import AIProvider
        provider = AIProvider(provider="ollama")
        assert provider.provider_name == "ollama"

    @pytest.mark.unit
    def test_ollama_default_base_url(self, clean_env):
        from ai_provider import OllamaProvider
        ollama = OllamaProvider()
        assert "localhost" in ollama.base_url or ollama.base_url == "http://localhost:11434"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.unit
    def test_chat_function(self, mock_anthropic, with_api_key):
        from ai_provider import chat
        result = chat([{"role": "user", "content": "Hello"}], provider="claude")
        assert result == "Test response."
