import asyncio

from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
    extract_resource_json,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)
from src.app.mcp_integration.security import (
    build_mcp_security_report,
    evaluate_mcp_server_security,
    evaluate_mcp_tool_security,
)


def test_mcp_security_report_is_ci_safe_and_allows_registered_read_tools():
    report = build_mcp_security_report()

    assert report["report_version"] == "day70_mcp_security_report_v1"
    assert report["policy"]["policy_version"] == "day70_mcp_security_policy_v1"
    assert report["summary"]["tool_count"] == 9
    assert report["summary"]["allowed_tool_count"] == 9
    assert report["summary"]["denied_tool_count"] == 0
    assert report["summary"]["external_servers_executed_in_ci"] is False
    assert report["summary"]["write_tools_enabled_in_ci"] is False
    assert report["summary"]["live_neo4j_required_in_ci"] is False
    assert report["summary"]["network_required_in_ci"] is False
    assert report["safety"]["ci_safe"] is True
    assert report["safety"]["graph_mutation_requires_dry_run"] is True
    assert report["safety"]["audit_trace_enabled"] is True


def test_mcp_security_blocks_missing_scope_write_and_graph_mutation_without_dry_run():
    restricted_principal = MCPPrincipal(
        principal_id="restricted-test-principal",
        scopes=("mcp:system:read",),
        allow_external_servers=False,
        allow_write_tools=False,
        allow_live_neo4j=False,
        allow_network=False,
    )

    missing_scope = evaluate_mcp_tool_security(
        tool_name="agentic_rag_query",
        principal=restricted_principal,
        trace_id="test-day70-missing-scope",
    )
    assert missing_scope["allowed"] is False
    assert "missing_required_scopes" in missing_scope["blocked_reasons"]
    assert missing_scope["audit_trace"]["event_type"] == "mcp_security_decision"

    write_request = evaluate_mcp_tool_security(
        tool_name="mcp_security_report",
        principal=get_ci_safe_mcp_principal(),
        requested_write=True,
        trace_id="test-day70-write-block",
    )
    assert write_request["allowed"] is False
    assert "write_tools_disabled_by_principal" in write_request["blocked_reasons"]
    assert "destructive_tools_blocked_by_policy" in write_request["blocked_reasons"]

    graph_mutation = evaluate_mcp_tool_security(
        tool_name="graph_fusion_retrieve",
        principal=get_ci_safe_mcp_principal(),
        requested_graph_mutation=True,
        requested_dry_run=False,
        trace_id="test-day70-graph-mutation-block",
    )
    assert graph_mutation["allowed"] is False
    assert "graph_mutation_requires_dry_run" in graph_mutation["blocked_reasons"]


def test_mcp_security_blocks_external_servers_by_default():
    internal_decision = evaluate_mcp_server_security(
        server_id="agent-api-local",
        trace_id="test-day70-internal-server",
    )
    assert internal_decision["allowed"] is True
    assert internal_decision["reason"] == "allowed"

    external_decision = evaluate_mcp_server_security(
        server_id="external-filesystem-stdio",
        trace_id="test-day70-external-server-block",
    )
    assert external_decision["allowed"] is False
    assert "external_servers_disabled_by_principal" in external_decision["blocked_reasons"]
    assert "external_server_not_in_allowlist" in external_decision["blocked_reasons"]
    assert external_decision["audit_trace"]["target_type"] == "server"


def test_real_mcp_client_can_call_security_report_tool():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_security_report",
            arguments={
                "trace_id": "test-day70-security-report-tool",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_security_report"
    assert payload["trace_id"] == "test-day70-security-report-tool"
    assert payload["summary"]["tool_count"] == 9
    assert payload["summary"]["allowed_tool_count"] == 9
    assert payload["summary"]["denied_tool_count"] == 0
    assert payload["summary"]["external_servers_executed_in_ci"] is False
    assert payload["summary"]["write_tools_enabled_in_ci"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_real_mcp_client_can_read_security_report_resource():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.read_resource(uri="agent-api://mcp/security-report")
    )

    payload = extract_resource_json(result)

    assert payload["resource"] == "agent-api://mcp/security-report"
    report = payload["security_report"]
    assert report["summary"]["tool_count"] == 9
    assert report["summary"]["allowed_tool_count"] == 9
    assert report["summary"]["external_servers_executed_in_ci"] is False
    assert report["safety"]["audit_trace_enabled"] is True
