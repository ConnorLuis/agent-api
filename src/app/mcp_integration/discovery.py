from __future__ import annotations

from typing import Any

from src.app.mcp_integration.marketplace import (
    authorize_marketplace_server_access,
    list_marketplace_servers,
    serialize_marketplace_access_decision,
    serialize_marketplace_server,
    summarize_marketplace,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)


def _build_manual_validation_command(server_payload: dict[str, Any]) -> dict[str, Any]:
    command = server_payload["command"]
    args = server_payload["args"]

    return {
        "server_id": server_payload["server_id"],
        "transport": server_payload["transport"],
        "manual_only": True,
        "ci_safe": False,
        "command": command,
        "args": args,
        "shell_preview": " ".join([command, *args]),
        "note": (
            "Manual validation command only. It is not executed by CI and should be "
            "used only after explicitly allowing external MCP servers locally."
        ),
    }


def build_marketplace_discovery_report(
    *,
    principal: MCPPrincipal | None = None,
) -> dict[str, Any]:
    principal = principal or get_ci_safe_mcp_principal()
    servers = list_marketplace_servers()

    server_reports = []
    manual_validation_commands = []

    for server in servers:
        server_payload = serialize_marketplace_server(server)
        decision = authorize_marketplace_server_access(
            principal=principal,
            server=server,
        )
        access_payload = serialize_marketplace_access_decision(decision)

        launch_policy = {
            "enabled_by_default": server.enabled_by_default,
            "ci_safe": server.ci_safe,
            "requires_network": server.requires_network,
            "requires_install": server.requires_install,
            "will_launch_in_ci": server.ci_safe and server.enabled_by_default,
            "external_launch_disabled_by_default": (
                server.trust_level != "internal" and not server.enabled_by_default
            ),
            "capability_discovery_mode": (
                "live_local_stdio_discovery"
                if server.server_id == "agent-api-local"
                else "manual_only_not_executed_in_ci"
            ),
        }

        if server.trust_level != "internal":
            manual_validation_commands.append(
                _build_manual_validation_command(server_payload)
            )

        server_reports.append(
            {
                "server": server_payload,
                "access_decision": access_payload,
                "launch_policy": launch_policy,
            }
        )

    marketplace_summary = summarize_marketplace()

    return {
        "report_name": "agent-api MCP marketplace discovery report",
        "report_version": "day69_marketplace_discovery_v1",
        "principal": {
            "principal_id": principal.principal_id,
            "scopes": list(principal.scopes),
            "allow_external_servers": principal.allow_external_servers,
            "allow_write_tools": principal.allow_write_tools,
            "allow_live_neo4j": principal.allow_live_neo4j,
            "allow_network": principal.allow_network,
        },
        "summary": {
            "server_count": marketplace_summary["server_count"],
            "enabled_by_default": marketplace_summary["enabled_by_default"],
            "ci_safe_servers": marketplace_summary["ci_safe_servers"],
            "external_server_ids": marketplace_summary["external_server_ids"],
            "external_servers_enabled_by_default": marketplace_summary[
                "external_servers_enabled_by_default"
            ],
            "manual_only_servers": marketplace_summary["manual_only_servers"],
            "ci_external_server_launches": [],
            "ci_boundary": (
                "CI discovers and exercises only the internal agent-api-local MCP server. "
                "External servers are cataloged but disabled by default."
            ),
        },
        "servers": server_reports,
        "manual_validation_commands": manual_validation_commands,
        "safety": {
            "external_servers_executed_in_ci": False,
            "network_required_in_ci": False,
            "live_neo4j_required_in_ci": False,
            "write_tools_enabled_in_ci": False,
        },
    }
