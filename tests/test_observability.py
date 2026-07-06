from pathlib import Path

from src.app.observability.trace_store import (
    get_trace_events,
    list_recent_trace_ids,
    record_trace_event,
)


def test_trace_store_records_and_reads_events(tmp_path):
    db_path = Path(tmp_path) / "observability.sqlite"

    record_trace_event(
        trace_id="trace-store-test-001",
        event_type="test_event",
        payload={"message": "hello"},
        db_path=db_path,
    )

    record_trace_event(
        trace_id="trace-store-test-001",
        event_type="second_event",
        payload={"message": "world"},
        db_path=db_path,
    )

    events = get_trace_events(
        trace_id="trace-store-test-001",
        db_path=db_path,
    )

    traces = list_recent_trace_ids(
        limit=5,
        db_path=db_path,
    )

    assert len(events) == 2
    assert events[0]["trace_id"] == "trace-store-test-001"
    assert events[0]["event_type"] == "test_event"
    assert events[0]["payload"] == {"message": "hello"}
    assert events[1]["event_type"] == "second_event"
    assert traces[0]["trace_id"] == "trace-store-test-001"
    assert traces[0]["event_count"] == 2


def test_agentic_debug_writes_observability_trace(client):
    trace_id = "observability-agentic-debug-001"

    response = client.post(
        "/rag/agentic-debug",
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
    )

    assert response.status_code == 200

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    data = trace_response.json()

    assert data["trace_id"] == trace_id
    assert data["total_events"] >= 1

    matching_events = [
        event
        for event in data["events"]
        if event["event_type"] == "rag_agentic_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["query"] == "请搜索知识库：LangGraph 是什么？"
    assert payload["rewritten_query"] == "LangGraph 是什么？"
    assert payload["retrieval_needed"] is True
    assert payload["relevance_score"] > 0
    assert "query_analyzer" in payload["steps"]
    assert "answer_with_citations" in payload["steps"]
    assert payload["retrieval_results_count"] >= 1


def test_eval_debug_writes_observability_trace_and_list(client):
    trace_id = "observability-eval-debug-001"

    response = client.post(
        "/rag/eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
        },
    )

    assert response.status_code == 200

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_eval_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["eval_file"] == "eval_cases/rag_agentic_eval.jsonl"
    assert payload["case_count"] == 3
    assert payload["metrics"]["total_cases"] == 3
    assert payload["metrics"]["pass_rate"] == 1.0

    list_response = client.get("/observability/traces?limit=100")

    assert list_response.status_code == 200

    list_data = list_response.json()
    trace_ids = [item["trace_id"] for item in list_data["traces"]]

    assert trace_id in trace_ids