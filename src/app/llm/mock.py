from langchain_core.messages import AIMessage, BaseMessage

class MockChatProvider:
    """
    Deterministic mock chat provider.

    Used for tests and CI.
    """

    provider = "mock"
    model_name = "mock-echo"

    def invoke(self, messages: list[BaseMessage]) -> AIMessage:
        if not messages:
            return AIMessage(content="Mock LLM response: empty input")

        last_message = messages[-1]
        return AIMessage(content=f"Mock LLM response: {last_message.content}")