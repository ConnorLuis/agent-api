from src.app.rag.agentic_graph import invoke_agentic_rag


def test_agentic_rag_retrieval_path_returns_citations():
    result = invoke_agentic_rag(
        query="请搜索知识库：LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
    )

    assert result["query"] == "请搜索知识库：LangGraph 是什么？"
    assert result["rewritten_query"] == "LangGraph 是什么？"
    assert result["retrieval_needed"] is True
    assert result["relevance_score"] > 0
    assert len(result["citations"]) >= 1
    assert len(result["retrieval_results"]) >= 1
    assert result["final_answer"].startswith("根据混合检索结果")
    assert result["steps"] == [
        "query_analyzer",
        "query_rewriter",
        "hybrid_retrieve",
        "relevance_grade",
        "answer_with_citations",
    ]

    first = result["retrieval_results"][0]

    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert "langgraph" in first["matched_terms"]


def test_agentic_rag_direct_path_skips_retrieval():
    result = invoke_agentic_rag(
        query="你好，介绍一下你自己",
        top_k=2,
        source_filter="agent_basics",
    )

    assert result["query"] == "你好，介绍一下你自己"
    assert result["rewritten_query"] == "你好，介绍一下你自己"
    assert result["retrieval_needed"] is False
    assert result["relevance_score"] == 0.0
    assert result["citations"] == []
    assert result["retrieval_results"] == []
    assert result["steps"] == ["query_analyzer", "direct_answer"]
    assert "不需要检索知识库" in result["final_answer"]


def test_rag_agentic_debug_endpoint(client):
    trace_id = "rag-agentic-debug-001"

    response = client.post(
        "/rag/agentic-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "请搜索知识库：LangGraph 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["query"] == "请搜索知识库：LangGraph 是什么？"
    assert data["rewritten_query"] == "LangGraph 是什么？"
    assert data["retrieval_needed"] is True
    assert data["relevance_score"] > 0
    assert data["trace_id"] == trace_id
    assert len(data["citations"]) >= 1
    assert len(data["retrieval_results"]) >= 1
    assert data["final_answer"].startswith("根据混合检索结果")
    assert data["steps"] == [
        "query_analyzer",
        "query_rewriter",
        "hybrid_retrieve",
        "relevance_grade",
        "answer_with_citations",
    ]

    first = data["retrieval_results"][0]

    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert "langgraph" in first["matched_terms"]