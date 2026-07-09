from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from src.app.mcp_integration.permissions import MCPPrincipal


MCPServerTrustLevel = Literal[
    "internal",
    "allowlisted_external",
    "blocked_external",
]

MCPServerTransport = Literal[
    "stdio",
    "sse",
    "streamable_http",
]


@dataclass(frozen=True)
class MCPMarketplaceServer:
    server_id: str
    display_name: str
    description: str
    command: str
    args: tuple[str, ...] = field(default_factory=tuple)
    transport: MCPServerTransport = "stdio"
    trust_level: MCPServerTrustLevel = "internal"
    enabled_by_default: bool = False
    ci_safe: bool = True
    requires_network: bool = False
    requires_install: bool = False
    required_scopes: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)
    documentation_url: str | None = None


@dataclass(frozen=True)
class MCPMarketplaceAccessDecision:
    allowed: bool
    reason: str
    server_id: str
    principal_id: str
    trust_level: MCPServerTrustLevel
    transport: MCPServerTransport
    denied_scopes: tuple[str, ...] = field(default_factory=tuple)


LOCAL_MCP_MARKETPLACE: tuple[MCPMarketplaceServer, ...] = (
    MCPMarketplaceServer(
        server_id="agent-api-local",
        display_name="agent-api local MCP server",
        description=(
            "Local MCP server exposing agent-api Agentic RAG, GraphRAG, "
            "Multi-Agent, verification, evaluation, registry, and resource tools."
        ),
        command="python",
        args=("-m", "src.app.mcp_integration.server"),
        transport="stdio",
        trust_level="internal",
        enabled_by_default=True,
        ci_safe=True,
        requires_network=False,
        requires_install=False,
        required_scopes=("mcp:tools:list", "mcp:resources:read"),
        tags=("agent-api", "internal", "ci-safe", "stdio"),
    ),
    MCPMarketplaceServer(
        server_id="external-filesystem-stdio",
        display_name="External filesystem MCP server",
        description=(
            "Disabled-by-default external stdio MCP server catalog entry. "
            "It is intended for local/manual integration only and is never used in CI."
        ),
        command="npx",
        args=("-y", "@modelcontextprotocol/server-filesystem", "."),
        transport="stdio",
        trust_level="allowlisted_external",
        enabled_by_default=False,
        ci_safe=False,
        requires_network=True,
        requires_install=True,
        required_scopes=("mcp:external:read",),
        tags=("external", "filesystem", "manual-only", "stdio"),
    ),
    MCPMarketplaceServer(
        server_id="external-memory-stdio",
        display_name="External memory MCP server",
        description=(
            "Disabled-by-default external stdio MCP server catalog entry. "
            "It is intended for local/manual integration only and is never used in CI."
        ),
        command="npx",
        args=("-y", "@modelcontextprotocol/server-memory"),
        transport="stdio",
        trust_level="allowlisted_external",
        enabled_by_default=False,
        ci_safe=False,
        requires_network=True,
        requires_install=True,
        required_scopes=("mcp:external:read",),
        tags=("external", "memory", "manual-only", "stdio"),
    ),
)


def list_marketplace_servers() -> list[MCPMarketplaceServer]:
    return list(LOCAL_MCP_MARKETPLACE)


def get_marketplace_server(server_id: str) -> MCPMarketplaceServer:
    for server in LOCAL_MCP_MARKETPLACE:
        if server.server_id == server_id:
            return server

    raise KeyError(f"Unknown MCP marketplace server: {server_id}")


def list_enabled_marketplace_servers() -> list[MCPMarketplaceServer]:
    return [
        server
        for server in LOCAL_MCP_MARKETPLACE
        if server.enabled_by_default
    ]


def list_ci_safe_marketplace_servers() -> list[MCPMarketplaceServer]:
    return [
        server
        for server in LOCAL_MCP_MARKETPLACE
        if server.ci_safe
    ]


def authorize_marketplace_server_access(
    *,
    principal: MCPPrincipal,
    server: MCPMarketplaceServer,
) -> MCPMarketplaceAccessDecision:
    denied_scopes = tuple(
        scope for scope in server.required_scopes if scope not in principal.scopes
    )

    if denied_scopes:
        return MCPMarketplaceAccessDecision(
            allowed=False,
            reason="missing_required_scopes",
            server_id=server.server_id,
            principal_id=principal.principal_id,
            trust_level=server.trust_level,
            transport=server.transport,
            denied_scopes=denied_scopes,
        )

    if server.trust_level == "blocked_external":
        return MCPMarketplaceAccessDecision(
            allowed=False,
            reason="blocked_external_server",
            server_id=server.server_id,
            principal_id=principal.principal_id,
            trust_level=server.trust_level,
            transport=server.transport,
        )

    if server.trust_level == "internal":
        return MCPMarketplaceAccessDecision(
            allowed=True,
            reason="allowed_internal_server",
            server_id=server.server_id,
            principal_id=principal.principal_id,
            trust_level=server.trust_level,
            transport=server.transport,
        )

    if server.trust_level == "allowlisted_external":
        if not principal.allow_external_servers:
            return MCPMarketplaceAccessDecision(
                allowed=False,
                reason="external_servers_are_not_allowed",
                server_id=server.server_id,
                principal_id=principal.principal_id,
                trust_level=server.trust_level,
                transport=server.transport,
            )

        if server.requires_network and not principal.allow_network:
            return MCPMarketplaceAccessDecision(
                allowed=False,
                reason="network_access_is_not_allowed_for_external_server",
                server_id=server.server_id,
                principal_id=principal.principal_id,
                trust_level=server.trust_level,
                transport=server.transport,
            )

        return MCPMarketplaceAccessDecision(
            allowed=True,
            reason="allowed_allowlisted_external_server",
            server_id=server.server_id,
            principal_id=principal.principal_id,
            trust_level=server.trust_level,
            transport=server.transport,
        )

    return MCPMarketplaceAccessDecision(
        allowed=False,
        reason="unknown_trust_level",
        server_id=server.server_id,
        principal_id=principal.principal_id,
        trust_level=server.trust_level,
        transport=server.transport,
    )


def serialize_marketplace_server(server: MCPMarketplaceServer) -> dict:
    return {
        "server_id": server.server_id,
        "display_name": server.display_name,
        "description": server.description,
        "command": server.command,
        "args": list(server.args),
        "transport": server.transport,
        "trust_level": server.trust_level,
        "enabled_by_default": server.enabled_by_default,
        "ci_safe": server.ci_safe,
        "requires_network": server.requires_network,
        "requires_install": server.requires_install,
        "required_scopes": list(server.required_scopes),
        "tags": list(server.tags),
        "documentation_url": server.documentation_url,
    }


def serialize_marketplace_access_decision(
    decision: MCPMarketplaceAccessDecision,
) -> dict:
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
        "server_id": decision.server_id,
        "principal_id": decision.principal_id,
        "trust_level": decision.trust_level,
        "transport": decision.transport,
        "denied_scopes": list(decision.denied_scopes),
    }


def summarize_marketplace() -> dict:
    servers = list_marketplace_servers()
    enabled_servers = list_enabled_marketplace_servers()
    ci_safe_servers = list_ci_safe_marketplace_servers()

    return {
        "server_count": len(servers),
        "server_ids": [server.server_id for server in servers],
        "enabled_by_default": [
            server.server_id for server in enabled_servers
        ],
        "ci_safe_servers": [
            server.server_id for server in ci_safe_servers
        ],
        "external_server_ids": [
            server.server_id
            for server in servers
            if server.trust_level != "internal"
        ],
        "external_servers_enabled_by_default": [
            server.server_id
            for server in servers
            if server.trust_level != "internal" and server.enabled_by_default
        ],
        "manual_only_servers": [
            server.server_id
            for server in servers
            if not server.ci_safe
        ],
        "transports": sorted({server.transport for server in servers}),
    }
