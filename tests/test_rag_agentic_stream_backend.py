def test_rag_agentic_stream_supports_chroma_backend(client):
    trace_id = "rag-agentic-stream-chroma-backend-001"

    response = client.post(
        "/rag/agentic-stream",
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

    body = response.text

    assert "event: metadata" in body
    assert "event: retrieval" in body
    assert "event: final" in body
    assert '"retrieval_backend":"chroma"' in body or '"retrieval_backend": "chroma"' in body
    assert "chroma_retrieve" in body

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_agentic_stream"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["retrieval_backend"] == "chroma"
    assert payload["retrieval_metadata"]["retrieval_backend"] == "chroma"
    assert "chroma_retrieve" in payload["steps"]