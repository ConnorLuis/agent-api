from langgraph.graph import END, START, StateGraph

from src.app.agent.nodes import agent_node
from src.app.agent.state import AgentState

def build_agent_graph():
    """
    Flow:
        START -> agent -> END
    """
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)

    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)

    return builder.compile()


agent_graph = build_agent_graph()


def invoke_agent(message: str, thread_id: str | None = None) -> AgentState:
    """
    Invoke the compiled LangGraph with initial state.
    """
    initial_state: AgentState = {
        "message": message,
        "thread_id": thread_id,
    }

    return agent_graph.invoke(initial_state)
