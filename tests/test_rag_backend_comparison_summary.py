from src.app.evaluation.rag_eval import compare_rag_retrieval_backends


def test_compare_rag_retrieval_backends_returns_multi_backend_summary():
    result = compare_rag_retrieval_backends(
        backends=["hybrid", "chroma", "chroma_rerank"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
        embedding_provider="deterministic",
        rebuild_index=True,
    )

    summary = result["comparison_summary"]

    assert summary["total_backends"] == 3
    assert summary["evaluated_backends"] == [
        "hybrid",
        "chroma",
        "chroma_rerank",
    ]

    assert summary["best_backend_by_pass_rate"] == "hybrid"
    assert summary["best_backend_by_average_relevance"] == "chroma_rerank"

    pass_rate_winner = summary["metric_winners"]["pass_rate"]

    assert pass_rate_winner["tie"] is True
    assert set(pass_rate_winner["winners"]) == {
        "hybrid",
        "chroma_rerank",
    }
    assert pass_rate_winner["value"] == 1.0

    average_relevance_winner = summary["metric_winners"][
        "average_relevance_score"
    ]

    assert average_relevance_winner["tie"] is False
    assert average_relevance_winner["winners"] == ["chroma_rerank"]
    assert average_relevance_winner["value"] == 0.394302

    assert summary["metric_rankings"]["pass_rate"][0]["value"] == 1.0
    assert (
        summary["metric_rankings"]["average_relevance_score"][0][
            "retrieval_backend"
        ]
        == "chroma_rerank"
    )

    top_improvement_pairs = summary["top_improvement_pairs"]

    assert len(top_improvement_pairs) >= 1

    improvement_pairs = {
        (
            item["metric"],
            item["baseline_backend"],
            item["comparison_backend"],
        ): item["delta"]
        for item in top_improvement_pairs
    }

    assert (
        "pass_rate",
        "chroma",
        "chroma_rerank",
    ) in improvement_pairs

    assert (
        "average_relevance_score",
        "hybrid",
        "chroma_rerank",
    ) in improvement_pairs

    notes_text = "\n".join(summary["notes"])

    assert "Evaluated 3 backends" in notes_text
    assert "Pass rate is tied" in notes_text
    assert "Best average_relevance_score is chroma_rerank" in notes_text
    assert "Largest pass_rate improvement is chroma -> chroma_rerank" in notes_text
    assert (
        "Largest average_relevance_score improvement is hybrid -> chroma_rerank"
        in notes_text
    )


def test_rag_backend_eval_debug_trace_contains_multi_backend_summary(client):
    trace_id = "rag-backend-summary-refinement-001"

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

    data = response.json()
    summary = data["comparison_summary"]

    assert summary["evaluated_backends"] == [
        "hybrid",
        "chroma",
        "chroma_rerank",
    ]
    assert summary["metric_winners"]["pass_rate"]["tie"] is True
    assert summary["metric_winners"]["average_relevance_score"][
        "winners"
    ] == ["chroma_rerank"]

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
    trace_summary = payload["comparison_summary"]

    assert trace_summary["evaluated_backends"] == [
        "hybrid",
        "chroma",
        "chroma_rerank",
    ]
    assert trace_summary["metric_winners"]["pass_rate"]["tie"] is True
    assert trace_summary["metric_winners"]["average_relevance_score"][
        "winners"
    ] == ["chroma_rerank"]
    assert len(trace_summary["top_improvement_pairs"]) >= 1

    notes_text = "\n".join(trace_summary["notes"])

    assert "Evaluated 3 backends" in notes_text
    assert "Pass rate is tied" in notes_text
    assert "Best average_relevance_score is chroma_rerank" in notes_text