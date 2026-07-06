from src.app.graph.neo4j_client import get_neo4j_settings


def test_neo4j_settings_are_env_overridable(monkeypatch):
    monkeypatch.setenv("NEO4J_ENABLED", "true")
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j-test:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "test-user")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("NEO4J_DATABASE", "test-db")

    settings = get_neo4j_settings()

    assert settings.enabled is True
    assert settings.uri == "bolt://neo4j-test:7687"
    assert settings.username == "test-user"
    assert settings.password == "test-password"
    assert settings.database == "test-db"

    public = settings.safe_public_dict()

    assert public["uri"] == "bolt://neo4j-test:7687"
    assert public["username"] == "test-user"
    assert public["database"] == "test-db"
    assert public["password_configured"] is True
    assert "password" not in public


def test_graph_schema_debug_endpoint(client):
    trace_id = "day42-graph-schema-debug-001"

    response = client.get(
        "/graph/schema-debug",
        headers={"x-trace-id": trace_id},
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["schema_version"] == "day42_graph_schema_v1"
    assert "Document" in data["node_labels"]
    assert "Chunk" in data["node_labels"]
    assert "Entity" in data["node_labels"]
    assert "HAS_CHUNK" in data["relation_types"]
    assert "MENTIONS" in data["relation_types"]


def test_graph_health_debug_skips_connection_by_default(client):
    trace_id = "day42-graph-health-debug-001"

    response = client.get(
        "/graph/health-debug",
        headers={"x-trace-id": trace_id},
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["connection_check_requested"] is False
    assert data["connection"]["ok"] is None
    assert data["connection"]["status"] == "skipped"
    assert data["connection"]["settings"]["uri"] == "bolt://localhost:7687"
    assert data["connection"]["settings"]["database"] == "neo4j"
    assert "password" not in data["connection"]["settings"]
