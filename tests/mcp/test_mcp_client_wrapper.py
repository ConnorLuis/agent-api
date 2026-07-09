import asyncio
import json

import pytest

from src.app.mcp_integration.client import (
    MCPClientConfig,
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    discover_mcp_server_capabilities,
    extract_json_content,
    extract_resource_json,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)


EXPECTED_DAY69_TOOLS = {
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
}

EXPECTED_DAY69_RESOURCES = {
    "agent-api://mcp/tool-registry",
    "agent-api://mcp/marketplace",
    "agent-api://graph/schema",
    "agent-api://docs/graphrag",
    "agent-api://docs/multi-agent",
    "agent-api://docs/mcp-plan",
    "agent-api://mcp/marketplace-discovery",
    "agent-api://mcp/security-report",
    "agent-api://mcp/endpoint-coverage",
}


def test_build_client_config_from_internal_marketplace_server():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )

    assert config.server_id == "agent-api-local"
    assert config.transport == "stdio"
    assert config.trust_level == "internal"
    assert config.ci_safe is True
    assert config.source == "marketplace"
    assert config.command == "python"
    assert config.args == ("-m", "src.app.mcp_integration.server")


def test_build_client_config_denies_external_server_for_ci_safe_principal():
    with pytest.raises(PermissionError) as exc_info:
        build_mcp_client_config_from_marketplace(
            server_id="external-filesystem-stdio",
            principal=get_ci_safe_mcp_principal(),
        )

    payload = json.loads(str(exc_info.value))
    assert payload["allowed"] is False
    assert payload["server_id"] == "external-filesystem-stdio"
    assert payload["reason"] == "missing_required_scopes"


def test_build_client_config_allows_external_server_for_manual_principal_without_launching():
    principal = MCPPrincipal(
        principal_id="external-manual-principal",
        scopes=("mcp:external:read",),
        allow_external_servers=True,
        allow_network=True,
    )

    config = build_mcp_client_config_from_marketplace(
        server_id="external-filesystem-stdio",
        principal=principal,
    )

    assert config.server_id == "external-filesystem-stdio"
    assert config.transport == "stdio"
    assert config.trust_level == "allowlisted_external"
    assert config.ci_safe is False
    assert config.command == "npx"


def test_mcp_client_wrapper_can_list_tools_from_local_server():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    tool_names = asyncio.run(wrapper.list_tools())

    assert set(tool_names) == EXPECTED_DAY69_TOOLS


def test_mcp_client_wrapper_can_list_resources_from_local_server():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    resource_uris = asyncio.run(wrapper.list_resources())

    assert set(resource_uris) == EXPECTED_DAY69_RESOURCES


def test_mcp_client_wrapper_can_call_registry_summary_tool():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_registry_summary",
            arguments={
                "trace_id": "test-day69-client-wrapper-registry-summary",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_registry_summary"
    assert payload["summary"]["tool_count"] == 10
    assert payload["summary"]["server_count"] == 3
    assert payload["summary"]["external_servers_enabled_by_default"] == []


def test_mcp_client_wrapper_can_read_marketplace_resource():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.read_resource(uri="agent-api://mcp/marketplace")
    )

    payload = extract_resource_json(result)

    assert payload["resource"] == "agent-api://mcp/marketplace"
    assert payload["marketplace"]["server_count"] == 3
    assert payload["marketplace"]["enabled_by_default"] == ["agent-api-local"]
    assert payload["marketplace"]["external_servers_enabled_by_default"] == []


def test_mcp_client_wrapper_discovers_capabilities():
    capability = asyncio.run(
        discover_mcp_server_capabilities(
            server_id="agent-api-local",
            principal=get_ci_safe_mcp_principal(),
        )
    )

    assert capability["server_id"] == "agent-api-local"
    assert capability["transport"] == "stdio"
    assert capability["trust_level"] == "internal"
    assert capability["tool_count"] == 10
    assert capability["resource_count"] == 9
    assert set(capability["tool_names"]) == EXPECTED_DAY69_TOOLS
    assert set(capability["resource_uris"]) == EXPECTED_DAY69_RESOURCES


def test_mcp_client_wrapper_rejects_non_stdio_transport():
    wrapper = MCPClientWrapper(
        MCPClientConfig(
            server_id="remote-http-placeholder",
            command="unused",
            args=(),
            transport="streamable_http",
            trust_level="allowlisted_external",
            ci_safe=False,
        )
    )

    with pytest.raises(NotImplementedError):
        asyncio.run(wrapper.list_tools())
