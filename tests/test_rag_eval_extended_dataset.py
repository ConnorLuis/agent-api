from src.app.evaluation.rag_eval import load_rag_eval_cases


EXTENDED_EVAL_FILE = "eval_cases/rag_agentic_eval_extended.jsonl"


def test_extended_rag_eval_dataset_has_enough_cases():
    cases = load_rag_eval_cases(EXTENDED_EVAL_FILE)

    assert len(cases) >= 11

    case_ids = {case["case_id"] for case in cases}

    assert "rag_definition" in case_ids
    assert "langgraph_definition" in case_ids
    assert "agent_definition" in case_ids
    assert "agent_components" in case_ids
    assert "direct_chat_greeting" in case_ids
    assert "direct_chat_casual" in case_ids


def test_backend_eval_debug_supports_extended_eval_dataset(client):
    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": "day40-extended-eval-001"},
        json={
            "eval_file": EXTENDED_EVAL_FILE,
            "backends": ["hybrid", "chroma", "chroma_rerank"],
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
            "embedding_provider": "deterministic",
            "rebuild_index": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["eval_file"] == EXTENDED_EVAL_FILE
    assert data["backends"] == ["hybrid", "chroma", "chroma_rerank"]
    assert "evaluation_report" in data

    report = data["evaluation_report"]

    assert report["eval_case_count"] >= 11
    assert report["recommended_backend"]
    assert report["default_backend"] == "hybrid"
    assert isinstance(report["metric_highlights"], list)
    assert isinstance(report["risk_notes"], list)
    assert isinstance(report["backend_rank_summary"], list)

    risk_text = " ".join(report["risk_notes"]).lower()

    assert "deterministic" in risk_text or "ci-safe" in risk_text
    assert "small/tiny" not in risk_text


def test_extended_backend_eval_trace_contains_report(client):
    trace_id = "day40-extended-eval-trace-001"

    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "eval_file": EXTENDED_EVAL_FILE,
            "backends": ["hybrid", "chroma", "chroma_rerank"],
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
            "embedding_provider": "deterministic",
            "rebuild_index": True,
        },
    )

    assert response.status_code == 200

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()
    events = trace_data["events"]

    backend_eval_events = [
        event
        for event in events
        if event["event_type"] == "rag_backend_eval_debug"
    ]

    assert backend_eval_events

    payload = backend_eval_events[-1]["payload"]

    assert "evaluation_report" in payload

    report = payload["evaluation_report"]

    assert report["eval_case_count"] >= 11
    assert report["recommended_backend"]
    assert report["default_backend_should_change"] is False
    assert isinstance(report["risk_notes"], list)
