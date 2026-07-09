from src.app.mcp_integration.tools import (
    run_answer_verify_mcp_tool,
    run_mcp_registry_summary_tool,
    run_rag_backend_eval_mcp_tool,
)


def test_answer_verify_mcp_tool_contract():
    payload = run_answer_verify_mcp_tool(
        query="RAG 是什么？",
        top_k=2,
        trace_id="test-day68-answer-verify-001",
    )

    assert payload["tool_name"] == "answer_verify"
    assert payload["trace_id"] == "test-day68-answer-verify-001"
    assert payload["allowed"] is True
    assert payload["authorization"]["allowed"] is True
    assert payload["summary"]["status"] == "completed"
    assert payload["summary"]["retrieval_backend"] == "hybrid"
    assert "verification_pass" in payload["summary"]
    assert "answer_supported" in payload["summary"]
    assert payload["mcp_boundary"]["server"] == "agent-api-mcp"
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_answer_verify_mcp_tool_enforces_graph_dry_run_for_graph_fusion():
    payload = run_answer_verify_mcp_tool(
        query="RAG 和 LangGraph 有什么关系？",
        retrieval_backend="graph_fusion",
        graph_dry_run=False,
        top_k=2,
        trace_id="test-day68-answer-verify-graph-001",
    )

    assert payload["tool_name"] == "answer_verify"
    assert payload["allowed"] is True
    assert payload["authorization"]["reason"] == "allowed_with_dry_run_enforced_for_live_neo4j"
    assert payload["authorization"]["enforced_dry_run"] is True
    assert payload["summary"]["graph_dry_run"] is True
    assert payload["summary"]["retrieval_backend"] == "graph_fusion"


def test_rag_backend_eval_mcp_tool_contract():
    payload = run_rag_backend_eval_mcp_tool(
        backends=["hybrid", "graph_fusion"],
        graph_dry_run=True,
        trace_id="test-day68-rag-backend-eval-001",
    )

    assert payload["tool_name"] == "rag_backend_eval"
    assert payload["trace_id"] == "test-day68-rag-backend-eval-001"
    assert payload["allowed"] is True
    assert payload["summary"]["status"] == "completed"
    assert payload["summary"]["backends"] == ["hybrid", "graph_fusion"]
    assert payload["summary"]["graph_dry_run"] is True
    assert payload["result"]["backends"] == ["hybrid", "graph_fusion"]
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_rag_backend_eval_mcp_tool_enforces_dry_run_for_graph_fusion():
    payload = run_rag_backend_eval_mcp_tool(
        backends=["hybrid", "graph_fusion"],
        graph_dry_run=False,
        trace_id="test-day68-rag-backend-eval-dry-run-001",
    )

    assert payload["tool_name"] == "rag_backend_eval"
    assert payload["allowed"] is True
    assert payload["authorization"]["reason"] == "allowed_with_dry_run_enforced_for_live_neo4j"
    assert payload["authorization"]["enforced_dry_run"] is True
    assert payload["summary"]["graph_dry_run"] is True


def test_mcp_registry_summary_tool_contract():
    payload = run_mcp_registry_summary_tool(
        trace_id="test-day68-registry-summary-001",
    )

    assert payload["tool_name"] == "mcp_registry_summary"
    assert payload["trace_id"] == "test-day68-registry-summary-001"
    assert payload["allowed"] is True
    assert payload["summary"]["tool_count"] == 8
    assert payload["summary"]["server_count"] == 3
    assert payload["summary"]["external_servers_enabled_by_default"] == []
    assert payload["result"]["registry"]["tool_count"] == 8
    assert payload["result"]["permission_boundary"]["allow_external_servers"] is False
    assert payload["result"]["permission_boundary"]["allow_live_neo4j"] is False
