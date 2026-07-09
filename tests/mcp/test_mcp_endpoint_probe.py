import asyncio

from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
)
from src.app.mcp_integration.endpoint_probe import (
    SUPPORTED_ENDPOINT_PROBE_IDS,
    build_mcp_endpoint_probe_report,
)
from src.app.mcp_integration.permissions import get_ci_safe_mcp_principal


def test_endpoint_probe_supports_selected_day71_endpoint_ids():
    assert SUPPORTED_ENDPOINT_PROBE_IDS == (
        "graph_extract_debug",
        "graph_retrieval_debug",
        "multi_agent_supervisor_debug",
        "multi_agent_stream",
    )


def test_graph_extract_endpoint_probe_is_ci_safe_and_read_only():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="graph_extract_debug",
        trace_id="test-day71-graph-extract-probe",
    )

    assert report["report_version"] == "day71_mcp_endpoint_probe_report_v1"
    assert report["endpoint_id"] == "graph_extract_debug"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["summary"]["entities"] >= 1
    assert report["summary"]["relations"] >= 1
    assert report["safety"]["ci_safe"] is True
    assert report["safety"]["read_only"] is True
    assert report["safety"]["write_executed"] is False
    assert report["safety"]["live_neo4j_required"] is False
    assert report["safety"]["rest_endpoint_behavior_changed"] is False


def test_graph_retrieval_endpoint_probe_enforces_dry_run():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="graph_retrieval_debug",
        trace_id="test-day71-graph-retrieval-probe",
        query="RAG 和 LangGraph 有什么关系？",
        dry_run=False,
    )

    assert report["endpoint_id"] == "graph_retrieval_debug"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["probe"]["dry_run"] is True
    assert report["summary"]["dry_run"] is True
    assert report["summary"]["live_neo4j_required"] is False
    assert report["safety"]["dry_run_enforced"] is True
    assert report["safety"]["write_executed"] is False
    assert report["safety"]["live_neo4j_required"] is False


def test_multi_agent_supervisor_endpoint_probe_returns_supervisor_summary():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="multi_agent_supervisor_debug",
        trace_id="test-day71-supervisor-probe",
        task="Implement a CI-safe Agentic RAG feature and validate it.",
    )

    assert report["endpoint_id"] == "multi_agent_supervisor_debug"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["summary"]["current_role"] == "supervisor"
    assert report["summary"]["status"] == "completed"
    assert report["summary"]["orchestration_pass"] is True
    assert report["summary"]["llm_used"] is False
    assert report["safety"]["write_executed"] is False


def test_multi_agent_stream_endpoint_probe_returns_stream_summary():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="multi_agent_stream",
        trace_id="test-day71-stream-probe",
        task="Implement a CI-safe Agentic RAG feature and validate it.",
    )

    assert report["endpoint_id"] == "multi_agent_stream"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["summary"]["event_count"] == 29
    assert report["summary"]["event_counts"]["metadata"] == 1
    assert report["summary"]["event_counts"]["graph"] == 1
    assert report["summary"]["event_counts"]["node"] == 6
    assert report["summary"]["event_counts"]["edge"] == 5
    assert report["summary"]["event_counts"]["role"] == 7
    assert report["summary"]["event_counts"]["artifact"] == 7
    assert report["summary"]["event_counts"]["final"] == 1
    assert report["summary"]["event_counts"]["done"] == 1
    assert report["summary"]["llm_used"] is False


def test_unsupported_endpoint_probe_is_denied_without_execution():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="observability_traces",
        trace_id="test-day71-unsupported-probe",
    )

    assert report["allowed"] is False
    assert report["status"] == "unsupported_endpoint_probe"
    assert "graph_extract_debug" in report["supported_endpoint_ids"]
    assert report["safety"]["ci_safe"] is True
    assert report["safety"]["write_executed"] is False
    assert report["safety"]["live_neo4j_required"] is False


def test_mcp_endpoint_probe_tool_is_security_wrapped():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_endpoint_probe",
            arguments={
                "endpoint_id": "graph_retrieval_debug",
                "trace_id": "test-day71-mcp-endpoint-probe-tool",
                "query": "RAG 和 LangGraph 有什么关系？",
                "dry_run": False,
            },
        )
    )
    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_endpoint_probe"
    assert payload["trace_id"] == "test-day71-mcp-endpoint-probe-tool"
    assert payload["summary"]["endpoint_id"] == "graph_retrieval_debug"
    assert payload["summary"]["dry_run_enforced"] is True
    assert payload["summary"]["write_executed"] is False
    assert payload["summary"]["live_neo4j_required"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False
    assert payload["security_decision"]["tool_name"] == "mcp_endpoint_probe"
    assert payload["security_decision"]["allowed"] is True
    assert payload["security_audit_trace"]["event_type"] == "mcp_security_decision"
