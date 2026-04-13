"""
Provider Manager - AI Provider Configuration Management

Manages AI provider configurations loaded from YAML file.
Supports official providers and custom user-defined providers.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import threading


@dataclass
class ModelConfig:
    """Model configuration"""
    id: str
    name: str
    max_tokens: int = 4096
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


@dataclass
class ProviderConfig:
    """Provider configuration"""
    id: str
    name: str
    type: str  # official, openai-compatible, local
    api_base: Optional[str] = None
    models: List[ModelConfig] = field(default_factory=list)
    default_model: Optional[str] = None
    cost_multiplier: float = 1.0
    env_key: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get model configuration by ID"""
        for model in self.models:
            if model.id == model_id:
                return model
        return None
    
    def get_default_model(self) -> str:
        """Get default model ID"""
        if self.default_model:
            return self.default_model
        if self.models:
            return self.models[0].id
        return ""


class ProviderManager:
    """
    AI Provider Configuration Manager
    
    Singleton class that manages provider configurations.
    Supports loading from YAML, runtime modifications, and custom providers.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ProviderManager.
        
        Args:
            config_path: Path to providers.yaml. If None, uses default location.
        """
        if self._initialized:
            return
            
        self._providers: Dict[str, ProviderConfig] = {}
        self._default_provider_id: Optional[str] = None
        self._cost_limits: Dict[str, Any] = {}
        self._config_path = config_path
        
        # Load configuration
        self._load_config()
        self._initialized = True
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        possible_paths = [
            os.path.join(os.getcwd(), 'config', 'providers.yaml'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'providers.yaml'),
            os.path.join(os.path.expanduser('~'), '.pdf-master', 'providers.yaml'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return possible_paths[0]
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = self._config_path or self._get_default_config_path()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                for provider_data in data.get('providers', []):
                    provider = self._parse_provider(provider_data)
                    self._providers[provider.id] = provider
                
                self._default_provider_id = data.get('default_provider', 'claude')
                self._cost_limits = data.get('cost_limits', {})
                
            except Exception as e:
                print(f"Warning: Failed to load provider config: {e}")
                self._load_builtin_providers()
        else:
            self._load_builtin_providers()
    
    def _parse_provider(self, data: Dict[str, Any]) -> ProviderConfig:
        """Parse provider configuration from dict"""
        models = []
        for model_data in data.get('models', []):
            models.append(ModelConfig(
                id=model_data.get('id', ''),
                name=model_data.get('name', model_data.get('id', '')),
                max_tokens=model_data.get('max_tokens', 4096),
                cost_per_1k_input=model_data.get('cost_per_1k_input', 0.0),
                cost_per_1k_output=model_data.get('cost_per_1k_output', 0.0),
            ))
        
        return ProviderConfig(
            id=data.get('id', ''),
            name=data.get('name', data.get('id', '')),
            type=data.get('type', 'openai-compatible'),
            api_base=data.get('api_base'),
            models=models,
            default_model=data.get('default_model'),
            cost_multiplier=data.get('cost_multiplier', 1.0),
            env_key=data.get('env_key'),
            extra={k: v for k, v in data.items() 
                   if k not in ['id', 'name', 'type', 'api_base', 'models', 
                               'default_model', 'cost_multiplier', 'env_key']},
        )
    
    def _load_builtin_providers(self):
        """Load built-in provider configurations as fallback"""
        builtin_configs = [
            {'id': 'claude', 'name': 'Claude (Anthropic)', 'type': 'official',
             'api_base': 'https://api.anthropic.com',
             'models': [{'id': 'claude-sonnet-4-6', 'name': 'Claude Sonnet 4.6', 'max_tokens': 8192}],
             'default_model': 'claude-sonnet-4-6', 'env_key': 'ANTHROPIC_API_KEY'},
            {'id': 'openai', 'name': 'OpenAI', 'type': 'official',
             'api_base': 'https://api.openai.com/v1',
             'models': [{'id': 'gpt-4o', 'name': 'GPT-4o', 'max_tokens': 4096}],
             'default_model': 'gpt-4o', 'env_key': 'OPENAI_API_KEY'},
            {'id': 'gemini', 'name': 'Google Gemini', 'type': 'official',
             'api_base': 'https://generativelanguage.googleapis.com',
             'models': [{'id': 'gemini-2.0-flash-exp', 'name': 'Gemini 2.0 Flash', 'max_tokens': 8192}],
             'default_model': 'gemini-2.0-flash-exp', 'env_key': 'GOOGLE_API_KEY'},
            {'id': 'deepseek', 'name': 'DeepSeek', 'type': 'openai-compatible',
             'api_base': 'https://api.deepseek.com/v1',
             'models': [{'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'max_tokens': 4096}],
             'default_model': 'deepseek-chat', 'env_key': 'DEEPSEEK_API_KEY'},
            {'id': 'qwen', 'name': 'Qwen', 'type': 'openai-compatible',
             'api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
             'models': [{'id': 'qwen-turbo', 'name': 'Qwen Turbo', 'max_tokens': 4096}],
             'default_model': 'qwen-turbo', 'env_key': 'QWEN_API_KEY'},
            {'id': 'zhipu', 'name': 'Zhipu GLM', 'type': 'official',
             'api_base': 'https://open.bigmodel.cn/api/paas/v4',
             'models': [{'id': 'glm-4-flash', 'name': 'GLM-4 Flash', 'max_tokens': 4096}],
             'default_model': 'glm-4-flash', 'env_key': 'ZHIPU_API_KEY'},
            {'id': 'moonshot', 'name': 'Moonshot (Kimi)', 'type': 'openai-compatible',
             'api_base': 'https://api.moonshot.cn/v1',
             'models': [{'id': 'moonshot-v1-8k', 'name': 'Moonshot V1 8K', 'max_tokens': 8192}],
             'default_model': 'moonshot-v1-8k', 'env_key': 'MOONSHOT_API_KEY'},
            {'id': 'ollama', 'name': 'Ollama (Local)', 'type': 'local',
             'api_base': 'http://localhost:11434',
             'models': [{'id': 'llama3.2', 'name': 'Llama 3.2', 'max_tokens': 4096}],
             'default_model': 'llama3.2', 'env_key': None},
        ]
        
        for config in builtin_configs:
            self._providers[config['id']] = self._parse_provider(config)
        
        self._default_provider_id = 'claude'
    
    def load_providers(self, config_path: str) -> bool:
        """Load providers from a specific config file."""
        if not os.path.exists(config_path):
            return False
        try:
            self._config_path = config_path
            self._providers.clear()
            self._load_config()
            return True
        except Exception:
            return False
    
    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration by ID."""
        return self._providers.get(provider_id)
    
    def list_providers(self) -> List[ProviderConfig]:
        """List all available providers."""
        return list(self._providers.values())
    
    def list_provider_ids(self) -> List[str]:
        """List all provider IDs."""
        return list(self._providers.keys())
    
    def add_provider(self, config: Dict[str, Any], save: bool = False) -> bool:
        """Add a new provider or update existing one."""
        try:
            provider = self._parse_provider(config)
            if not provider.id:
                return False
            
            self._providers[provider.id] = provider
            
            if save:
                self._save_config()
            
            return True
        except Exception:
            return False
    
    def remove_provider(self, provider_id: str, save: bool = False) -> bool:
        """Remove a provider by ID."""
        if provider_id not in self._providers:
            return False
        
        builtin_ids = ['claude', 'openai', 'gemini', 'deepseek', 'qwen', 'zhipu', 'moonshot', 'ollama']
        if provider_id in builtin_ids:
            print(f"Warning: Cannot remove built-in provider '{provider_id}'")
            return False
        
        del self._providers[provider_id]
        
        if self._default_provider_id == provider_id:
            self._default_provider_id = 'claude'
        
        if save:
            self._save_config()
        
        return True
    
    def set_default(self, provider_id: str, save: bool = False) -> bool:
        """Set the default provider."""
        if provider_id not in self._providers:
            return False
        
        self._default_provider_id = provider_id
        
        if save:
            self._save_config()
        
        return True
    
    def get_default_provider(self) -> Optional[ProviderConfig]:
        """Get the default provider configuration."""
        if self._default_provider_id:
            return self._providers.get(self._default_provider_id)
        return self._providers.get('claude')
    
    def get_default_provider_id(self) -> str:
        """Get default provider ID"""
        return self._default_provider_id or 'claude'
    
    def get_cost_limits(self) -> Dict[str, Any]:
        """Get cost limit settings"""
        return self._cost_limits.copy()
    
    def is_cost_tracking_enabled(self) -> bool:
        """Check if cost tracking is enabled"""
        return self._cost_limits.get('tracking_enabled', False)
    
    def _save_config(self):
        """Save current configuration to YAML file"""
        config_path = self._config_path or self._get_default_config_path()
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        data = {
            'providers': [],
            'default_provider': self._default_provider_id,
            'cost_limits': self._cost_limits,
        }
        
        for provider in self._providers.values():
            provider_data = {
                'id': provider.id,
                'name': provider.name,
                'type': provider.type,
                'api_base': provider.api_base,
                'models': [
                    {'id': m.id, 'name': m.name, 'max_tokens': m.max_tokens}
                    for m in provider.models
                ],
                'default_model': provider.default_model,
                'cost_multiplier': provider.cost_multiplier,
                'env_key': provider.env_key,
            }
            provider_data.update(provider.extra)
            data['providers'].append(provider_data)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'ProviderManager':
        """Get the singleton instance of ProviderManager."""
        return cls(config_path)
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)"""
        with cls._lock:
            cls._instance = None


def get_provider_manager(config_path: Optional[str] = None) -> ProviderManager:
    """Get ProviderManager singleton instance"""
    return ProviderManager.get_instance(config_path)


if __name__ == "__main__":
    manager = ProviderManager.get_instance()
    
    print("Available Providers:")
    print("=" * 50)
    for provider in manager.list_providers():
        print(f"  - {provider.id}: {provider.name}")
        print(f"    Type: {provider.type}")
        print(f"    Default Model: {provider.get_default_model()}")
        print(f"    Env Key: {provider.env_key}")
        print()
    
    print(f"Default Provider: {manager.get_default_provider_id()}")
