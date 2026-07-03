from src.app.rag.hybrid import hybrid_search_knowledge


def test_hybrid_search_knowledge_returns_ranked_chunks():
    result = hybrid_search_knowledge(
        query="RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
    )

    assert result["query"] == "RAG 是什么？"
    assert result["top_k"] == 2
    assert result["source_filter"] == "agent_basics"
    assert result["max_chars"] == 300
    assert result["embedding_dim"] == 64
    assert result["keyword_weight"] == 0.6
    assert result["vector_weight"] == 0.4
    assert result["total_chunks"] >= 1
    assert len(result["results"]) <= 2
    assert len(result["results"]) >= 1

    first = result["results"][0]

    assert first["rank"] == 1
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["hybrid_score"] > 0
    assert first["keyword_score"] > 0
    assert first["vector_score"] > 0
    assert first["content"]
    assert first["preview"]
    assert "rag" in first["matched_terms"]
    assert first["content_length"] > 0


def test_hybrid_search_normalizes_zero_weights():
    result = hybrid_search_knowledge(
        query="RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0,
        vector_weight=0,
    )

    assert result["keyword_weight"] == 0.5
    assert result["vector_weight"] == 0.5
    assert result["total_chunks"] >= 1
    assert len(result["results"]) >= 1


def test_rag_hybrid_search_debug_endpoint(client):
    trace_id = "rag-hybrid-search-debug-001"

    response = client.post(
        "/rag/hybrid-search-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
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

    assert data["query"] == "RAG 是什么？"
    assert data["top_k"] == 2
    assert data["source_filter"] == "agent_basics"
    assert data["max_chars"] == 300
    assert data["embedding_dim"] == 64
    assert data["keyword_weight"] == 0.6
    assert data["vector_weight"] == 0.4
    assert data["trace_id"] == trace_id
    assert data["total_chunks"] >= 1
    assert len(data["results"]) <= 2
    assert len(data["results"]) >= 1

    first = data["results"][0]

    assert first["rank"] == 1
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["hybrid_score"] > 0
    assert first["keyword_score"] > 0
    assert first["vector_score"] > 0
    assert first["content"]
    assert first["preview"]
    assert "rag" in first["matched_terms"]
    assert first["content_length"] > 0