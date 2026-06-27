from langchain_core.messages import HumanMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.app.agent.nodes import agent_node
from src.app.agent.state import AgentState
from src.app.agent.tools import tools

def build_agent_graph():
    """
    Flow:
        START -> agent -> tools -> agent -> END

    The edge from agent is conditional:
        - if AIMessage has tool_calls: go to tools
        - otherwise: end
    """
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile()


agent_graph = build_agent_graph()


def invoke_agent(message: str, thread_id: str | None = None) -> AgentState:
    """
    Invoke the compiled LangGraph with initial messages.
    """
    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": thread_id,
    }

    return agent_graph.invoke(initial_state)
