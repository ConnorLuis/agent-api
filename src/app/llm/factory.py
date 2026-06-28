from typing import Literal

from src.app.core.config import get_settings
from src.app.llm.base import ChatProvider, LLMProviderError
from src.app.llm.mock import MockChatProvider
from src.app.llm.ollama import OllamaChatProvider

ProviderName = Literal["ollama", "mock"]

def get_chat_provider(provider: ProviderName | None = None) -> ChatProvider:
    settings = get_settings()
    provider_name = provider or settings.llm_provider

    if provider_name == "mock":
        return MockChatProvider()

    if provider_name == "ollama":
        return OllamaChatProvider(
            model_name=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.ollama_temperature,
        )
    raise LLMProviderError(f"Unsupported LLM provider: {provider_name}")
