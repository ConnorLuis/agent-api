import asyncio

from src.app.mcp_integration.client import (
    call_mcp_tool,
    extract_json_content,
    list_mcp_tools,
)


EXPECTED_TOOL_NAMES = {
    "agentic_rag_query",
    "graph_fusion_retrieve",
    "multi_agent_eval_trace",
    "answer_verify",
    "rag_backend_eval",
    "mcp_registry_summary",
    "mcp_marketplace_discovery",
    "mcp_security_report",
    "mcp_endpoint_coverage_report",
    "mcp_endpoint_probe",
    "erp_get_user_access_profile",
    "erp_get_document_context",
    "erp_check_operation_permission",
    "erp_get_approval_context",
    "erp_get_transfer_context",
}


def test_real_mcp_stdio_client_can_list_agent_api_tools():
    tool_names = asyncio.run(list_mcp_tools())
    assert set(tool_names) == EXPECTED_TOOL_NAMES


def test_real_mcp_stdio_client_can_call_multi_agent_eval_trace():
    result = asyncio.run(
        call_mcp_tool(
            tool_name="multi_agent_eval_trace",
            arguments={
                "task": "解释 MCP 如何调用 Multi-Agent eval trace",
                "thread_id": "test-real-mcp-client-thread",
                "trace_id": "test-real-mcp-client-trace",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "multi_agent_eval_trace"
    assert payload["trace_id"] == "test-real-mcp-client-trace"
    assert payload["allowed"] is True
    assert payload["summary"]["eval_pass"] is True
    assert payload["summary"]["failed_check_count"] == 0
    assert payload["mcp_boundary"]["server"] == "agent-api-mcp"
    assert payload["mcp_boundary"]["default_retrieval_backend"] == "hybrid"
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_real_mcp_stdio_client_can_call_graph_fusion_with_ci_safe_dry_run():
    result = asyncio.run(
        call_mcp_tool(
            tool_name="graph_fusion_retrieve",
            arguments={
                "query": "RAG 和 LangGraph 有什么关系？",
                "top_k": 2,
                "graph_dry_run": False,
                "trace_id": "test-real-mcp-client-graph-trace",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "graph_fusion_retrieve"
    assert payload["trace_id"] == "test-real-mcp-client-graph-trace"
    assert payload["allowed"] is True
    assert payload["authorization"]["reason"] == "allowed_with_dry_run_enforced_for_live_neo4j"
    assert payload["authorization"]["enforced_dry_run"] is True
    assert payload["summary"]["graph_dry_run"] is True
    assert payload["summary"]["graph_status"] == "dry_run"


def test_real_mcp_stdio_client_can_call_erp_permission_tool():
    result = asyncio.run(
        call_mcp_tool(
            tool_name="erp_check_operation_permission",
            arguments={
                "user_id": "SYN-U001",
                "document_id": "SYN-PO-002",
                "operation": "SUBMIT",
                "trace_id": "test-real-mcp-client-erp-permission",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "erp_check_operation_permission"
    assert payload["allowed"] is True
    assert payload["authorization"]["principal_id"] == "erp-diagnosis-readonly-principal"
    assert payload["summary"]["status"] == "completed"
    assert payload["summary"]["operation_allowed"] is False
    assert "ORG_SCOPE_DENIED" in payload["summary"]["reason_codes"]
    assert payload["mcp_boundary"]["read_only"] is True
    assert payload["mcp_boundary"]["write_capability_exposed"] is False
    assert payload["business_audit"]["raw_argument_values_recorded"] is False
