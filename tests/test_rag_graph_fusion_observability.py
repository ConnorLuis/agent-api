def _latest_payload(trace_response):
    data = trace_response.json()
    events = data["events"]
    assert events
    return events[-1]["payload"]


def _first_retrieval_case(cases):
    for case in cases:
        if case["actual_retrieval_needed"] is True:
            return case
    raise AssertionError("No retrieval case found")


def _result_by_backend(data, backend):
    for result in data["results"]:
        if result["retrieval_backend"] == backend:
            return result
    raise AssertionError(f"Backend result not found: {backend}")


def test_agentic_graph_fusion_trace_preserves_graph_vector_metadata(client):
    trace_id = "day49-agentic-graph-fusion-trace-001"

    response = client.post(
        "/rag/agentic-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 和 LangGraph 有什么关系？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "retrieval_backend": "graph_fusion",
            "graph_dry_run": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_backend"] == "graph_fusion"
    assert data["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"
    assert data["graph_vector_contribution"]["graph_dry_run"] is True

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    payload = _latest_payload(trace_response)

    assert payload["retrieval_backend"] == "graph_fusion"
    assert payload["retrieval_metadata"]["retrieval_backend"] == "graph_fusion"
    assert payload["retrieval_metadata"]["graph_dry_run"] is True
    assert payload["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"
    assert payload["graph_vector_contribution"]["graph_dry_run"] is True


def test_rag_eval_graph_fusion_trace_preserves_case_contribution(client):
    trace_id = "day49-rag-eval-graph-fusion-trace-001"

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

    data = response.json()

    assert data["graph_evaluation_metadata"]["graph_fusion_enabled"] is True

    retrieval_case = _first_retrieval_case(data["cases"])

    assert retrieval_case["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    payload = _latest_payload(trace_response)
    trace_case = _first_retrieval_case(payload["cases"])

    assert payload["retrieval_backend"] == "graph_fusion"
    assert payload["graph_evaluation_metadata"]["graph_fusion_enabled"] is True
    assert trace_case["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"
    assert trace_case["graph_vector_contribution"]["graph_dry_run"] is True


def test_backend_eval_graph_fusion_trace_preserves_backend_contribution(client):
    trace_id = "day49-backend-eval-graph-fusion-trace-001"

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

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    payload = _latest_payload(trace_response)

    assert payload["graph_evaluation_metadata"]["graph_fusion_included"] is True

    graph_result = _result_by_backend(payload, "graph_fusion")
    retrieval_case = _first_retrieval_case(graph_result["cases"])

    assert retrieval_case["retrieval_metadata"]["retrieval_backend"] == "graph_fusion"
    assert retrieval_case["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"
    assert retrieval_case["graph_vector_contribution"]["graph_dry_run"] is True

    assert payload["evaluation_report"]["default_backend"] == "hybrid"
    assert payload["evaluation_report"]["default_backend_should_change"] is False
