from src.app.evaluation.rag_eval import compare_rag_retrieval_backends


def test_compare_rag_retrieval_backends_returns_pairwise_metric_deltas():
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

    assert result["backends"] == ["hybrid", "chroma", "chroma_rerank"]

    # Backward-compatible Day34 field remains first-vs-second.
    assert result["metric_deltas"]["baseline_backend"] == "hybrid"
    assert result["metric_deltas"]["comparison_backend"] == "chroma"

    pairwise = result["pairwise_metric_deltas"]

    assert len(pairwise) == 3

    pairs = {
        (
            item["baseline_backend"],
            item["comparison_backend"],
        ): item
        for item in pairwise
    }

    assert ("hybrid", "chroma") in pairs
    assert ("hybrid", "chroma_rerank") in pairs
    assert ("chroma", "chroma_rerank") in pairs

    assert pairs[("hybrid", "chroma")]["pass_rate_delta"] == -0.333333
    assert pairs[("hybrid", "chroma_rerank")]["pass_rate_delta"] == 0.0
    assert pairs[("chroma", "chroma_rerank")]["pass_rate_delta"] == 0.333333

    assert (
        pairs[("hybrid", "chroma_rerank")]["average_relevance_score_delta"]
        > 0
    )
    assert (
        pairs[("chroma", "chroma_rerank")]["average_relevance_score_delta"]
        > 0
    )


def test_rag_backend_eval_debug_endpoint_returns_pairwise_metric_deltas(client):
    trace_id = "rag-backend-pairwise-eval-001"

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

    assert data["trace_id"] == trace_id
    assert data["backends"] == ["hybrid", "chroma", "chroma_rerank"]

    # Backward-compatible Day34 field.
    assert data["metric_deltas"]["baseline_backend"] == "hybrid"
    assert data["metric_deltas"]["comparison_backend"] == "chroma"

    pairwise = data["pairwise_metric_deltas"]

    assert len(pairwise) == 3

    pairs = {
        (
            item["baseline_backend"],
            item["comparison_backend"],
        ): item
        for item in pairwise
    }

    assert ("hybrid", "chroma") in pairs
    assert ("hybrid", "chroma_rerank") in pairs
    assert ("chroma", "chroma_rerank") in pairs

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

    assert len(payload["pairwise_metric_deltas"]) == 3

    trace_pairs = {
        (
            item["baseline_backend"],
            item["comparison_backend"],
        )
        for item in payload["pairwise_metric_deltas"]
    }

    assert ("hybrid", "chroma") in trace_pairs
    assert ("hybrid", "chroma_rerank") in trace_pairs
    assert ("chroma", "chroma_rerank") in trace_pairs