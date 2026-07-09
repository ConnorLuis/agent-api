from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl, TypeAdapter

from src.app.mcp_integration.marketplace import (
    MCPMarketplaceServer,
    authorize_marketplace_server_access,
    get_marketplace_server,
    serialize_marketplace_access_decision,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)


DEFAULT_MCP_SERVER_COMMAND = sys.executable
DEFAULT_MCP_SERVER_ARGS = ["-m", "src.app.mcp_integration.server"]


@dataclass(frozen=True)
class MCPClientConfig:
    server_id: str = "agent-api-local"
    command: str = DEFAULT_MCP_SERVER_COMMAND
    args: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_MCP_SERVER_ARGS))
    env: dict[str, str] | None = None
    transport: str = "stdio"
    trust_level: str = "internal"
    ci_safe: bool = True
    source: str = "direct"


@dataclass(frozen=True)
class MCPServerCapabilitySnapshot:
    server_id: str
    transport: str
    trust_level: str
    tool_names: tuple[str, ...]
    resource_uris: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "server_id": self.server_id,
            "transport": self.transport,
            "trust_level": self.trust_level,
            "tool_count": len(self.tool_names),
            "resource_count": len(self.resource_uris),
            "tool_names": list(self.tool_names),
            "resource_uris": list(self.resource_uris),
        }


def build_stdio_server_parameters(
    *,
    command: str | None = None,
    args: list[str] | tuple[str, ...] | None = None,
    env: dict[str, str] | None = None,
) -> StdioServerParameters:
    return StdioServerParameters(
        command=command or DEFAULT_MCP_SERVER_COMMAND,
        args=list(args or DEFAULT_MCP_SERVER_ARGS),
        env=env,
    )


def build_mcp_client_config_from_marketplace(
    *,
    server_id: str,
    principal: MCPPrincipal | None = None,
) -> MCPClientConfig:
    principal = principal or get_ci_safe_mcp_principal()
    server = get_marketplace_server(server_id)

    decision = authorize_marketplace_server_access(
        principal=principal,
        server=server,
    )

    if not decision.allowed:
        payload = serialize_marketplace_access_decision(decision)
        raise PermissionError(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    return _build_config_from_marketplace_server(server)


def _build_config_from_marketplace_server(
    server: MCPMarketplaceServer,
) -> MCPClientConfig:
    return MCPClientConfig(
        server_id=server.server_id,
        command=server.command,
        args=server.args,
        env=None,
        transport=server.transport,
        trust_level=server.trust_level,
        ci_safe=server.ci_safe,
        source="marketplace",
    )


class MCPClientWrapper:
    def __init__(self, config: MCPClientConfig | None = None) -> None:
        self.config = config or MCPClientConfig()

    def _stdio_server_parameters(self) -> StdioServerParameters:
        if self.config.transport != "stdio":
            raise NotImplementedError(
                f"Only stdio transport is supported by Day69 wrapper. "
                f"Got transport={self.config.transport!r}."
            )

        return build_stdio_server_parameters(
            command=self.config.command,
            args=self.config.args,
            env=self.config.env,
        )

    async def list_tools(self) -> list[str]:
        server_params = self._stdio_server_parameters()

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                return [tool.name for tool in response.tools]

    async def call_tool(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        server_params = self._stdio_server_parameters()

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments=arguments)

    async def list_resources(self) -> list[str]:
        server_params = self._stdio_server_parameters()

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_resources()
                return [str(resource.uri) for resource in response.resources]

    async def read_resource(
        self,
        *,
        uri: str,
    ) -> Any:
        server_params = self._stdio_server_parameters()
        resource_uri = TypeAdapter(AnyUrl).validate_python(uri)

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await session.read_resource(resource_uri)

    async def discover_capabilities(self) -> MCPServerCapabilitySnapshot:
        tool_names = await self.list_tools()
        resource_uris = await self.list_resources()

        return MCPServerCapabilitySnapshot(
            server_id=self.config.server_id,
            transport=self.config.transport,
            trust_level=self.config.trust_level,
            tool_names=tuple(tool_names),
            resource_uris=tuple(resource_uris),
        )


async def list_mcp_tools(
    *,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    wrapper = MCPClientWrapper(
        MCPClientConfig(
            command=command or DEFAULT_MCP_SERVER_COMMAND,
            args=tuple(args or DEFAULT_MCP_SERVER_ARGS),
            env=env,
            source="direct",
        )
    )
    return await wrapper.list_tools()


async def call_mcp_tool(
    *,
    tool_name: str,
    arguments: dict[str, Any],
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    wrapper = MCPClientWrapper(
        MCPClientConfig(
            command=command or DEFAULT_MCP_SERVER_COMMAND,
            args=tuple(args or DEFAULT_MCP_SERVER_ARGS),
            env=env,
            source="direct",
        )
    )
    return await wrapper.call_tool(
        tool_name=tool_name,
        arguments=arguments,
    )


async def list_mcp_resources(
    *,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    wrapper = MCPClientWrapper(
        MCPClientConfig(
            command=command or DEFAULT_MCP_SERVER_COMMAND,
            args=tuple(args or DEFAULT_MCP_SERVER_ARGS),
            env=env,
            source="direct",
        )
    )
    return await wrapper.list_resources()


async def read_mcp_resource(
    *,
    uri: str,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    wrapper = MCPClientWrapper(
        MCPClientConfig(
            command=command or DEFAULT_MCP_SERVER_COMMAND,
            args=tuple(args or DEFAULT_MCP_SERVER_ARGS),
            env=env,
            source="direct",
        )
    )
    return await wrapper.read_resource(uri=uri)


async def discover_mcp_server_capabilities(
    *,
    server_id: str = "agent-api-local",
    principal: MCPPrincipal | None = None,
) -> dict[str, Any]:
    config = build_mcp_client_config_from_marketplace(
        server_id=server_id,
        principal=principal,
    )
    wrapper = MCPClientWrapper(config)
    snapshot = await wrapper.discover_capabilities()
    return snapshot.to_dict()


def extract_text_content(tool_result: Any) -> str:
    content = getattr(tool_result, "content", None)
    if not content:
        raise ValueError("MCP tool result does not contain content.")

    first_content = content[0]
    text = getattr(first_content, "text", None)
    if text is None:
        raise ValueError("MCP tool result first content item does not contain text.")

    return text


def extract_json_content(tool_result: Any) -> dict[str, Any]:
    text = extract_text_content(tool_result)
    return json.loads(text)


def extract_resource_text(resource_result: Any) -> str:
    contents = getattr(resource_result, "contents", None)
    if not contents:
        raise ValueError("MCP resource result does not contain contents.")

    first_content = contents[0]
    text = getattr(first_content, "text", None)
    if text is None:
        raise ValueError("MCP resource result first content item does not contain text.")

    return text


def extract_resource_json(resource_result: Any) -> dict[str, Any]:
    return json.loads(extract_resource_text(resource_result))
