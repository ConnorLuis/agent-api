from langchain_core.tools import tool

from src.app.rag.retriever import search_knowledge
from src.app.agent.mcp_tool_gateway import search_knowledge_base_gateway_text


@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the product."""
    return a * b

@tool
def search_knowledge_base(query: str, k: int = 3) -> str:
    """Search the local knowledge base.

    Day72 routes this tool through a config-controlled MCP gateway.
    By default MCP is disabled and this falls back to the original internal
    deterministic search path.
    """
    return search_knowledge_base_gateway_text(query=query, k=k)


tools = [add, multiply, search_knowledge_base]