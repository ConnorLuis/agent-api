from src.app.rag.agentic_streaming import stream_agentic_rag_events


def _collect_event_names(raw_body: str) -> list[str]:
    return [
        line.replace("event: ", "")
        for line in raw_body.splitlines()
        if line.startswith("event: ")
    ]


def test_stream_agentic_rag_events_retrieval_path():
    events = list(
        stream_agentic_rag_events(
            query="请搜索知识库：LangGraph 是什么？",
            trace_id="agentic-stream-unit-001",
            top_k=2,
            source_filter="agent_basics",
            max_chars=300,
            embedding_dim=64,
            keyword_weight=0.6,
            vector_weight=0.4,
        )
    )

    raw_body = "".join(events)
    event_names = _collect_event_names(raw_body)

    assert event_names == [
        "metadata",
        "decision",
        "rewrite",
        "retrieval",
        "relevance",
        "citation",
        "answer_chunk",
        "final",
        "done",
    ]

    assert '"retrieval_needed": true' in raw_body
    assert '"rewritten_query": "LangGraph 是什么？"' in raw_body
    assert '"relevance_score": 0.383914' in raw_body
    assert '"rag_agentic_stream"' not in raw_body
    assert "knowledge/agent_basics.md::chunk-1" in raw_body


def test_stream_agentic_rag_events_direct_path():
    events = list(
        stream_agentic_rag_events(
            query="你好，介绍一下你自己",
            trace_id="agentic-stream-unit-direct-001",
            top_k=2,
            source_filter="agent_basics",
        )
    )

    raw_body = "".join(events)
    event_names = _collect_event_names(raw_body)

    assert event_names == [
        "metadata",
        "decision",
        "answer_chunk",
        "final",
        "done",
    ]

    assert '"retrieval_needed": false' in raw_body
    assert '"citations": []' in raw_body
    assert '"retrieval_results": []' in raw_body
    assert "不需要检索知识库" in raw_body


def test_rag_agentic_stream_endpoint_writes_trace(client):
    trace_id = "rag-agentic-stream-endpoint-001"

    with client.stream(
        "POST",
        "/rag/agentic-stream",
        headers={"x-trace-id": trace_id},
        json={
            "query": "请搜索知识库：LangGraph 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["x-trace-id"] == trace_id
        raw_body = response.read().decode("utf-8")

    event_names = _collect_event_names(raw_body)

    assert event_names == [
        "metadata",
        "decision",
        "rewrite",
        "retrieval",
        "relevance",
        "citation",
        "answer_chunk",
        "final",
        "done",
    ]

    assert '"retrieval_needed": true' in raw_body
    assert '"rewritten_query": "LangGraph 是什么？"' in raw_body
    assert "knowledge/agent_basics.md::chunk-1" in raw_body

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

    assert payload["query"] == "请搜索知识库：LangGraph 是什么？"
    assert payload["rewritten_query"] == "LangGraph 是什么？"
    assert payload["retrieval_needed"] is True
    assert payload["relevance_score"] > 0
    assert payload["retrieval_results_count"] >= 1
    assert "query_analyzer" in payload["steps"]
    assert "answer_with_citations" in payload["steps"]