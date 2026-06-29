from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.app.agent.llm_nodes import llm_agent_node
from src.app.agent.memory import build_sqlite_checkpointer
from src.app.agent.state import AgentState
from src.app.agent.tools import tools


def build_llm_agent_graph():
    builder = StateGraph(AgentState)

    builder.add_node("agent", llm_agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    checkpointer = build_sqlite_checkpointer()
    return builder.compile(checkpointer=checkpointer)


llm_agent_graph = build_llm_agent_graph()


def _build_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def invoke_llm_agent(message: str, thread_id: str | None = None) -> AgentState:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    config = _build_config(final_thread_id)
    result = llm_agent_graph.invoke(initial_state, config=config)
    result["thread_id"] = final_thread_id

    return result


def serialize_message(message: BaseMessage) -> dict:
    return {
        "type": message.__class__.__name__,
        "content": str(message.content),
        "tool_calls": getattr(message, "tool_calls", None),
        "name": getattr(message, "name", None),
    }


def debug_llm_agent(message: str, thread_id: str | None = None) -> dict:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    config = _build_config(final_thread_id)

    steps = []

    for update in llm_agent_graph.stream(
        initial_state,
        config=config,
        stream_mode="updates",
    ):
        for node_name, node_update in update.items():
            messages = node_update.get("messages", [])

            if not isinstance(messages, list):
                messages = [messages]

            steps.append(
                {
                    "node": node_name,
                    "messages": [
                        serialize_message(message)
                        for message in messages
                    ],
                }
            )

    final_state = llm_agent_graph.get_state(config).values
    final_messages = final_state["messages"]
    final_answer = str(final_messages[-1].content)

    return {
        "thread_id": final_thread_id,
        "steps": steps,
        "final_answer": final_answer,
        "messages_count": len(final_messages),
    }