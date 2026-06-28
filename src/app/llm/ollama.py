from langchain_core.messages import AIMessage, BaseMessage
from langchain_ollama import ChatOllama

class OllamaChatProvider:
    """
    Ollama chat provider based on langchain-ollama ChatOllama.
    """

    provider = "ollama"

    def __init__(self, model_name: str, base_url: str, temperature: float = 0.0,) -> None:
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature

        self.clent = ChatOllama(model=model_name, base_url=base_url, temperature=temperature)

    def invoke(self, messages: list[BaseMessage]) -> AIMessage:
        response = self.clent.invoke(messages)

        if isinstance(response, AIMessage):
            return response

        return AIMessage(content=str(response.content))