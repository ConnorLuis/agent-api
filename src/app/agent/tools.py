from langchain_core.tools import tool

from src.app.rag.retriever import search_knowledge


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
    """Search the local knowledge base for Agent, LangGraph, and RAG related information."""
    results = search_knowledge(query=query, k=k)

    if not results:
        return "No relevant documents found."

    lines = []

    for index, item in enumerate(results, start=1):
        lines.append(
            f"[{index}] source={item.source}, score={item.score}\n{item.content}"
        )

    return "\n\n".join(lines)

tools = [add, multiply, search_knowledge_base]