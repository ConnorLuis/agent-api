from typing import Protocol

from langchain_core.messages import AIMessage, BaseMessage

class ChatProvider(Protocol):
    """
    Minimal chat provider protocol.

    Later providers:
    - MockChatProvider
    - OllamaChatProvider
    - OpenAIChatProvider
    """

    provider: str
    model_name: str

    def invoke(self, messages: list[BaseMessage]) -> AIMessage:
        ...

class LLMProviderError(RuntimeError):
    """Raised when LLM provider configuration is invalid."""