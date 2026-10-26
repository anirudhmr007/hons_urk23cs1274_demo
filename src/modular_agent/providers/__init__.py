"""LLM provider adapters and factory."""

from modular_agent.config import AppConfig
from modular_agent.providers.base import (
    BaseLLMProvider,
    ChatMessage,
    LLMResponse,
    MessageRole,
    ToolCall,
    ToolDefinition,
    mask_secret,
)
from modular_agent.providers.hosted_provider import HostedOpenAIProvider
from modular_agent.providers.mock_provider import MockLLMProvider
from modular_agent.providers.ollama_provider import OllamaProvider

__all__ = [
    "BaseLLMProvider",
    "ChatMessage",
    "LLMResponse",
    "MessageRole",
    "ToolCall",
    "ToolDefinition",
    "MockLLMProvider",
    "OllamaProvider",
    "HostedOpenAIProvider",
    "mask_secret",
    "create_llm_provider",
]


def create_llm_provider(config: AppConfig) -> BaseLLMProvider:
    """Factory function to instantiate the configured LLM provider."""
    provider_name = config.llm_provider.lower().strip()

    if provider_name == "ollama":
        return OllamaProvider(
            base_url=config.llm_base_url,
            model_name=config.llm_model,
            timeout_seconds=config.llm_timeout,
        )
    elif provider_name in ("openai", "hosted"):
        return HostedOpenAIProvider(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url if config.llm_base_url != "http://localhost:11434" else "https://api.openai.com/v1",
            model_name=config.llm_model if config.llm_model != "llama3.1" else "gpt-4o-mini",
            timeout_seconds=config.llm_timeout,
        )
    elif provider_name == "mock":
        return MockLLMProvider(model_name=config.llm_model)
    else:
        raise ValueError(
            f"Unsupported LLM provider '{provider_name}'. "
            "Supported providers: 'mock', 'ollama', 'hosted' (or 'openai')."
        )

