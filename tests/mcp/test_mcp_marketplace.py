from src.app.mcp_integration.marketplace import (
    authorize_marketplace_server_access,
    get_marketplace_server,
    list_ci_safe_marketplace_servers,
    list_enabled_marketplace_servers,
    list_marketplace_servers,
    serialize_marketplace_access_decision,
    summarize_marketplace,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)


def test_marketplace_contains_internal_and_external_catalog_entries():
    servers = list_marketplace_servers()
    server_ids = [server.server_id for server in servers]

    assert "agent-api-local" in server_ids
    assert "external-filesystem-stdio" in server_ids
    assert "external-memory-stdio" in server_ids


def test_local_marketplace_keeps_agent_api_local_enabled_and_ci_safe():
    server = get_marketplace_server("agent-api-local")

    assert server.server_id == "agent-api-local"
    assert server.trust_level == "internal"
    assert server.transport == "stdio"
    assert server.enabled_by_default is True
    assert server.ci_safe is True
    assert server.requires_network is False


def test_external_marketplace_servers_are_disabled_by_default_and_not_ci_safe():
    filesystem_server = get_marketplace_server("external-filesystem-stdio")
    memory_server = get_marketplace_server("external-memory-stdio")

    for server in [filesystem_server, memory_server]:
        assert server.trust_level == "allowlisted_external"
        assert server.enabled_by_default is False
        assert server.ci_safe is False
        assert server.requires_network is True
        assert server.requires_install is True


def test_enabled_and_ci_safe_server_lists_only_include_local_server():
    enabled_servers = list_enabled_marketplace_servers()
    ci_safe_servers = list_ci_safe_marketplace_servers()

    assert [server.server_id for server in enabled_servers] == ["agent-api-local"]
    assert [server.server_id for server in ci_safe_servers] == ["agent-api-local"]


def test_marketplace_summary_keeps_external_servers_disabled_by_default():
    summary = summarize_marketplace()

    assert summary["server_count"] == 3
    assert summary["enabled_by_default"] == ["agent-api-local"]
    assert summary["ci_safe_servers"] == ["agent-api-local"]
    assert set(summary["external_server_ids"]) == {
        "external-filesystem-stdio",
        "external-memory-stdio",
    }
    assert summary["external_servers_enabled_by_default"] == []
    assert set(summary["manual_only_servers"]) == {
        "external-filesystem-stdio",
        "external-memory-stdio",
    }


def test_ci_safe_principal_allows_internal_server_access():
    principal = get_ci_safe_mcp_principal()
    server = get_marketplace_server("agent-api-local")

    decision = authorize_marketplace_server_access(
        principal=principal,
        server=server,
    )

    assert decision.allowed is True
    assert decision.reason == "allowed_internal_server"
    assert decision.server_id == "agent-api-local"


def test_ci_safe_principal_denies_external_server_access():
    principal = get_ci_safe_mcp_principal()
    server = get_marketplace_server("external-filesystem-stdio")

    decision = authorize_marketplace_server_access(
        principal=principal,
        server=server,
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_scopes"
    assert decision.denied_scopes == ("mcp:external:read",)


def test_external_principal_still_requires_network_permission():
    principal = MCPPrincipal(
        principal_id="external-no-network-principal",
        scopes=("mcp:external:read",),
        allow_external_servers=True,
        allow_network=False,
    )
    server = get_marketplace_server("external-filesystem-stdio")

    decision = authorize_marketplace_server_access(
        principal=principal,
        server=server,
    )

    assert decision.allowed is False
    assert decision.reason == "network_access_is_not_allowed_for_external_server"


def test_external_principal_can_access_allowlisted_external_server_when_enabled():
    principal = MCPPrincipal(
        principal_id="external-manual-principal",
        scopes=("mcp:external:read",),
        allow_external_servers=True,
        allow_network=True,
    )
    server = get_marketplace_server("external-filesystem-stdio")

    decision = authorize_marketplace_server_access(
        principal=principal,
        server=server,
    )

    assert decision.allowed is True
    assert decision.reason == "allowed_allowlisted_external_server"

    payload = serialize_marketplace_access_decision(decision)
    assert payload["allowed"] is True
    assert payload["server_id"] == "external-filesystem-stdio"
