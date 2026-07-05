from src.app.evaluation.rag_report import build_backend_evaluation_report


def test_build_backend_evaluation_report_from_comparison_dict():
    comparison = {
        "eval_file": "eval_cases/rag_agentic_eval.jsonl",
        "embedding_provider": "deterministic",
        "embedding_model": "deterministic-hash",
        "best_backend_by_pass_rate": "hybrid",
        "best_backend_by_average_relevance": "chroma_rerank",
        "comparison_summary": {
            "metric_winners": {
                "pass_rate": {
                    "value": 1.0,
                    "winners": ["hybrid", "chroma_rerank"],
                    "tie": True,
                },
                "average_relevance_score": {
                    "value": 0.394302,
                    "winners": ["chroma_rerank"],
                    "tie": False,
                },
            },
            "top_improvement_pairs": [
                {
                    "metric": "average_relevance_score",
                    "baseline_backend": "hybrid",
                    "comparison_backend": "chroma_rerank",
                    "delta": 0.116079,
                }
            ],
            "notes": [],
        },
        "results": [
            {
                "retrieval_backend": "hybrid",
                "metrics": {
                    "total_cases": 3,
                    "passed_cases": 3,
                    "pass_rate": 1.0,
                    "retrieval_decision_accuracy": 1.0,
                    "expected_terms_hit_rate": 1.0,
                    "citation_hit_rate": 1.0,
                    "average_relevance_score": 0.278223,
                },
            },
            {
                "retrieval_backend": "chroma_rerank",
                "metrics": {
                    "total_cases": 3,
                    "passed_cases": 3,
                    "pass_rate": 1.0,
                    "retrieval_decision_accuracy": 1.0,
                    "expected_terms_hit_rate": 1.0,
                    "citation_hit_rate": 1.0,
                    "average_relevance_score": 0.394302,
                },
            },
        ],
    }

    report = build_backend_evaluation_report(comparison)

    assert report["recommended_backend"] == "chroma_rerank"
    assert report["default_backend"] == "hybrid"
    assert report["default_backend_should_change"] is False
    assert report["selection_policy"] == "keep_default_hybrid_until_larger_eval_set"
    assert isinstance(report["metric_highlights"], list)
    assert isinstance(report["risk_notes"], list)
    assert isinstance(report["backend_rank_summary"], list)

    risk_text = " ".join(report["risk_notes"]).lower()
    assert "deterministic" in risk_text or "ci-safe" in risk_text
    assert "small" in risk_text or "tiny" in risk_text


def test_backend_eval_debug_returns_evaluation_report(client):
    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": "day39-backend-report-001"},
        json={
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
    assert "evaluation_report" in data

    report = data["evaluation_report"]

    assert report["recommended_backend"]
    assert "recommendation_reason" in report
    assert "default_backend_should_change" in report
    assert isinstance(report["metric_highlights"], list)
    assert isinstance(report["risk_notes"], list)
    assert isinstance(report["backend_rank_summary"], list)

    risk_text = " ".join(report["risk_notes"]).lower()
    assert "deterministic" in risk_text or "ci-safe" in risk_text
    assert "small" in risk_text or "tiny" in risk_text


def test_backend_eval_debug_trace_contains_evaluation_report(client):
    trace_id = "day39-backend-report-trace-001"

    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": trace_id},
        json={
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
    events = trace_data["events"] if isinstance(trace_data, dict) else trace_data

    backend_eval_events = [
        event
        for event in events
        if event["event_type"] == "rag_backend_eval_debug"
    ]

    assert backend_eval_events

    payload = backend_eval_events[-1]["payload"]

    assert "evaluation_report" in payload

    report = payload["evaluation_report"]

    assert report["recommended_backend"]
    assert report["default_backend_should_change"] is False
    assert isinstance(report["risk_notes"], list)