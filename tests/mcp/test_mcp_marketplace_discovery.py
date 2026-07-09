import asyncio

from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
    extract_resource_json,
)
from src.app.mcp_integration.discovery import build_marketplace_discovery_report
from src.app.mcp_integration.permissions import get_ci_safe_mcp_principal


def test_marketplace_discovery_report_keeps_external_servers_manual_only():
    report = build_marketplace_discovery_report()

    assert report["report_version"] == "day69_marketplace_discovery_v1"
    assert report["summary"]["server_count"] == 3
    assert report["summary"]["enabled_by_default"] == ["agent-api-local"]
    assert report["summary"]["ci_safe_servers"] == ["agent-api-local"]
    assert set(report["summary"]["external_server_ids"]) == {
        "external-filesystem-stdio",
        "external-memory-stdio",
    }
    assert report["summary"]["external_servers_enabled_by_default"] == []
    assert report["summary"]["ci_external_server_launches"] == []
    assert report["safety"]["external_servers_executed_in_ci"] is False
    assert report["safety"]["network_required_in_ci"] is False


def test_marketplace_discovery_report_records_access_decisions():
    report = build_marketplace_discovery_report()
    decisions = {
        item["server"]["server_id"]: item["access_decision"]
        for item in report["servers"]
    }

    assert decisions["agent-api-local"]["allowed"] is True
    assert decisions["agent-api-local"]["reason"] == "allowed_internal_server"

    assert decisions["external-filesystem-stdio"]["allowed"] is False
    assert decisions["external-filesystem-stdio"]["reason"] == "missing_required_scopes"

    assert decisions["external-memory-stdio"]["allowed"] is False
    assert decisions["external-memory-stdio"]["reason"] == "missing_required_scopes"


def test_marketplace_discovery_report_exposes_manual_validation_commands_without_execution():
    report = build_marketplace_discovery_report()
    commands = {
        item["server_id"]: item
        for item in report["manual_validation_commands"]
    }

    assert set(commands) == {
        "external-filesystem-stdio",
        "external-memory-stdio",
    }

    filesystem_command = commands["external-filesystem-stdio"]
    assert filesystem_command["manual_only"] is True
    assert filesystem_command["ci_safe"] is False
    assert filesystem_command["command"] == "npx"
    assert "@modelcontextprotocol/server-filesystem" in filesystem_command["args"]
    assert "npx" in filesystem_command["shell_preview"]


def test_real_mcp_client_can_call_marketplace_discovery_tool():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_marketplace_discovery",
            arguments={
                "trace_id": "test-day69-marketplace-discovery-tool",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_marketplace_discovery"
    assert payload["trace_id"] == "test-day69-marketplace-discovery-tool"
    assert payload["summary"]["server_count"] == 3
    assert payload["summary"]["external_servers_enabled_by_default"] == []
    assert payload["summary"]["manual_validation_command_count"] == 2
    assert payload["summary"]["external_servers_executed_in_ci"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_real_mcp_client_can_read_marketplace_discovery_resource():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.read_resource(uri="agent-api://mcp/marketplace-discovery")
    )

    payload = extract_resource_json(result)

    assert payload["resource"] == "agent-api://mcp/marketplace-discovery"
    report = payload["discovery_report"]
    assert report["summary"]["server_count"] == 3
    assert report["summary"]["external_servers_enabled_by_default"] == []
    assert report["safety"]["external_servers_executed_in_ci"] is False
    assert len(report["manual_validation_commands"]) == 2
