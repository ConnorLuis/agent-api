EXTENDED_EVAL_FILE = "eval_cases/rag_agentic_eval_extended.jsonl"


def _post_extended_backend_eval(client, trace_id: str):
    return client.post(
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


def test_extended_backend_eval_report_contains_failure_analysis_and_policy(
    client,
):
    response = _post_extended_backend_eval(
        client=client,
        trace_id="day40-extended-analysis-001",
    )

    assert response.status_code == 200

    data = response.json()
    report = data["evaluation_report"]

    assert "failure_analysis" in report
    assert "selection_policy_evaluation" in report

    failure_analysis = report["failure_analysis"]

    assert failure_analysis["total_case_count"] == 12
    assert "hybrid" in failure_analysis["failed_cases_by_backend"]
    assert "chroma" in failure_analysis["failed_cases_by_backend"]
    assert "chroma_rerank" in failure_analysis["failed_cases_by_backend"]

    assert "agent_definition" in failure_analysis["common_failed_cases"]
    assert "agent_graph_flow" not in failure_analysis["common_failed_cases"]

    assert failure_analysis["failure_count_by_backend"]["hybrid"] >= 1
    assert failure_analysis["failure_count_by_backend"]["chroma"] >= 1
    assert failure_analysis["failure_count_by_backend"]["chroma_rerank"] >= 1

    policy = report["selection_policy_evaluation"]

    assert policy["candidate_backend"] == report["recommended_backend"]
    assert policy["default_backend"] == "hybrid"
    assert policy["default_backend_should_change"] is False
    assert "chroma_rerank" in policy["pass_rate_winners"]
    assert policy["best_relevance_backend"] == "chroma_rerank"

    blocking_text = " ".join(policy["blocking_reasons"]).lower()

    assert "deterministic" in blocking_text or "semantic" in blocking_text
    assert "agent_definition" in blocking_text


def test_extended_backend_eval_trace_contains_failure_analysis_and_policy(
    client,
):
    trace_id = "day40-extended-analysis-trace-001"

    response = _post_extended_backend_eval(
        client=client,
        trace_id=trace_id,
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
    report = payload["evaluation_report"]

    assert "failure_analysis" in report
    assert "selection_policy_evaluation" in report

    assert report["failure_analysis"]["total_case_count"] == 12
    assert report["selection_policy_evaluation"][
        "candidate_backend"
    ] == report["recommended_backend"]
    assert report["selection_policy_evaluation"][
        "default_backend_should_change"
    ] is False
