def test_agentic_rag_graph_fusion_backend_is_ci_safe(client):
    trace_id = "day47-agentic-rag-graph-fusion-debug-001"

    response = client.post(
        "/rag/agentic-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 和 LangGraph 有什么关系？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "retrieval_backend": "graph_fusion",
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["retrieval_backend"] == "graph_fusion"
    assert "graph_fusion_retrieve" in data["steps"]

    assert data["retrieval_needed"] is True
    assert len(data["retrieval_results"]) >= 1
    assert len(data["citations"]) >= 1
    assert data["final_answer"]

    metadata = data["retrieval_metadata"]

    assert metadata["retrieval_backend"] == "graph_fusion"
    assert metadata["graph_dry_run"] is True
    assert metadata["graph_retrieval"]["status"] == "dry_run"
    assert metadata["vector_retrieval"]["result_count"] >= 1
    assert metadata["fusion"]["result_count"] >= 1

    first_result = data["retrieval_results"][0]

    assert "fusion_score" in first_result
    assert "graph_score" in first_result
    assert "vector_score" in first_result
    assert "retrieval_sources" in first_result


def test_agentic_rag_default_backend_remains_hybrid(client):
    response = client.post(
        "/rag/agentic-debug",
        json={
            "query": "RAG 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_backend"] == "hybrid"
    assert "hybrid_retrieve" in data["steps"]
    assert "graph_fusion_retrieve" not in data["steps"]


def test_agentic_rag_graph_fusion_backend_handles_no_graph_entity_match(client):
    response = client.post(
        "/rag/agentic-debug",
        json={
            "query": "请搜索知识库：今天天气怎么样？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "retrieval_backend": "graph_fusion",
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_backend"] == "graph_fusion"

    metadata = data["retrieval_metadata"]

    assert metadata["graph_dry_run"] is True
    assert metadata["graph_retrieval"]["status"] in {
        "dry_run",
        "no_query_entity_match",
    }
    assert "fusion" in metadata
