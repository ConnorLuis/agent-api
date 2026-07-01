def test_rag_search_debug_returns_explainable_results(client):
    trace_id = "rag-search-debug-001"

    response = client.post(
        "/rag/search-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
            "k": 2,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["query"] == "RAG 是什么？"
    assert data["normalized_query"] == "rag 是什么？"
    assert data["k"] == 2
    assert data["trace_id"] == trace_id

    assert len(data["results"]) >= 1

    first = data["results"][0]

    assert first["rank"] == 1
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["score"] >= 1
    assert "RAG" in first["content"] or "rag" in first["content"].lower()
    assert first["preview"]
    assert "rag" in first["matched_terms"]
    assert first["content_length"] > 0


def test_rag_search_debug_respects_k(client):
    response = client.post(
        "/rag/search-debug",
        json={
            "query": "RAG 是什么？",
            "k": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["k"] == 1
    assert len(data["results"]) <= 1

    if data["results"]:
        assert data["results"][0]["rank"] == 1


def test_rag_search_debug_langgraph_matched_terms(client):
    trace_id = "rag-search-debug-langgraph-001"

    response = client.post(
        "/rag/search-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "LangGraph 是什么？",
            "k": 2,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert len(data["results"]) >= 1

    first = data["results"][0]

    assert first["source"] == "knowledge/agent_basics.md"
    assert "langgraph" in first["matched_terms"]
    assert first["content_length"] > 0