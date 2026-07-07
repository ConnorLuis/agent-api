from src.app.evaluation.rag_eval import compare_rag_retrieval_backends
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.reranker import rerank_retrieval_results
from src.app.rag.retrieval_backend import retrieve_agentic_context


def test_rerank_retrieval_results_promotes_keyword_match():
    results = [
        {
            "rank": 1,
            "chunk_id": "rag_chunk",
            "content": "RAG 是 Retrieval-Augmented Generation。",
            "score": 0.40,
        },
        {
            "rank": 2,
            "chunk_id": "langgraph_chunk",
            "content": "LangGraph 使用图结构表达 Agent 工作流。",
            "score": 0.38,
        },
    ]

    reranked = rerank_retrieval_results(
        query="LangGraph 是什么？",
        results=results,
    )

    assert reranked[0]["chunk_id"] == "langgraph_chunk"
    assert reranked[0]["original_rank"] == 2
    assert "langgraph" in reranked[0]["rerank_matched_terms"]
    assert reranked[0]["rerank_score"] > reranked[1]["rerank_score"]


def test_retrieve_agentic_context_supports_chroma_rerank_backend():
    result = retrieve_agentic_context(
        query="LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        retrieval_backend="chroma_rerank",
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["retrieval_backend"] == "chroma_rerank"
    assert result["metadata"]["retrieval_backend"] == "chroma_rerank"
    assert result["metadata"]["base_backend"] == "chroma"
    assert result["metadata"]["rerank_enabled"] is True

    first = result["results"][0]

    assert first["chunk_id"] == "knowledge/agent_basics.md::chunk-1"
    assert first["retrieval_backend"] == "chroma_rerank"
    assert first["original_rank"] >= 1
    assert first["rerank_score"] > 0
    assert "langgraph" in first["rerank_matched_terms"]


def test_invoke_agentic_rag_with_chroma_rerank_backend():
    result = invoke_agentic_rag(
        query="请搜索知识库：LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        retrieval_backend="chroma_rerank",
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["retrieval_backend"] == "chroma_rerank"
    assert "chroma_rerank_retrieve" in result["steps"]
    assert result["citations"][0] == "knowledge/agent_basics.md::chunk-1"
    assert result["relevance_score"] > 0
    assert "LangGraph" in result["final_answer"]
    assert "图结构" in result["final_answer"]


def test_backend_eval_can_compare_chroma_and_chroma_rerank():
    result = compare_rag_retrieval_backends(
        backends=["chroma", "chroma_rerank"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    chroma_result = result["results"][0]
    rerank_result = result["results"][1]

    assert chroma_result["retrieval_backend"] == "chroma"
    assert rerank_result["retrieval_backend"] == "chroma_rerank"
    assert (
        rerank_result["metrics"]["pass_rate"]
        >= chroma_result["metrics"]["pass_rate"]
    )
    assert result["metric_deltas"]["baseline_backend"] == "chroma"
    assert result["metric_deltas"]["comparison_backend"] == "chroma_rerank"