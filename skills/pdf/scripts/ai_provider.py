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
- 自定义 Provider (通过 YAML 配置)
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


def _load_claude_code_env():
    """
    自动加载 Claude Code 的环境变量配置

    Claude Code 将 API Key 存储在 ~/.claude/settings.json 的 env 字段中。
    这个函数在模块加载时自动调用，实现零配置设计。
    """
    settings_path = Path.home() / '.claude' / 'settings.json'
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                env = settings.get('env', {})
                for key, value in env.items():
                    # 只设置未定义的环境变量
                    if key not in os.environ and value:
                        os.environ[key] = value
        except Exception:
            pass  # 静默失败，不影响正常使用


# 模块加载时自动执行
_load_claude_code_env()

# Import ProviderManager
try:
    from provider_manager import get_provider_manager, ProviderConfig
except ImportError:
    def get_provider_manager(config_path=None):
        return None
    ProviderConfig = None


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
    CUSTOM = "custom"


@dataclass
class Message:
    """聊天消息"""
    role: str
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
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def _normalize_messages(self, messages: List[Union[Message, Dict[str, str]]]) -> List[Dict[str, str]]:
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
    # Claude Code 可能使用的其他环境变量
    ALT_ENV_KEYS = ["ANTHROPIC_AUTH_TOKEN"]

    def __init__(self, model: str = None, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        # 优先使用传入的 api_key，然后检查环境变量
        if api_key is None:
            api_key = os.environ.get(self.ENV_KEY)
            # 如果 ANTHROPIC_API_KEY 未设置，检查 Claude Code 的 ANTHROPIC_AUTH_TOKEN
            if api_key is None:
                api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN")
        # 如果未传入 base_url，检查环境变量
        if base_url is None:
            base_url = os.environ.get("ANTHROPIC_BASE_URL")
        # 将 base_url 存入 config
        if base_url:
            kwargs['base_url'] = base_url
        super().__init__(model, api_key, **kwargs)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                # 检查是否使用自定义 base_url（如 Claude Code 代理）
                base_url = self.config.get('base_url') or os.environ.get("ANTHROPIC_BASE_URL")
                if base_url:
                    self._client = anthropic.Anthropic(api_key=self.api_key, base_url=base_url)
                else:
                    self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("pip install anthropic")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)
        system = None
        chat_messages = []
        for msg in normalized:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        params = {"model": self.model, "messages": chat_messages, "max_tokens": kwargs.get("max_tokens", 4096)}
        if system:
            params["system"] = system
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        response = client.messages.create(**params)

        # 处理代理服务器可能返回的非标准响应
        if isinstance(response, str):
            # 某些代理直接返回字符串
            return ChatResponse(
                content=response,
                model=self.model,
                provider=self.PROVIDER_NAME,
                usage=None,
                finish_reason="stop"
            )
        elif hasattr(response, 'choices'):
            # OpenAI 格式响应（某些代理使用）
            return ChatResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=self.PROVIDER_NAME,
                usage={"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens} if response.usage else None,
                finish_reason=response.choices[0].finish_reason
            )
        else:
            # 标准 Anthropic 响应
            # 处理 response.content 可能包含多个 block 的情况
            content_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content_text += block.text
                elif isinstance(block, dict) and 'text' in block:
                    content_text += block['text']
            return ChatResponse(
                content=content_text,
                model=response.model,
                provider=self.PROVIDER_NAME,
                usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens} if hasattr(response, 'usage') else None,
                finish_reason=response.stop_reason if hasattr(response, 'stop_reason') else "stop"
            )


class OpenAIProvider(BaseAIProvider):
    """OpenAI 提供商"""
    PROVIDER_NAME = "openai"
    DEFAULT_MODEL = "gpt-4o"
    ENV_KEY = "OPENAI_API_KEY"

    def __init__(self, model: str = None, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        model = model or self.DEFAULT_MODEL
        api_key = api_key or os.environ.get(self.ENV_KEY)
        super().__init__(model, api_key, **kwargs)
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError("pip install openai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)
        params = {"model": self.model, "messages": normalized}
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        response = client.chat.completions.create(**params)
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.PROVIDER_NAME,
            usage={"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens},
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
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("pip install google-generativeai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)
        gemini_messages = []
        for msg in normalized:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        generation_config = {}
        if "max_tokens" in kwargs:
            generation_config["max_output_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            generation_config["temperature"] = kwargs["temperature"]
        response = client.generate_content(gemini_messages, generation_config=generation_config if generation_config else None)
        return ChatResponse(
            content=response.text,
            model=self.model,
            provider=self.PROVIDER_NAME,
            usage=None,
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
    """Qwen 提供商 (OpenAI 兼容)"""
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
        if self._client is None:
            try:
                from zhipuai import ZhipuAI
                self._client = ZhipuAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("pip install zhipuai")
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Union[Message, Dict[str, str]]], **kwargs) -> ChatResponse:
        client = self._get_client()
        normalized = self._normalize_messages(messages)
        params = {"model": self.model, "messages": normalized}
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        response = client.chat.completions.create(**params)
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.PROVIDER_NAME,
            usage={"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens} if response.usage else None,
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
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
            except ImportError:
                raise ImportError("pip install ollama")
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
        params = {"model": self.model, "messages": normalized}
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


class CustomOpenAIProvider(OpenAIProvider):
    """自定义 OpenAI 兼容 Provider"""
    PROVIDER_NAME = "custom"
    DEFAULT_MODEL = ""

    def __init__(self, provider_id: str, model: str = None, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        self.provider_id = provider_id
        self.PROVIDER_NAME = provider_id
        model = model or self.DEFAULT_MODEL
        super().__init__(model, api_key, base_url=base_url, **kwargs)


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

# 字符串 ID 到 ProviderType 的映射
PROVIDER_ID_TO_TYPE = {
    'claude': ProviderType.CLAUDE,
    'openai': ProviderType.OPENAI,
    'gemini': ProviderType.GEMINI,
    'deepseek': ProviderType.DEEPSEEK,
    'qwen': ProviderType.QWEN,
    'zhipu': ProviderType.ZHIPU,
    'moonshot': ProviderType.MOONSHOT,
    'ollama': ProviderType.OLLAMA,
}

# 字符串 ID 到 Provider 类的映射
PROVIDER_CLASS_MAP = {
    'claude': ClaudeProvider,
    'openai': OpenAIProvider,
    'gemini': GeminiProvider,
    'deepseek': DeepSeekProvider,
    'qwen': QwenProvider,
    'zhipu': ZhipuProvider,
    'moonshot': MoonshotProvider,
    'ollama': OllamaProvider,
}


def _get_provider_config_from_manager(provider_id: str) -> Optional[Dict[str, Any]]:
    """从 ProviderManager 获取 provider 配置"""
    manager = get_provider_manager()
    if manager is None:
        return None
    config = manager.get_provider(provider_id)
    if config is None:
        return None
    return {
        'id': config.id,
        'name': config.name,
        'type': config.type,
        'api_base': config.api_base,
        'default_model': config.default_model or (config.models[0].id if config.models else ''),
        'env_key': config.env_key,
        'cost_multiplier': config.cost_multiplier,
        'models': [{'id': m.id, 'name': m.name, 'max_tokens': m.max_tokens} for m in config.models],
    }


class AIProvider:
    """统一的 AI 提供商接口"""

    def __init__(self, provider: Union[str, ProviderType] = None, model: Optional[str] = None, **kwargs):
        # 如果未指定 provider，使用 ProviderManager 的默认配置
        if provider is None:
            manager = get_provider_manager()
            if manager:
                provider = manager.get_default_provider_id()
            else:
                provider = ProviderType.CLAUDE

        # 保存原始 provider 参数用于确定 provider_type
        self._original_provider = provider
        
        # 处理字符串 provider ID
        provider_id = provider.value if isinstance(provider, ProviderType) else provider.lower()

        # 尝试从 ProviderManager 获取配置
        config = _get_provider_config_from_manager(provider_id)
        
        if config:
            self._init_from_config(config, model, **kwargs)
        elif provider_id in PROVIDER_CLASS_MAP:
            self._init_builtin(provider_id, model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_provider_type_for_id(self, provider_id: str) -> Union[ProviderType, str]:
        """根据 provider ID 获取 ProviderType 枚举（用于内置 provider）或字符串 ID（用于自定义 provider）"""
        if provider_id in PROVIDER_ID_TO_TYPE:
            return PROVIDER_ID_TO_TYPE[provider_id]
        return provider_id

    def _init_from_config(self, config: Dict[str, Any], model: Optional[str], **kwargs):
        """从配置初始化 provider"""
        provider_id = config['id']
        provider_type_str = config.get('type', 'openai-compatible')

        # 获取 API key - 支持多个环境变量名（零配置设计）
        api_key = kwargs.pop('api_key', None)
        if api_key is None and config.get('env_key'):
            # 首先检查主环境变量
            api_key = os.environ.get(config['env_key'])
            # 对于 Claude，还检查 Claude Code 使用的 ANTHROPIC_AUTH_TOKEN
            if api_key is None and provider_id == 'claude':
                api_key = os.environ.get('ANTHROPIC_AUTH_TOKEN')

        # 获取 API base URL - 优先使用环境变量（零配置设计）
        # 顺序：环境变量 > YAML 配置
        env_base_url = os.environ.get('ANTHROPIC_BASE_URL') if provider_id == 'claude' else None
        if env_base_url:
            api_base = env_base_url
        else:
            api_base = kwargs.pop('base_url', config.get('api_base'))

        # 获取模型
        if model is None:
            model = config.get('default_model', '')

        # 根据类型创建 provider
        if provider_type_str == 'official':
            if provider_id == 'claude':
                self._provider = ClaudeProvider(model=model, api_key=api_key, base_url=api_base, **kwargs)
            elif provider_id == 'gemini':
                self._provider = GeminiProvider(model=model, api_key=api_key, **kwargs)
            elif provider_id == 'zhipu':
                self._provider = ZhipuProvider(model=model, api_key=api_key, **kwargs)
            elif provider_id == 'openai':
                self._provider = OpenAIProvider(model=model, api_key=api_key, base_url=api_base, **kwargs)
            else:
                self._provider = CustomOpenAIProvider(provider_id=provider_id, model=model, api_key=api_key, base_url=api_base, **kwargs)
        elif provider_type_str == 'local':
            if provider_id == 'ollama':
                self._provider = OllamaProvider(model=model, base_url=api_base, **kwargs)
            else:
                self._provider = CustomOpenAIProvider(provider_id=provider_id, model=model, api_key=api_key or 'dummy', base_url=api_base, **kwargs)
        else:
            self._provider = CustomOpenAIProvider(provider_id=provider_id, model=model, api_key=api_key, base_url=api_base, **kwargs)

        # 设置 provider_type：内置 provider 使用枚举，自定义 provider 使用字符串
        self.provider_type = self._get_provider_type_for_id(provider_id)
        self._config = config

    def _init_builtin(self, provider_id: str, model: Optional[str], **kwargs):
        """使用内置类初始化 provider"""
        # 始终使用 ProviderType 枚举
        self.provider_type = PROVIDER_ID_TO_TYPE[provider_id]
        provider_class = PROVIDER_CLASS_MAP.get(provider_id)
        
        if provider_class is None:
            raise ValueError(f"Unsupported provider: {provider_id}")
        
        self._provider = provider_class(model=model, **kwargs)
        self._config = None

    def chat(self, messages: List[Union[Message, Dict[str, str]]], system: Optional[str] = None, **kwargs) -> ChatResponse:
        if system:
            normalized = self._provider._normalize_messages(messages)
            normalized.insert(0, {"role": "system", "content": system})
            messages = normalized
        return self._provider.chat(messages, **kwargs)

    def summarize(self, text: str, language: str = "zh", max_length: int = 500, **kwargs) -> str:
        lang_prompt = {"zh": "请用中文生成以下文本的摘要，简洁明了，突出重点：", "en": "Please generate a summary of the following text in English:"}
        system_prompt = f"你是一个专业的文本摘要助手。请生成简洁、准确的摘要，长度控制在 {max_length} 字以内，使用{language}语言。"
        messages = [{"role": "user", "content": f"{lang_prompt.get(language, lang_prompt['zh'])}\n\n{text}"}]
        response = self.chat(messages, system=system_prompt, max_tokens=max_length * 2, **kwargs)
        return response.content

    def qa(self, question: str, context: str, language: str = "zh", **kwargs) -> str:
        system_prompt = f"你是一个专业的文档问答助手。请基于提供的上下文回答问题，使用{language}语言回答。"
        messages = [{"role": "user", "content": f"上下文：\n{context}\n\n问题：{question}\n\n请基于上下文回答问题。"}]
        response = self.chat(messages, system=system_prompt, **kwargs)
        return response.content

    def translate(self, text: str, target_language: str, source_language: Optional[str] = None, **kwargs) -> str:
        system_prompt = f"你是一个专业的翻译助手。请将以下文本翻译成{target_language}，保持原文的语气和风格。"
        messages = [{"role": "user", "content": text}]
        response = self.chat(messages, system=system_prompt, **kwargs)
        return response.content

    def is_available(self) -> bool:
        return self._provider.is_available()

    @property
    def model(self) -> str:
        return self._provider.model

    @property
    def provider_name(self) -> str:
        return self._provider.PROVIDER_NAME


def get_ai_provider(provider: Union[str, ProviderType] = None, model: Optional[str] = None, **kwargs) -> AIProvider:
    """获取 AI 提供商实例"""
    return AIProvider(provider=provider, model=model, **kwargs)


def list_providers() -> List[Dict[str, Any]]:
    """列出所有支持的提供商及其信息（向后兼容格式）"""
    manager = get_provider_manager()
    if manager:
        providers_info = []
        for provider in manager.list_providers():
            # 向后兼容：name 字段返回 provider id，display_name 返回显示名称
            info = {
                "name": provider.id,  # 向后兼容：name 字段包含 provider id
                "display_name": provider.name,
                "id": provider.id,
                "type": provider.type,
                "default_model": provider.get_default_model(),
                "env_key": provider.env_key,
                "api_base": provider.api_base,
                "models": [{"id": m.id, "name": m.name} for m in provider.models],
            }
            providers_info.append(info)
        return providers_info
    
    # 回退到内置列表
    providers_info = []
    for provider_type, provider_class in PROVIDERS.items():
        info = {
            "name": provider_type.value,  # 向后兼容
            "default_model": provider_class.DEFAULT_MODEL,
            "env_key": getattr(provider_class, "ENV_KEY", None),
        }
        providers_info.append(info)
    return providers_info


def get_default_provider() -> str:
    """获取默认 provider ID"""
    manager = get_provider_manager()
    if manager:
        return manager.get_default_provider_id()
    return 'claude'


def chat(messages: List[Union[Message, Dict[str, str]]], provider: str = None, model: Optional[str] = None, **kwargs) -> str:
    """快速聊天函数"""
    ai = get_ai_provider(provider, model)
    response = ai.chat(messages, **kwargs)
    return response.content


if __name__ == "__main__":
    print("AI Provider Unified Interface")
    print("=" * 50)
    providers = list_providers()
    print("\nSupported AI Providers:")
    for p in providers:
        print(f"  - {p.get('name')}: {p.get('display_name', p.get('name'))}")
        if p.get('env_key'):
            print(f"    Env Key: {p['env_key']}")
