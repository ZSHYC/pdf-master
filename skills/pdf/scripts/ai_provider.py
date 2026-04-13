"""
AI Provider Unified Interface

支持多个 AI 提供商的统一接口：
- Claude (anthropic SDK)
- OpenAI (openai SDK)
- Gemini (google-generativeai SDK)
- DeepSeek (OpenAI 兼容)
- 通义千问 Qwen (OpenAI 兼容)
- 智谱 GLM (zhipuai SDK)
- Moonshot (OpenAI 兼容)
- Ollama (本地)
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    """AI 提供商类型"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    OLLAMA = "ollama"


@dataclass
class Message:
    """聊天消息"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class BaseAIProvider(ABC):
    """AI 提供商基类"""

    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        """统一聊天接口"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

    def _normalize_messages(self, messages: List[Union[Message, Dict[str, str]]]) -> List[Dict[str, str]]:
        """标准化消息格式"""
        normalized = []
        for msg in messages:
            if isinstance(msg, Message):
                normalized.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                normalized.append(msg)
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")
        return normalized


class ClaudeProvider(BaseAIProvider):
    """Claude (Anthropic) 提供商"""

    PROVIDER_NAME = "claude"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    ENV_KEY = "ANTHROPIC_API_KEY"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, **kwargs)
        self._client = None

    def _get_client(self):
        """获取 Anthropic 客户端"""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("请安装 anthropic: pip install anthropic")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)

        # 分离 system 消息
        system = None
        chat_messages = []
        for msg in normalized:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        params = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        if system:
            params["system"] = system
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        response = client.messages.create(**params)

        return ChatResponse(
            content=response.content[0].text,
            model=response.model,
            provider=self.PROVIDER_NAME,
            usage={"input_tokens": response.usage.input_tokens,
                   "output_tokens": response.usage.output_tokens},
            finish_reason=response.stop_reason
        )


class OpenAIProvider(BaseAIProvider):
    """OpenAI 提供商"""

    PROVIDER_NAME = "openai"
    DEFAULT_MODEL = "gpt-4o"
    ENV_KEY = "OPENAI_API_KEY"

    def __init__(self, model: str = None, api_key: Optional[str] = None,
                 base_url: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, **kwargs)
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)

        params = {
            "model": self.model,
            "messages": normalized,
        }
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        response = client.chat.completions.create(**params)

        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.PROVIDER_NAME,
            usage={"input_tokens": response.usage.prompt_tokens,
                   "output_tokens": response.usage.completion_tokens},
            finish_reason=response.choices[0].finish_reason
        )


class GeminiProvider(BaseAIProvider):
    """Google Gemini 提供商"""

    PROVIDER_NAME = "gemini"
    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    ENV_KEY = "GOOGLE_API_KEY"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, **kwargs)
        self._client = None

    def _get_client(self):
        """获取 Gemini 客户端"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("请安装 google-generativeai: pip install google-generativeai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)

        # 转换为 Gemini 格式
        gemini_messages = []
        for msg in normalized:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        generation_config = {}
        if "max_tokens" in kwargs:
            generation_config["max_output_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            generation_config["temperature"] = kwargs["temperature"]

        response = client.generate_content(
            gemini_messages,
            generation_config=generation_config if generation_config else None
        )

        return ChatResponse(
            content=response.text,
            model=self.model,
            provider=self.PROVIDER_NAME,
            usage=None,  # Gemini 不直接提供 token 用量
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None
        )


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek 提供商 (OpenAI 兼容)"""

    PROVIDER_NAME = "deepseek"
    DEFAULT_MODEL = "deepseek-chat"
    ENV_KEY = "DEEPSEEK_API_KEY"
    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, base_url=self.BASE_URL, **kwargs)


class QwenProvider(OpenAIProvider):
    """通义千问 Qwen 提供商 (OpenAI 兼容)"""

    PROVIDER_NAME = "qwen"
    DEFAULT_MODEL = "qwen-turbo"
    ENV_KEY = "QWEN_API_KEY"
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, base_url=self.BASE_URL, **kwargs)


class ZhipuProvider(BaseAIProvider):
    """智谱 GLM 提供商"""

    PROVIDER_NAME = "zhipu"
    DEFAULT_MODEL = "glm-4-flash"
    ENV_KEY = "ZHIPU_API_KEY"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, **kwargs)
        self._client = None

    def _get_client(self):
        """获取智谱客户端"""
        if self._client is None:
            try:
                from zhipuai import ZhipuAI
                self._client = ZhipuAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("请安装 zhipuai: pip install zhipuai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)

        params = {
            "model": self.model,
            "messages": normalized,
        }
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        response = client.chat.completions.create(**params)

        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.PROVIDER_NAME,
            usage={"input_tokens": response.usage.prompt_tokens,
                   "output_tokens": response.usage.completion_tokens} if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )


class MoonshotProvider(OpenAIProvider):
    """Moonshot 提供商 (OpenAI 兼容)"""

    PROVIDER_NAME = "moonshot"
    DEFAULT_MODEL = "moonshot-v1-8k"
    ENV_KEY = "MOONSHOT_API_KEY"
    BASE_URL = "https://api.moonshot.cn/v1"

    def __init__(self, model: str = None, api_key: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, base_url=self.BASE_URL, **kwargs)


class OllamaProvider(BaseAIProvider):
    """Ollama 本地提供商"""

    PROVIDER_NAME = "ollama"
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, model: str = None, base_url: str = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        super().__init__(model, None, **kwargs)
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", self.DEFAULT_BASE_URL)
        self._client = None

    def _get_client(self):
        """获取 Ollama 客户端"""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
            except ImportError:
                raise ImportError("请安装 ollama: pip install ollama")
        return self._client

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            client.list()
            return True
        except Exception:
            return False

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)

        params = {
            "model": self.model,
            "messages": normalized,
        }
        if "stream" in kwargs:
            params["stream"] = kwargs["stream"]
        if "format" in kwargs:
            params["format"] = kwargs["format"]

        response = client.chat(**params)

        return ChatResponse(
            content=response["message"]["content"],
            model=response.get("model", self.model),
            provider=self.PROVIDER_NAME,
            usage=None,
            finish_reason="stop"
        )


# 提供商注册表
PROVIDERS = {
    ProviderType.CLAUDE: ClaudeProvider,
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.GEMINI: GeminiProvider,
    ProviderType.DEEPSEEK: DeepSeekProvider,
    ProviderType.QWEN: QwenProvider,
    ProviderType.ZHIPU: ZhipuProvider,
    ProviderType.MOONSHOT: MoonshotProvider,
    ProviderType.OLLAMA: OllamaProvider,
}


class AIProvider:
    """
    统一的 AI 提供商接口

    使用示例:
        # 使用默认提供商
        ai = AIProvider()
        response = ai.chat([{"role": "user", "content": "你好"}])

        # 指定提供商
        ai = AIProvider(provider="claude", model="claude-3-5-sonnet-20241022")
        response = ai.chat([{"role": "user", "content": "你好"}])

        # 生成摘要
        summary = ai.summarize("长文本内容...", language="zh")

        # 文档问答
        answer = ai.qa("这个文档主要讲了什么？", context="文档内容...")

        # 翻译
        translated = ai.translate("Hello world", target_language="中文")
    """

    def __init__(
        self,
        provider: Union[str, ProviderType] = ProviderType.CLAUDE,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        初始化 AI 提供商

        Args:
            provider: 提供商名称或类型
            model: 模型名称（可选，使用默认模型）
            **kwargs: 其他配置参数
        """
        if isinstance(provider, str):
            provider = ProviderType(provider.lower())

        self.provider_type = provider
        provider_class = PROVIDERS.get(provider)

        if provider_class is None:
            raise ValueError(f"不支持的提供商: {provider}")

        self._provider = provider_class(model=model, **kwargs)

    def chat(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        system: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        统一聊天接口

        Args:
            messages: 消息列表
            system: 系统提示（可选）
            **kwargs: 其他参数（max_tokens, temperature 等）

        Returns:
            ChatResponse: 聊天响应
        """
        # 如果提供了 system 消息，添加到消息列表开头
        if system:
            normalized = self._provider._normalize_messages(messages)
            normalized.insert(0, {"role": "system", "content": system})
            messages = normalized

        return self._provider.chat(messages, **kwargs)

    def summarize(
        self,
        text: str,
        language: str = "zh",
        max_length: int = 500,
        **kwargs
    ) -> str:
        """
        生成文本摘要

        Args:
            text: 要摘要的文本
            language: 摘要语言（zh/en）
            max_length: 最大长度
            **kwargs: 其他参数

        Returns:
            str: 摘要文本
        """
        lang_prompt = {
            "zh": "请用中文生成以下文本的摘要，简洁明了，突出重点：",
            "en": "Please generate a summary of the following text in English, concise and highlighting key points:"
        }

        system_prompt = f"""你是一个专业的文本摘要助手。请生成简洁、准确的摘要。
摘要要求：
1. 突出核心内容和关键信息
2. 保持客观准确
3. 摘要长度控制在 {max_length} 字以内
4. 使用{language}语言"""

        messages = [
            {"role": "user", "content": f"{lang_prompt.get(language, lang_prompt['zh'])}\n\n{text}"}
        ]

        response = self.chat(messages, system=system_prompt, max_tokens=max_length * 2, **kwargs)
        return response.content

    def qa(
        self,
        question: str,
        context: str,
        language: str = "zh",
        **kwargs
    ) -> str:
        """
        基于上下文的文档问答

        Args:
            question: 问题
            context: 上下文/文档内容
            language: 回答语言
            **kwargs: 其他参数

        Returns:
            str: 回答
        """
        system_prompt = f"""你是一个专业的文档问答助手。请基于提供的上下文回答问题。

要求：
1. 答案必须基于上下文内容，不要编造信息
2. 如果上下文中没有相关信息，请诚实说明
3. 回答要准确、清晰
4. 使用{language}语言回答"""

        messages = [
            {
                "role": "user",
                "content": f"""上下文：
{context}

问题：{question}

请基于上下文回答问题。"""
            }
        ]

        response = self.chat(messages, system=system_prompt, **kwargs)
        return response.content

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        翻译文本

        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言（可选，自动检测）
            **kwargs: 其他参数

        Returns:
            str: 翻译结果
        """
        source_hint = f" from {source_language}" if source_language else ""

        system_prompt = f"""你是一个专业的翻译助手。请将以下文本翻译成{target_language}。

要求：
1. 保持原文的语气和风格
2. 确保翻译准确、流畅
3. 保留专业术语或提供适当解释
4. 只输出翻译结果，不要添加额外说明"""

        messages = [
            {"role": "user", "content": text}
        ]

        response = self.chat(messages, system=system_prompt, **kwargs)
        return response.content

    def is_available(self) -> bool:
        """检查当前提供商是否可用"""
        return self._provider.is_available()

    @property
    def model(self) -> str:
        """获取当前模型名称"""
        return self._provider.model

    @property
    def provider_name(self) -> str:
        """获取提供商名称"""
        return self._provider.PROVIDER_NAME


def get_ai_provider(
    provider: Union[str, ProviderType] = ProviderType.CLAUDE,
    model: Optional[str] = None,
    **kwargs
) -> AIProvider:
    """
    获取 AI 提供商实例

    Args:
        provider: 提供商名称或类型
        model: 模型名称（可选）
        **kwargs: 其他配置参数

    Returns:
        AIProvider: AI 提供商实例

    示例:
        # 使用默认 Claude 提供商
        ai = get_ai_provider()

        # 使用 OpenAI
        ai = get_ai_provider("openai", model="gpt-4o")

        # 使用 DeepSeek
        ai = get_ai_provider("deepseek")

        # 使用本地 Ollama
        ai = get_ai_provider("ollama", model="llama3.2")
    """
    return AIProvider(provider=provider, model=model, **kwargs)


def list_providers() -> List[Dict[str, Any]]:
    """
    列出所有支持的提供商及其信息

    Returns:
        List[Dict]: 提供商信息列表
    """
    providers_info = []
    for provider_type, provider_class in PROVIDERS.items():
        info = {
            "name": provider_type.value,
            "default_model": provider_class.DEFAULT_MODEL,
            "env_key": getattr(provider_class, "ENV_KEY", None),
            "available": None  # 需要实例化才能检查
        }
        providers_info.append(info)
    return providers_info


# 便捷函数
def chat(
    messages: List[Union[Message, Dict[str, str]]],
    provider: str = "claude",
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    快速聊天函数

    Args:
        messages: 消息列表
        provider: 提供商名称
        model: 模型名称
        **kwargs: 其他参数

    Returns:
        str: 回复内容
    """
    ai = get_ai_provider(provider, model)
    response = ai.chat(messages, **kwargs)
    return response.content


if __name__ == "__main__":
    # 测试代码
    print("AI Provider 统一接口")
    print("=" * 50)

    # 列出所有提供商
    providers = list_providers()
    print("\n支持的 AI 提供商：")
    for p in providers:
        print(f"  - {p['name']}: 默认模型 {p['default_model']}")
        if p['env_key']:
            print(f"    环境变量: {p['env_key']}")
