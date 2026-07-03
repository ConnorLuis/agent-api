import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM


class AgenticRagState(TypedDict, total=False):
    query: str
    top_k: int
    source_filter: str | None
    max_chars: int
    embedding_dim: int
    keyword_weight: float
    vector_weight: float

    retrieval_needed: bool
    rewritten_query: str
    retrieval_results: list[dict[str, Any]]
    relevance_score: float
    citations: list[str]
    final_answer: str
    steps: Annotated[list[str], operator.add]


def _normalize_query(query: str) -> str:
    normalized = query.strip()

    prefixes = [
        "请搜索知识库：",
        "搜索知识库：",
        "请检索知识库：",
        "检索知识库：",
        "知识库：",
    ]

    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()

    return normalized


def query_analyzer_node(state: AgenticRagState) -> dict[str, Any]:
    query = state["query"].strip().lower()

    retrieval_keywords = [
        "rag",
        "langgraph",
        "agent",
        "知识库",
        "检索",
        "搜索",
        "工具",
        "workflow",
        "graph",
    ]

    retrieval_needed = any(keyword in query for keyword in retrieval_keywords)

    return {
        "retrieval_needed": retrieval_needed,
        "steps": ["query_analyzer"],
    }


def should_retrieve(state: AgenticRagState) -> str:
    if state.get("retrieval_needed"):
        return "retrieve"

    return "direct"


def query_rewriter_node(state: AgenticRagState) -> dict[str, Any]:
    rewritten_query = _normalize_query(state["query"])

    return {
        "rewritten_query": rewritten_query,
        "steps": ["query_rewriter"],
    }


def retrieve_node(state: AgenticRagState) -> dict[str, Any]:
    query = state.get("rewritten_query") or state["query"]

    result = hybrid_search_knowledge(
        query=query,
        top_k=state.get("top_k", 3),
        source_filter=state.get("source_filter"),
        max_chars=state.get("max_chars", DEFAULT_MAX_CHARS),
        embedding_dim=state.get("embedding_dim", DEFAULT_EMBEDDING_DIM),
        keyword_weight=state.get("keyword_weight", 0.6),
        vector_weight=state.get("vector_weight", 0.4),
    )

    return {
        "retrieval_results": result["results"],
        "steps": ["hybrid_retrieve"],
    }


def relevance_grade_node(state: AgenticRagState) -> dict[str, Any]:
    results = state.get("retrieval_results", [])

    if not results:
        return {
            "relevance_score": 0.0,
            "citations": [],
            "steps": ["relevance_grade"],
        }

    top_result = results[0]
    relevance_score = float(top_result.get("hybrid_score", 0.0))

    citations = [
        item["chunk_id"]
        for item in results
        if item.get("hybrid_score", 0.0) > 0
    ]

    return {
        "relevance_score": relevance_score,
        "citations": citations,
        "steps": ["relevance_grade"],
    }


def answer_node(state: AgenticRagState) -> dict[str, Any]:
    results = state.get("retrieval_results", [])

    if not results or state.get("relevance_score", 0.0) <= 0:
        final_answer = "未找到足够相关的知识库内容，暂时无法基于知识库回答。"
    else:
        top_result = results[0]
        final_answer = (
            "根据混合检索结果：\n"
            f"{top_result['content']}\n\n"
            f"引用来源：{top_result['chunk_id']}"
        )

    return {
        "final_answer": final_answer,
        "steps": ["answer_with_citations"],
    }


def direct_answer_node(state: AgenticRagState) -> dict[str, Any]:
    final_answer = (
        "这是一个普通对话问题，当前 Agentic RAG 判断不需要检索知识库。"
    )

    return {
        "rewritten_query": state["query"],
        "retrieval_results": [],
        "relevance_score": 0.0,
        "citations": [],
        "final_answer": final_answer,
        "steps": ["direct_answer"],
    }


def build_agentic_rag_graph():
    graph = StateGraph(AgenticRagState)

    graph.add_node("query_analyzer", query_analyzer_node)
    graph.add_node("query_rewriter", query_rewriter_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("relevance_grade", relevance_grade_node)
    graph.add_node("answer", answer_node)
    graph.add_node("direct_answer", direct_answer_node)

    graph.add_edge(START, "query_analyzer")

    graph.add_conditional_edges(
        "query_analyzer",
        should_retrieve,
        {
            "retrieve": "query_rewriter",
            "direct": "direct_answer",
        },
    )

    graph.add_edge("query_rewriter", "retrieve")
    graph.add_edge("retrieve", "relevance_grade")
    graph.add_edge("relevance_grade", "answer")
    graph.add_edge("answer", END)
    graph.add_edge("direct_answer", END)

    return graph.compile()


agentic_rag_graph = build_agentic_rag_graph()


def invoke_agentic_rag(
        query: str,
        top_k: int = 3,
        source_filter: str | None = None,
        max_chars: int = DEFAULT_MAX_CHARS,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        keyword_weight: float = 0.6,
        vector_weight: float = 0.4,
) -> dict[str, Any]:
    initial_state: AgenticRagState = {
        "query": query,
        "top_k": top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "steps": [],
    }

    result = agentic_rag_graph.invoke(initial_state)

    return {
        "query": result["query"],
        "rewritten_query": result.get("rewritten_query", result["query"]),
        "retrieval_needed": result.get("retrieval_needed", False),
        "relevance_score": result.get("relevance_score", 0.0),
        "citations": result.get("citations", []),
        "retrieval_results": result.get("retrieval_results", []),
        "final_answer": result.get("final_answer", ""),
        "steps": result.get("steps", []),
    }