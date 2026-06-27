from src.app.agent.state import AgentState

def agent_node(state: AgentState) -> dict:
    """
    It reads the current state and returns a partial state update.
    Later this node will be replaced by an LLM / ReAct / Tool Calling node.
    """
    user_message = state["message"]

    return {
        "answer": f"LangGraph agent response: {user_message}"
    }