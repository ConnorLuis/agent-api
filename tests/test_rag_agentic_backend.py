from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.chroma_store import build_chroma_collection_name
from src.app.rag.retrieval_backend import retrieve_agentic_context



from src.app.rag.chunking import load_knowledge_chunks

EXPECTED_AGENT_BASICS_CHUNKS = len(
    load_knowledge_chunks(source_filter="agent_basics", max_chars=300)
)

def test_chroma_collection_name_uses_short_hash_and_dimension():
    name_64 = build_chroma_collection_name(
        source_filter="agent_basics",
        embedding_provider="deterministic",
        embedding_model="deterministic-hash",
        embedding_dim=64,
    )

    name_128 = build_chroma_collection_name(
        source_filter="agent_basics",
        embedding_provider="deterministic",
        embedding_model="deterministic-hash",
        embedding_dim=128,
    )

    assert len(name_64) <= 63
    assert len(name_128) <= 63
    assert "d64" in name_64
    assert "d128" in name_128
    assert name_64 != name_128


def test_retrieve_agentic_context_supports_chroma_backend():
    result = retrieve_agentic_context(
        query="RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        retrieval_backend="chroma",
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["retrieval_backend"] == "chroma"
    assert len(result["results"]) == 2
    assert result["metadata"]["retrieval_backend"] == "chroma"
    assert result["metadata"]["total_indexed_chunks"] == EXPECTED_AGENT_BASICS_CHUNKS
    assert result["metadata"]["embedding_provider"] == "deterministic"
    assert result["metadata"]["embedding_model"] == "deterministic-hash"

    first = result["results"][0]

    assert first["retrieval_backend"] == "chroma"
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["score"] > 0
    assert first["distance"] >= 0


def test_invoke_agentic_rag_with_chroma_backend():
    result = invoke_agentic_rag(
        query="请搜索知识库：RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        retrieval_backend="chroma",
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["retrieval_backend"] == "chroma"
    assert result["retrieval_needed"] is True
    assert "chroma_retrieve" in result["steps"]
    assert result["relevance_score"] > 0
    assert len(result["retrieval_results"]) == 2
    assert len(result["citations"]) >= 1
    assert result["retrieval_metadata"]["retrieval_backend"] == "chroma"
    assert result["retrieval_metadata"]["total_indexed_chunks"] == EXPECTED_AGENT_BASICS_CHUNKS


def test_rag_agentic_debug_endpoint_supports_chroma_backend(client):
    trace_id = "rag-agentic-chroma-backend-001"

    response = client.post(
        "/rag/agentic-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "请搜索知识库：RAG 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "retrieval_backend": "chroma",
            "embedding_provider": "deterministic",
            "rebuild_index": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["retrieval_backend"] == "chroma"
    assert data["retrieval_needed"] is True
    assert "chroma_retrieve" in data["steps"]
    assert len(data["retrieval_results"]) == 2
    assert data["retrieval_metadata"]["retrieval_backend"] == "chroma"
    assert data["retrieval_metadata"]["total_indexed_chunks"] == EXPECTED_AGENT_BASICS_CHUNKS

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_agentic_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["query"] == "请搜索知识库：RAG 是什么？"
    assert payload["retrieval_backend"] == "chroma"
    assert payload["retrieval_metadata"]["retrieval_backend"] == "chroma"
    assert payload["retrieval_metadata"]["total_indexed_chunks"] == EXPECTED_AGENT_BASICS_CHUNKS
    assert payload["retrieval_results_count"] == 2
