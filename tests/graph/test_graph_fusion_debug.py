def test_graph_fusion_debug_endpoint_defaults_to_graph_dry_run(client):
    trace_id = "day46-graph-fusion-dry-run-001"

    response = client.post(
        "/graph/fusion-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
            "top_k": 3,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["query"] == "RAG 是什么？"
    assert data["graph_dry_run"] is True
    assert data["graph_retrieval"]["status"] == "dry_run"
    assert data["vector_retrieval"]["result_count"] >= 1
    assert data["fusion"]["result_count"] >= 1
    assert data["fusion"]["strategy"] == "chunk_id_union_weighted_score"

    assert "Entity:concept:rag" in [
        item["entity_id"]
        for item in data["query_entity_matches"]
    ]


def test_graph_fusion_debug_endpoint_returns_ranked_fusion_results(client):
    response = client.post(
        "/graph/fusion-debug",
        json={
            "query": "LangGraph 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["top_k"] == 2
    assert len(data["results"]) <= 2

    if data["results"]:
        first = data["results"][0]
        assert first["rank"] == 1
        assert "fusion_score" in first
        assert "graph_score" in first
        assert "vector_score" in first
        assert "retrieval_sources" in first


def test_graph_fusion_debug_endpoint_handles_no_graph_entity_match(client):
    response = client.post(
        "/graph/fusion-debug",
        json={
            "query": "今天天气怎么样？",
            "top_k": 3,
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query_entity_matches"] == []
    assert data["graph_retrieval"]["status"] == "no_query_entity_match"
    assert data["vector_retrieval"]["result_count"] >= 0
    assert "results" in data
