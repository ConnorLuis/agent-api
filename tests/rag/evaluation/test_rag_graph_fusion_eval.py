def _result_by_backend(data, backend):
    for result in data["results"]:
        if result["retrieval_backend"] == backend:
            return result
    raise AssertionError(f"Backend result not found: {backend}")


def _retrieval_cases(eval_result):
    return [
        case
        for case in eval_result["cases"]
        if case["actual_retrieval_needed"] is True
    ]


def test_rag_eval_debug_supports_graph_fusion_backend_ci_safe(client):
    trace_id = "day48-rag-eval-graph-fusion-dry-run-001"

    response = client.post(
        "/rag/eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "eval_file": "eval_cases/rag_agentic_eval.jsonl",
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
            "retrieval_backend": "graph_fusion",
            "embedding_provider": "deterministic",
            "rebuild_index": True,
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["retrieval_backend"] == "graph_fusion"
    assert data["graph_dry_run"] is True
    assert data["graph_evaluation_metadata"]["graph_fusion_enabled"] is True

    retrieval_cases = _retrieval_cases(data)

    assert retrieval_cases

    first_retrieval_case = retrieval_cases[0]
    metadata = first_retrieval_case["retrieval_metadata"]

    assert metadata["retrieval_backend"] == "graph_fusion"
    assert metadata["graph_dry_run"] is True
    assert metadata["graph_retrieval"]["status"] in {
        "dry_run",
        "no_query_entity_match",
    }
    assert metadata["vector_retrieval"]["result_count"] >= 1
    assert metadata["fusion"]["result_count"] >= 1

    contribution = first_retrieval_case["graph_vector_contribution"]

    assert contribution["retrieval_backend"] == "graph_fusion"
    assert contribution["graph_dry_run"] is True
    assert "graph_status" in contribution
    assert "vector_result_count" in contribution
    assert "graph_and_vector_count" in contribution


def test_backend_eval_debug_compares_graph_fusion_with_existing_backends(client):
    trace_id = "day48-backend-eval-four-backends-dry-run-001"

    response = client.post(
        "/rag/backend-eval-debug",
        headers={"x-trace-id": trace_id},
        json={
            "eval_file": "eval_cases/rag_agentic_eval.jsonl",
            "backends": [
                "hybrid",
                "chroma",
                "chroma_rerank",
                "graph_fusion",
            ],
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
            "embedding_provider": "deterministic",
            "rebuild_index": True,
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["trace_id"] == trace_id
    assert data["backends"] == [
        "hybrid",
        "chroma",
        "chroma_rerank",
        "graph_fusion",
    ]
    assert data["graph_dry_run"] is True
    assert data["graph_evaluation_metadata"]["graph_fusion_included"] is True

    evaluated_backends = [
        result["retrieval_backend"]
        for result in data["results"]
    ]

    assert evaluated_backends == [
        "hybrid",
        "chroma",
        "chroma_rerank",
        "graph_fusion",
    ]

    graph_fusion_result = _result_by_backend(data, "graph_fusion")
    graph_fusion_retrieval_cases = _retrieval_cases(graph_fusion_result)

    assert graph_fusion_retrieval_cases

    metadata = graph_fusion_retrieval_cases[0]["retrieval_metadata"]

    assert metadata["retrieval_backend"] == "graph_fusion"
    assert metadata["graph_dry_run"] is True
    assert "graph_retrieval" in metadata
    assert "vector_retrieval" in metadata
    assert "fusion" in metadata

    contribution = graph_fusion_retrieval_cases[0]["graph_vector_contribution"]

    assert contribution["retrieval_backend"] == "graph_fusion"
    assert contribution["graph_dry_run"] is True

    assert data["comparison_summary"]["total_backends"] == 4
    assert "graph_fusion" in data["comparison_summary"]["evaluated_backends"]


def test_backend_eval_debug_default_backends_do_not_switch_to_graph_fusion(client):
    response = client.post(
        "/rag/backend-eval-debug",
        json={
            "eval_file": "eval_cases/rag_agentic_eval.jsonl",
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

    assert data["backends"] == ["hybrid", "chroma"]
    assert "graph_fusion" not in data["backends"]
    assert data["graph_evaluation_metadata"]["graph_fusion_included"] is False


def test_agentic_rag_default_backend_still_hybrid_after_eval_support(client):
    response = client.post(
        "/rag/agentic-debug",
        json={
            "query": "RAG 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_backend"] == "hybrid"
    assert "hybrid_retrieve" in data["steps"]
    assert "graph_fusion_retrieve" not in data["steps"]
