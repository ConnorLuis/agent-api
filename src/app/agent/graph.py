from uuid import uuid4

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.app.agent.nodes import agent_node
from src.app.agent.state import AgentState
from src.app.agent.tools import tools

def build_agent_graph():
    """
    Flow:
        START -> agent -> tools -> agent -> END

    Short-term memory:
        checkpointer + thread_id
    """
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)


agent_graph = build_agent_graph()


def invoke_agent(message: str, thread_id: str | None = None) -> AgentState:
    """
    Invoke the compiled LangGraph with short-term memory.

    If thread_id is provided, the graph will continue the same conversation thread.
    If thread_id is None, a new thread_id will be generated.
    """
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    config = {
        "configurable": {
            "thread_id": final_thread_id,
        }
    }

    result = agent_graph.invoke(initial_state, config=config)

    result["thread_id"] = final_thread_id
    return result
