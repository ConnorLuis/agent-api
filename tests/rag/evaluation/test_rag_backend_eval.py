from src.app.evaluation.rag_eval import (
    compare_rag_retrieval_backends,
    evaluate_rag_cases,
)


def test_evaluate_rag_cases_supports_hybrid_backend():
    result = evaluate_rag_cases(
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
        retrieval_backend="hybrid",
    )

    assert result["retrieval_backend"] == "hybrid"
    assert result["metrics"]["total_cases"] == 3
    assert len(result["cases"]) == 3
    assert result["cases"][0]["retrieval_backend"] == "hybrid"


def test_evaluate_rag_cases_supports_chroma_backend():
    result = evaluate_rag_cases(
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        retrieval_backend="chroma",
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["retrieval_backend"] == "chroma"
    assert result["metrics"]["total_cases"] == 3
    assert len(result["cases"]) == 3
    assert result["cases"][0]["retrieval_backend"] == "chroma"


def test_compare_rag_retrieval_backends():
    result = compare_rag_retrieval_backends(
        backends=["hybrid", "chroma"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["backends"] == ["hybrid", "chroma"]
    assert len(result["results"]) == 2
    assert result["results"][0]["retrieval_backend"] == "hybrid"
    assert result["results"][1]["retrieval_backend"] == "chroma"
    assert result["best_backend_by_pass_rate"] in {"hybrid", "chroma"}
    assert result["best_backend_by_average_relevance"] in {"hybrid", "chroma"}


def test_rag_backend_eval_debug_endpoint_writes_trace(client):
    trace_id = "rag-backend-eval-debug-001"

    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "backends": ["hybrid", "chroma"],
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
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["backends"] == ["hybrid", "chroma"]
    assert len(data["results"]) == 2
    assert data["results"][0]["retrieval_backend"] == "hybrid"
    assert data["results"][1]["retrieval_backend"] == "chroma"

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_backend_eval_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["backends"] == ["hybrid", "chroma"]
    assert len(payload["backend_metrics"]) == 2
    assert payload["backend_metrics"][0]["retrieval_backend"] == "hybrid"
    assert payload["backend_metrics"][1]["retrieval_backend"] == "chroma"


def test_compare_rag_retrieval_backends_returns_refined_metrics():
    result = compare_rag_retrieval_backends(
        backends=["hybrid", "chroma"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    assert result["metric_deltas"]["baseline_backend"] == "hybrid"
    assert result["metric_deltas"]["comparison_backend"] == "chroma"
    assert "pass_rate_delta" in result["metric_deltas"]
    assert "average_relevance_score_delta" in result["metric_deltas"]

    assert len(result["case_comparisons"]) == 3
    assert result["case_comparisons"][0]["case_id"]
    assert result["case_comparisons"][0]["backend_results"]

    assert result["comparison_summary"]["best_backend_by_pass_rate"] in {
        "hybrid",
        "chroma",
    }
    assert result["comparison_summary"]["best_backend_by_average_relevance"] in {
        "hybrid",
        "chroma",
    }
    assert len(result["comparison_summary"]["notes"]) >= 1


def test_rag_backend_eval_debug_endpoint_returns_refined_metrics(client):
    trace_id = "rag-backend-eval-refined-001"

    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "backends": ["hybrid", "chroma"],
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

    assert data["trace_id"] == trace_id
    assert data["metric_deltas"]["baseline_backend"] == "hybrid"
    assert data["metric_deltas"]["comparison_backend"] == "chroma"
    assert len(data["case_comparisons"]) == 3
    assert len(data["comparison_summary"]["notes"]) >= 1

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    trace_data = trace_response.json()

    matching_events = [
        event
        for event in trace_data["events"]
        if event["event_type"] == "rag_backend_eval_debug"
    ]

    assert len(matching_events) >= 1

    payload = matching_events[-1]["payload"]

    assert payload["metric_deltas"]["baseline_backend"] == "hybrid"
    assert payload["metric_deltas"]["comparison_backend"] == "chroma"
    assert len(payload["case_comparisons"]) == 3
    assert len(payload["comparison_summary"]["notes"]) >= 1