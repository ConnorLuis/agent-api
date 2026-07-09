import asyncio

from src.app.mcp_integration.client import (
    call_mcp_tool,
    extract_json_content,
    list_mcp_tools,
)


def test_real_mcp_stdio_client_can_list_agent_api_tools():
    tool_names = asyncio.run(list_mcp_tools())

    assert set(tool_names) == {
        "agentic_rag_query",
        "graph_fusion_retrieve",
        "multi_agent_eval_trace",
        "answer_verify",
        "rag_backend_eval",
        "mcp_registry_summary",
        "mcp_marketplace_discovery",
        "mcp_security_report",
        "mcp_endpoint_coverage_report",
    }


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
