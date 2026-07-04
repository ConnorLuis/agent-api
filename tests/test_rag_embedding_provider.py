from src.app.rag.embedding_provider import (
    debug_embeddings,
    get_embedding_provider,
)


def test_deterministic_embedding_provider_returns_stable_embedding():
    provider = get_embedding_provider(provider="deterministic")

    first = provider.embed_text(
        text="LangGraph 是什么？",
        embedding_dim=64,
    )
    second = provider.embed_text(
        text="LangGraph 是什么？",
        embedding_dim=64,
    )

    assert provider.provider == "deterministic"
    assert provider.model == "deterministic-hash"
    assert len(first) == 64
    assert first == second


def test_debug_embeddings_with_documents():
    result = debug_embeddings(
        query="LangGraph 是什么？",
        documents=[
            "LangGraph 是一个适合构建 Agent 工作流的框架。",
            "RAG 是 Retrieval-Augmented Generation。",
        ],
        provider="deterministic",
        embedding_dim=64,
    )

    assert result["query"] == "LangGraph 是什么？"
    assert result["provider"] == "deterministic"
    assert result["model"] == "deterministic-hash"
    assert result["requested_embedding_dim"] == 64
    assert result["actual_embedding_dim"] == 64
    assert len(result["query_embedding_preview"]) == 8
    assert result["documents_count"] == 2
    assert len(result["documents"]) == 2

    for item in result["documents"]:
        assert item["embedding_dim"] == 64
        assert len(item["embedding_preview"]) == 8
        assert item["embedding_norm"] > 0


def test_rag_embedding_debug_endpoint_writes_trace(client):
    trace_id = "rag-embedding-debug-001"

    response = client.post(
        "/rag/embedding-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "LangGraph 是什么？",
            "documents": [
                "LangGraph 是一个适合构建 Agent 工作流的框架。",
                "RAG 是 Retrieval-Augmented Generation。",
            ],
            "provider": "deterministic",
            "embedding_dim": 64,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["provider"] == "deterministic"
    assert data["model"] == "deterministic-hash"
    assert data["requested_embedding_dim"] == 64
    assert data["actual_embedding_dim"] == 64
    assert data["documents_count"] == 2
    assert len(data["documents"]) == 2

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_embedding_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["query"] == "LangGraph 是什么？"
    assert payload["provider"] == "deterministic"
    assert payload["model"] == "deterministic-hash"
    assert payload["actual_embedding_dim"] == 64
    assert payload["documents_count"] == 2