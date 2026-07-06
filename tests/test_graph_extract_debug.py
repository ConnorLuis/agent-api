def test_graph_extract_debug_endpoint_returns_extraction_payload(client):
    trace_id = "day43-graph-extract-debug-001"

    response = client.post(
        "/graph/extract-debug",
        headers={"x-trace-id": trace_id},
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
            "include_related_entities": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["source_filter"] == "agent_basics"
    assert data["max_chars"] == 300
    assert data["include_related_entities"] is True

    assert data["counts"]["documents"] == len(data["documents"])
    assert data["counts"]["chunks"] == len(data["chunks"])
    assert data["counts"]["entities"] == len(data["entities"])
    assert data["counts"]["relations"] == len(data["relations"])

    entity_names = {entity["name"] for entity in data["entities"]}
    relation_types = {relation["type"] for relation in data["relations"]}

    assert "Agent" in entity_names
    assert "RAG" in entity_names
    assert "LangGraph" in entity_names

    assert "HAS_CHUNK" in relation_types
    assert "MENTIONS" in relation_types
    assert "RELATED_TO" in relation_types


def test_graph_extract_debug_endpoint_does_not_require_neo4j(client):
    response = client.post(
        "/graph/extract-debug",
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
            "include_related_entities": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    relation_types = {relation["type"] for relation in data["relations"]}

    assert data["counts"]["documents"] >= 1
    assert data["counts"]["chunks"] >= 1
    assert data["counts"]["entities"] >= 1
    assert "MENTIONS" in relation_types
    assert "RELATED_TO" not in relation_types
    assert "connection" not in data
