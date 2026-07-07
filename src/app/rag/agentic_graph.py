import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM
from src.app.rag.retrieval_backend import (
    DEFAULT_RETRIEVAL_BACKEND,
    retrieve_agentic_context,
)
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER


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

    retrieval_backend: str
    retrieval_metadata: dict[str, Any]
    embedding_provider: str
    embedding_model: str | None
    rebuild_index: bool

    graph_dry_run: bool
    fusion_graph_weight: float
    fusion_vector_weight: float
    graph_chunk_limit: int
    related_entity_limit: int


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


def retrieve_node(state: AgenticRagState) -> dict:
    rewritten_query = state.get("rewritten_query") or state["query"]

    retrieval_result = retrieve_agentic_context(
        query=rewritten_query,
        top_k=state["top_k"],
        source_filter=state["source_filter"],
        max_chars=state["max_chars"],
        embedding_dim=state["embedding_dim"],
        keyword_weight=state["keyword_weight"],
        vector_weight=state["vector_weight"],
        retrieval_backend=state["retrieval_backend"],
        embedding_provider=state.get("embedding_provider", "deterministic"),
        embedding_model=state.get("embedding_model"),
        rebuild_index=state.get("rebuild_index", False),

        # Day47 GraphRAG fusion options.
        graph_dry_run=state.get("graph_dry_run", True),
        fusion_graph_weight=state.get("fusion_graph_weight", 0.5),
        fusion_vector_weight=state.get("fusion_vector_weight", 0.5),
        graph_chunk_limit=state.get("graph_chunk_limit", 5),
        related_entity_limit=state.get("related_entity_limit", 10),
    )

    backend = retrieval_result["retrieval_backend"]

    if backend == "chroma":
        step_name = "chroma_retrieve"
    elif backend == "chroma_rerank":
        step_name = "chroma_rerank_retrieve"
    elif backend == "graph_fusion":
        step_name = "graph_fusion_retrieve"
    else:
        step_name = "hybrid_retrieve"

    return {
        "retrieval_results": retrieval_result["results"],
        "retrieval_backend": backend,
        "retrieval_metadata": retrieval_result.get(
            "metadata",
            retrieval_result.get("retrieval_metadata", {}),
        ),
        "steps": [step_name],
    }


def relevance_grade_node(state: AgenticRagState) -> dict[str, Any]:
    retrieval_results = state.get("retrieval_results", [])

    scores = [
        float(result.get("hybrid_score", result.get("score", 0.0)))
        for result in retrieval_results
    ]

    relevance_score = round(
        max(scores, default=0.0),
        6,
    )

    return {
        "relevance_score": relevance_score,
        "steps": ["relevance_grade"],
    }


def answer_node(state: AgenticRagState) -> dict[str, Any]:
    results = state.get("retrieval_results", [])
    retrieval_backend = state.get("retrieval_backend", DEFAULT_RETRIEVAL_BACKEND)

    if not results or state.get("relevance_score", 0.0) <= 0:
        final_answer = "未找到足够相关的知识库内容，暂时无法基于知识库回答。"
        citations: list[str] = []
    else:
        top_result = results[0]
        top_chunk_id = str(top_result["chunk_id"])

        if retrieval_backend == "chroma":
            answer_prefix = "根据 Chroma 向量检索结果："
        elif retrieval_backend == "chroma_rerank":
            answer_prefix = "根据 Chroma 向量检索 + rerank 结果："
        else:
            answer_prefix = "根据混合检索结果："

        final_answer = (
            f"{answer_prefix}\n"
            f"{top_result['content']}\n\n"
            f"引用来源：{top_chunk_id}"
        )

        citations = [top_chunk_id]

    return {
        "final_answer": final_answer,
        "citations": citations,
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
        retrieval_backend: str = DEFAULT_RETRIEVAL_BACKEND,
        embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
        embedding_model: str | None = None,
        rebuild_index: bool = True,
        graph_dry_run: bool = True,
        fusion_graph_weight: float = 0.5,
        fusion_vector_weight: float = 0.5,
        graph_chunk_limit: int = 5,
        related_entity_limit: int = 10,
) -> dict[str, Any]:
    initial_state: AgenticRagState = {
        "query": query,
        "top_k": top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "retrieval_backend": retrieval_backend,
        "retrieval_metadata": {},
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "rebuild_index": rebuild_index,
        "steps": [],
        "graph_dry_run": graph_dry_run,
        "fusion_graph_weight": fusion_graph_weight,
        "fusion_vector_weight": fusion_vector_weight,
        "graph_chunk_limit": graph_chunk_limit,
        "related_entity_limit": related_entity_limit,
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
        "retrieval_backend": result.get("retrieval_backend", retrieval_backend),
        "retrieval_metadata": result.get("retrieval_metadata", {}),
        "steps": result.get("steps", []),
    }