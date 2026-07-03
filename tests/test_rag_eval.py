from src.app.evaluation.rag_eval import evaluate_rag_cases, load_rag_eval_cases


def test_load_rag_eval_cases():
    cases = load_rag_eval_cases()

    assert len(cases) == 3
    assert cases[0]["case_id"] == "rag_definition"
    assert cases[1]["case_id"] == "langgraph_definition"
    assert cases[2]["case_id"] == "direct_chat"


def test_evaluate_rag_cases_returns_metrics():
    result = evaluate_rag_cases(
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
        keyword_weight=0.6,
        vector_weight=0.4,
    )

    metrics = result["metrics"]

    assert metrics["total_cases"] == 3
    assert metrics["passed_cases"] == 3
    assert metrics["pass_rate"] == 1.0
    assert metrics["retrieval_decision_accuracy"] == 1.0
    assert metrics["expected_terms_hit_rate"] == 1.0
    assert metrics["citation_hit_rate"] == 1.0
    assert metrics["average_relevance_score"] > 0

    for item in result["cases"]:
        assert item["passed"] is True
        assert item["retrieval_decision_pass"] is True
        assert item["expected_terms_pass"] is True
        assert item["citation_pass"] is True

    langgraph_case = next(
        item for item in result["cases"] if item["case_id"] == "langgraph_definition"
    )

    assert "query_rewriter" in langgraph_case["steps"]
    assert "langgraph" in [
        term.lower() for term in langgraph_case["matched_expected_terms"]
    ]


def test_rag_eval_debug_endpoint(client):
    trace_id = "rag-eval-debug-001"

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
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    metrics = data["metrics"]

    assert data["trace_id"] == trace_id
    assert data["eval_file"] == "eval_cases/rag_agentic_eval.jsonl"
    assert data["source_filter"] == "agent_basics"
    assert metrics["total_cases"] == 3
    assert metrics["passed_cases"] == 3
    assert metrics["pass_rate"] == 1.0
    assert metrics["retrieval_decision_accuracy"] == 1.0
    assert metrics["expected_terms_hit_rate"] == 1.0
    assert metrics["citation_hit_rate"] == 1.0
    assert len(data["cases"]) == 3
    assert all(item["passed"] is True for item in data["cases"])