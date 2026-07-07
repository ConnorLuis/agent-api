def test_graph_retrieval_debug_endpoint_defaults_to_dry_run(client):
    trace_id = "day45-graph-retrieval-dry-run-001"

    response = client.post(
        "/graph/retrieval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
            "chunk_limit": 5,
            "related_entity_limit": 10,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["query"] == "RAG 是什么？"
    assert data["dry_run"] is True
    assert data["execution"]["status"] == "dry_run"
    assert data["execution"]["ok"] is None

    assert "Entity:concept:rag" in data["plan"]["matched_entity_ids"]
    assert data["execution"]["chunks"] == []
    assert data["execution"]["related_entities"] == []


def test_graph_retrieval_debug_endpoint_matches_multiple_entities(client):
    response = client.post(
        "/graph/retrieval-debug",
        json={
            "query": "RAG 和 LangGraph 有什么关系？",
            "chunk_limit": 5,
            "related_entity_limit": 10,
            "dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()
    names = {match["name"] for match in data["query_entity_matches"]}

    assert "RAG" in names
    assert "LangGraph" in names
    assert "Entity:concept:rag" in data["plan"]["matched_entity_ids"]
    assert "Entity:framework:langgraph" in data["plan"]["matched_entity_ids"]
    assert data["execution"]["status"] == "dry_run"


def test_graph_retrieval_debug_endpoint_handles_no_entity_match(client):
    response = client.post(
        "/graph/retrieval-debug",
        json={
            "query": "今天天气怎么样？",
            "dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query_entity_matches"] == []
    assert data["plan"]["matched_entity_ids"] == []
    assert data["execution"]["ok"] is True
    assert data["execution"]["status"] == "no_query_entity_match"
    assert data["execution"]["counts"]["chunks"] == 0
    assert data["execution"]["counts"]["related_entities"] == 0
