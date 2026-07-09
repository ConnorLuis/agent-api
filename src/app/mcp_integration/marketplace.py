from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


MCPServerTrustLevel = Literal[
    "internal",
    "allowlisted_external",
    "blocked_external",
]


@dataclass(frozen=True)
class MCPMarketplaceServer:
    server_id: str
    display_name: str
    description: str
    command: str
    args: tuple[str, ...] = field(default_factory=tuple)
    trust_level: MCPServerTrustLevel = "internal"
    enabled_by_default: bool = False
    ci_safe: bool = True


LOCAL_MCP_MARKETPLACE: tuple[MCPMarketplaceServer, ...] = (
    MCPMarketplaceServer(
        server_id="agent-api-local",
        display_name="agent-api local MCP server",
        description=(
            "Local MCP server exposing agent-api Agentic RAG, GraphRAG, and Multi-Agent tools."
        ),
        command="python",
        args=("-m", "src.app.mcp_integration.server"),
        trust_level="internal",
        enabled_by_default=True,
        ci_safe=True,
    ),
)


def list_marketplace_servers() -> list[MCPMarketplaceServer]:
    return list(LOCAL_MCP_MARKETPLACE)


def summarize_marketplace() -> dict:
    servers = list_marketplace_servers()
    return {
        "server_count": len(servers),
        "server_ids": [server.server_id for server in servers],
        "enabled_by_default": [
            server.server_id for server in servers if server.enabled_by_default
        ],
        "ci_safe_servers": [
            server.server_id for server in servers if server.ci_safe
        ],
        "external_servers_enabled_by_default": [
            server.server_id
            for server in servers
            if server.trust_level != "internal" and server.enabled_by_default
        ],
    }
