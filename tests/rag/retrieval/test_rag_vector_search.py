from src.app.rag.vector_index import (
    build_deterministic_embedding,
    vector_search_knowledge,
)


def test_build_deterministic_embedding_is_stable():
    first = build_deterministic_embedding(
        text="RAG 是什么？",
        embedding_dim=16,
    )
    second = build_deterministic_embedding(
        text="RAG 是什么？",
        embedding_dim=16,
    )

    assert first == second
    assert len(first) == 16
    assert any(value > 0 for value in first)


def test_vector_search_knowledge_returns_ranked_chunks():
    result = vector_search_knowledge(
        query="RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
    )

    assert result["query"] == "RAG 是什么？"
    assert result["top_k"] == 2
    assert result["source_filter"] == "agent_basics"
    assert result["max_chars"] == 300
    assert result["embedding_dim"] == 64
    assert result["total_chunks"] >= 1
    assert len(result["results"]) <= 2
    assert len(result["results"]) >= 1

    first = result["results"][0]

    assert first["rank"] == 1
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["score"] > 0
    assert first["content"]
    assert first["preview"]
    assert "rag" in first["matched_terms"]
    assert first["content_length"] > 0


def test_rag_vector_search_debug_endpoint(client):
    trace_id = "rag-vector-search-debug-001"

    response = client.post(
        "/rag/vector-search-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["query"] == "RAG 是什么？"
    assert data["top_k"] == 2
    assert data["source_filter"] == "agent_basics"
    assert data["max_chars"] == 300
    assert data["embedding_dim"] == 64
    assert data["trace_id"] == trace_id
    assert data["total_chunks"] >= 1
    assert len(data["results"]) <= 2
    assert len(data["results"]) >= 1

    first = data["results"][0]

    assert first["rank"] == 1
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["score"] > 0
    assert first["content"]
    assert first["preview"]
    assert "rag" in first["matched_terms"]
    assert first["content_length"] > 0