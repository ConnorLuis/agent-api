from pathlib import Path

from src.app.rag.vector_store import (
    build_vector_store_index,
    debug_vector_store_search,
    query_vector_store,
)


def test_build_and_query_vector_store(tmp_path):
    db_path = Path(tmp_path) / "rag_vector_store.sqlite"

    index_stats = build_vector_store_index(
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        rebuild_index=True,
        db_path=db_path,
    )

    assert index_stats["source_filter"] == "agent_basics"
    assert index_stats["max_chars"] == 300
    assert index_stats["embedding_dim"] == 64
    assert index_stats["rebuild_index"] is True
    assert index_stats["loaded_chunks"] == 2
    assert index_stats["inserted_count"] == 2
    assert index_stats["stored_count"] == 2

    result = query_vector_store(
        query="LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        db_path=db_path,
    )

    assert result["query"] == "LangGraph 是什么？"
    assert result["top_k"] == 2
    assert result["source_filter"] == "agent_basics"
    assert result["embedding_dim"] == 64
    assert result["total_indexed_chunks"] == 2
    assert len(result["results"]) == 2

    first = result["results"][0]

    assert first["rank"] == 1
    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["score"] > 0
    assert first["content"]
    assert first["preview"]
    assert first["content_length"] > 0


def test_debug_vector_store_search_rebuilds_index(tmp_path):
    db_path = Path(tmp_path) / "rag_vector_store.sqlite"

    result = debug_vector_store_search(
        query="RAG 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        rebuild_index=True,
        db_path=db_path,
    )

    assert result["query"] == "RAG 是什么？"
    assert result["top_k"] == 2
    assert result["source_filter"] == "agent_basics"
    assert result["embedding_dim"] == 64
    assert result["rebuild_index"] is True
    assert result["total_indexed_chunks"] == 2
    assert result["index_stats"]["loaded_chunks"] == 2
    assert result["index_stats"]["inserted_count"] == 2
    assert result["index_stats"]["stored_count"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["score"] > 0


def test_rag_vector_store_debug_endpoint_writes_trace(client):
    trace_id = "rag-vector-store-debug-001"

    response = client.post(
        "/rag/vector-store-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "LangGraph 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "rebuild_index": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["query"] == "LangGraph 是什么？"
    assert data["top_k"] == 2
    assert data["source_filter"] == "agent_basics"
    assert data["embedding_dim"] == 64
    assert data["rebuild_index"] is True
    assert data["total_indexed_chunks"] == 2
    assert data["index_stats"]["loaded_chunks"] == 2
    assert data["index_stats"]["inserted_count"] == 2
    assert data["index_stats"]["stored_count"] == 2
    assert len(data["results"]) == 2

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_vector_store_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["query"] == "LangGraph 是什么？"
    assert payload["top_k"] == 2
    assert payload["source_filter"] == "agent_basics"
    assert payload["total_indexed_chunks"] == 2
    assert payload["results_count"] == 2
    assert payload["index_stats"]["stored_count"] == 2