from src.app.mcp_integration.marketplace import (
    list_marketplace_servers,
    summarize_marketplace,
)


def test_local_marketplace_contains_agent_api_local_server():
    servers = list_marketplace_servers()

    assert len(servers) == 1
    assert servers[0].server_id == "agent-api-local"
    assert servers[0].trust_level == "internal"
    assert servers[0].enabled_by_default is True
    assert servers[0].ci_safe is True


def test_marketplace_does_not_enable_external_servers_by_default():
    summary = summarize_marketplace()

    assert summary["server_count"] == 1
    assert summary["server_ids"] == ["agent-api-local"]
    assert summary["enabled_by_default"] == ["agent-api-local"]
    assert summary["ci_safe_servers"] == ["agent-api-local"]
    assert summary["external_servers_enabled_by_default"] == []
