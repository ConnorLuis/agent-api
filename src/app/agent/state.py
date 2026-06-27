from typing_extensions import NotRequired, TypedDict

class AgentState(TypedDict):
    """
    Minimal LangGraph state for Day2.

    message: user input
    answer: graph output
    thread_id: reserved for short-term memory in later days
    """

    message: str
    answer: NotRequired[str]
    thread_id: NotRequired[str | None]