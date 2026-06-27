from typing import Any
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.app.agent.memory import build_sqlite_checkpointer
from src.app.agent.nodes import agent_node
from src.app.agent.state import AgentState
from src.app.agent.tools import tools

def build_agent_graph():
    """
    Build Day6 Tool Calling Agent graph with SQLite short-term memory.

    Flow:
        START -> agent -> tools -> agent -> END

    Persistent short-term memory:
        SqliteSaver + thread_id
    """
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    checkpointer = build_sqlite_checkpointer()

    return builder.compile(checkpointer=checkpointer)


agent_graph = build_agent_graph()

def _build_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }

def _build_initial_state(message: str, thread_id: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=message)],
        "thread_id": thread_id,
    }

def serialize_message(message: BaseMessage) -> dict[str, Any]:
    """
    Convert a LangChain message object to a JSON-serializable dict.
    """
    return {
        "type": type(message).__name__,
        "content": str(message.content),
        "tool_calls": getattr(message, "tool_calls", None),
        "name": getattr(message, "name", None),
    }


def invoke_agent(message: str, thread_id: str | None = None) -> AgentState:
    """
    Invoke the compiled LangGraph with persistent short-term memory.

    If thread_id is provided, the graph will continue the same conversation thread.
    If thread_id is None, a new thread_id will be generated.
    """
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    result = agent_graph.invoke(
        _build_initial_state(message, final_thread_id),
        config=_build_config(final_thread_id),
    )

    result["thread_id"] = final_thread_id
    return result


def debug_agent(message: str, thread_id: str | None = None) -> dict[str, Any]:
    """
    Run the graph in debug mode.

    It streams node updates so we can inspect how the Agent moves through:
        HumanMessage -> AIMessage(tool_calls) -> ToolMessage -> AIMessage(final)
    """
    final_thread_id = thread_id or f"debug-thread-{uuid4().hex[:8]}"

    steps: list[dict[str, Any]] = []

    for chunk in agent_graph.stream(
        _build_initial_state(message, final_thread_id),
        config=_build_config(final_thread_id),
        stream_mode="updates",
    ):
        for node_name, update in chunk.items():
            raw_messages = update.get("messages", [])
            messages = [serialize_message(message) for message in raw_messages]

            steps.append(
                {
                    "node": node_name,
                    "messages": messages,
                }
            )

    state_snapshot = agent_graph.get_state(
        _build_config(final_thread_id)
    )

    final_messages = state_snapshot.values.get("messages", [])
    final_answer = ""
    if final_messages:
        final_answer = str(final_messages[-1].content)

    return {
        "thread_id": final_thread_id,
        "steps": steps,
        "final_answer": final_answer,
        "messages_count": len(final_messages)
    }
