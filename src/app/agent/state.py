from typing_extensions import NotRequired
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """

    messages: managed by MessagesState with add_messages reducer
    thread_id: reserved for short-term memory in later days
    """
    thread_id: NotRequired[str | None]