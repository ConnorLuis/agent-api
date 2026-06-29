from langchain_core.messages import SystemMessage

from src.app.agent.state import AgentState
from src.app.agent.tools import tools
from src.app.llm.factory import get_chat_provider


SYSTEM_PROMPT = """
You are a helpful tool-calling agent.

You have access to these tools:
- add: calculate the sum of two integers
- multiply: calculate the product of two integers

Rules:
1. If the user asks for arithmetic involving addition, call the add tool.
2. If the user asks for arithmetic involving multiplication, call the multiply tool.
3. After receiving a tool result, answer the user clearly in Chinese.
4. If no tool is needed, answer directly.
""".strip()

def llm_agent_node(state: AgentState) -> dict:
    """
    Real LLM-backed agent node.

    Difference from the deterministic Day3 agent_node:
    - Day3 agent_node manually created tool_calls by rules.
    - Day10 llm_agent_node lets the LLM decide whether to call tools.
    """
    provider = get_chat_provider(provider="ollama")

    if not hasattr(provider, "bind_tools"):
        raise RuntimeError("Current provider does not support tool calling.")

    model_with_tools = provider.bind_tools(tools)

    messages = state["messages"]
    response = model_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), *messages]
    )

    return {"messages": [response]}