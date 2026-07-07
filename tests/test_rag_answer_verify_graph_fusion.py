def _latest_payload(trace_response):
    data = trace_response.json()
    events = data["events"]
    assert events
    return events[-1]["payload"]


def test_answer_verify_supports_graph_fusion_backend_ci_safe(client):
    trace_id = "day49-answer-verify-graph-fusion-dry-run-001"

    response = client.post(
        "/rag/answer-verify-debug",
        headers={"x-trace-id": trace_id},
        json={
            "query": "请搜索知识库：RAG 是什么？",
            "top_k": 2,
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
    assert data["verification_pass"] is True
    assert data["answer_supported"] is True

    assert data["retrieval_metadata"]["retrieval_backend"] == "graph_fusion"
    assert data["retrieval_metadata"]["graph_dry_run"] is True

    contribution = data["graph_vector_contribution"]

    assert contribution["retrieval_backend"] == "graph_fusion"
    assert contribution["graph_dry_run"] is True
    assert contribution["vector_result_count"] >= 1
    assert contribution["fusion_result_count"] >= 1

    graph_verification = data["graph_fusion_verification"]

    assert graph_verification["retrieval_backend"] == "graph_fusion"
    assert graph_verification["graph_metadata_present"] is True
    assert graph_verification["graph_or_vector_evidence_present"] is True
    assert graph_verification["graph_dry_run"] is True

    trace_response = client.get(f"/observability/traces/{trace_id}")

    assert trace_response.status_code == 200

    payload = _latest_payload(trace_response)

    assert payload["retrieval_backend"] == "graph_fusion"
    assert payload["retrieval_metadata"]["retrieval_backend"] == "graph_fusion"
    assert payload["graph_vector_contribution"]["retrieval_backend"] == "graph_fusion"
    assert payload["graph_fusion_verification"]["retrieval_backend"] == "graph_fusion"


def test_answer_verify_default_backend_remains_hybrid(client):
    response = client.post(
        "/rag/answer-verify-debug",
        json={
            "query": "请搜索知识库：RAG 是什么？",
            "top_k": 2,
            "source_filter": "agent_basics",
            "max_chars": 300,
            "embedding_dim": 64,
            "keyword_weight": 0.6,
            "vector_weight": 0.4,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_backend"] == "hybrid"
    assert data["graph_vector_contribution"] == {}
    assert data["graph_fusion_verification"] == {}
