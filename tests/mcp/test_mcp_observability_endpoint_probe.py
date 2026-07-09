import asyncio

from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
)
from src.app.mcp_integration.endpoint_probe import build_mcp_endpoint_probe_report
from src.app.mcp_integration.permissions import get_ci_safe_mcp_principal


def test_observability_traces_probe_is_read_only_and_ci_safe():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="observability_traces",
        trace_id="test-day71-observability-traces-probe",
        trace_limit=5,
    )

    assert report["endpoint_id"] == "observability_traces"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["summary"]["status_code"] == 200
    assert report["summary"]["ok"] is True
    assert report["summary"]["read_only"] is True
    assert report["safety"]["ci_safe"] is True
    assert report["safety"]["read_only"] is True
    assert report["safety"]["write_executed"] is False
    assert report["safety"]["live_neo4j_required"] is False
    assert report["safety"]["rest_endpoint_behavior_changed"] is False


def test_observability_trace_detail_probe_is_read_only_even_when_trace_is_missing():
    report = build_mcp_endpoint_probe_report(
        endpoint_id="observability_trace_detail",
        trace_id="test-day71-observability-trace-detail-probe",
        target_trace_id="test-day71-nonexistent-trace",
        trace_limit=5,
    )

    assert report["endpoint_id"] == "observability_trace_detail"
    assert report["allowed"] is True
    assert report["status"] == "completed"
    assert report["summary"]["status_code"] in {200, 404}
    assert report["summary"]["read_only"] is True
    assert report["summary"]["live_neo4j_required"] is False
    assert report["safety"]["ci_safe"] is True
    assert report["safety"]["write_executed"] is False
    assert report["safety"]["live_neo4j_required"] is False
    assert report["safety"]["rest_endpoint_behavior_changed"] is False
    assert report["result"]["target_trace_id"] == "test-day71-nonexistent-trace"


def test_mcp_observability_traces_probe_tool_is_security_wrapped():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_endpoint_probe",
            arguments={
                "endpoint_id": "observability_traces",
                "trace_id": "test-day71-mcp-observability-traces-tool",
                "trace_limit": 5,
            },
        )
    )
    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_endpoint_probe"
    assert payload["summary"]["endpoint_id"] == "observability_traces"
    assert payload["summary"]["ci_safe"] is True
    assert payload["summary"]["read_only"] is True
    assert payload["summary"]["write_executed"] is False
    assert payload["summary"]["live_neo4j_required"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False
    assert payload["security_decision"]["tool_name"] == "mcp_endpoint_probe"
    assert payload["security_decision"]["allowed"] is True
    assert payload["security_audit_trace"]["event_type"] == "mcp_security_decision"


def test_mcp_observability_trace_detail_probe_tool_is_security_wrapped():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_endpoint_probe",
            arguments={
                "endpoint_id": "observability_trace_detail",
                "trace_id": "test-day71-mcp-observability-trace-detail-tool",
                "target_trace_id": "test-day71-nonexistent-trace",
                "trace_limit": 5,
            },
        )
    )
    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_endpoint_probe"
    assert payload["summary"]["endpoint_id"] == "observability_trace_detail"
    assert payload["summary"]["ci_safe"] is True
    assert payload["summary"]["read_only"] is True
    assert payload["summary"]["write_executed"] is False
    assert payload["summary"]["live_neo4j_required"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False
    assert payload["security_decision"]["allowed"] is True
