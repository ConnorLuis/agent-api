def test_graph_ingest_debug_endpoint_defaults_to_dry_run(client):
    trace_id = "day44-graph-ingest-dry-run-001"

    response = client.post(
        "/graph/ingest-debug",
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
    assert data["dry_run"] is True
    assert data["apply_schema"] is True

    assert data["execution"]["ok"] is None
    assert data["execution"]["status"] == "dry_run"

    assert data["extraction_counts"]["documents"] == 1
    assert data["extraction_counts"]["chunks"] >= 1
    assert data["extraction_counts"]["entities"] >= 1

    assert data["plan"]["node_counts"]["Document"] == 1
    assert data["plan"]["node_counts"]["Chunk"] == data["extraction_counts"]["chunks"]
    assert data["plan"]["node_counts"]["Entity"] == data["extraction_counts"]["entities"]


def test_graph_ingest_debug_endpoint_can_disable_related_edges(client):
    response = client.post(
        "/graph/ingest-debug",
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
            "include_related_entities": False,
            "dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["include_related_entities"] is False
    assert "RELATED_TO" not in data["extraction_counts"]["relation_types"]
    assert "RELATED_TO" not in data["plan"]["relationship_counts"]
    assert data["execution"]["status"] == "dry_run"


def test_graph_ingest_debug_endpoint_can_skip_schema_in_plan(client):
    response = client.post(
        "/graph/ingest-debug",
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
            "include_related_entities": True,
            "dry_run": True,
            "apply_schema": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["apply_schema"] is False
    assert data["plan"]["schema_statement_count"] == 0
    assert data["plan"]["schema_statements"] == []
    assert data["execution"]["status"] == "dry_run"
