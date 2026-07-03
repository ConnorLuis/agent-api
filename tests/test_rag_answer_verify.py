from src.app.rag.answer_verifier import verify_agentic_rag_answer


def test_verify_agentic_rag_answer_retrieval_path():
    result = verify_agentic_rag_answer(
        query="请搜索知识库：LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
    )

    verification = result["verification"]

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

    assert verification["verification_mode"] == "retrieval"
    assert verification["answer_supported"] is True
    assert verification["verification_pass"] is True
    assert verification["confidence"] == "high"
    assert verification["answer_has_citation"] is True
    assert verification["citation_coverage_pass"] is True
    assert verification["unsupported_citations"] == []
    assert "langgraph" in verification["grounding_terms"]
    assert "langgraph" in verification["matched_grounding_terms"]
    assert verification["risk_flags"] == []


def test_verify_agentic_rag_answer_direct_path():
    result = verify_agentic_rag_answer(
        query="你好，介绍一下你自己",
        top_k=2,
        source_filter="agent_basics",
    )

    verification = result["verification"]

    assert result["query"] == "你好，介绍一下你自己"
    assert result["rewritten_query"] == "你好，介绍一下你自己"
    assert result["retrieval_needed"] is False
    assert result["relevance_score"] == 0.0
    assert result["citations"] == []
    assert result["retrieval_results"] == []
    assert result["steps"] == ["query_analyzer", "direct_answer"]
    assert "不需要检索知识库" in result["final_answer"]

    assert verification["verification_mode"] == "direct"
    assert verification["answer_supported"] is True
    assert verification["verification_pass"] is True
    assert verification["confidence"] == "high"
    assert verification["answer_has_citation"] is False
    assert verification["citation_coverage_pass"] is True
    assert verification["cited_in_answer"] == []
    assert verification["unsupported_citations"] == []
    assert verification["grounding_terms"] == []
    assert verification["matched_grounding_terms"] == []
    assert verification["risk_flags"] == []


def test_rag_answer_verify_debug_endpoint_writes_trace(client):
    trace_id = "rag-answer-verify-debug-001"

    response = client.post(
        "/rag/answer-verify-debug",
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
    verification = data["verification"]

    assert data["trace_id"] == trace_id
    assert data["retrieval_needed"] is True
    assert verification["verification_mode"] == "retrieval"
    assert verification["answer_supported"] is True
    assert verification["verification_pass"] is True
    assert verification["confidence"] == "high"
    assert "langgraph" in verification["matched_grounding_terms"]

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_answer_verify_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["query"] == "请搜索知识库：LangGraph 是什么？"
    assert payload["rewritten_query"] == "LangGraph 是什么？"
    assert payload["retrieval_needed"] is True
    assert payload["verification"]["verification_pass"] is True
    assert payload["verification"]["confidence"] == "high"
    assert "langgraph" in payload["verification"]["matched_grounding_terms"]