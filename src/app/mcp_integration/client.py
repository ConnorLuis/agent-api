from __future__ import annotations

import json
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


DEFAULT_MCP_SERVER_COMMAND = sys.executable
DEFAULT_MCP_SERVER_ARGS = ["-m", "src.app.mcp_integration.server"]


def build_stdio_server_parameters(
    *,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> StdioServerParameters:
    return StdioServerParameters(
        command=command or DEFAULT_MCP_SERVER_COMMAND,
        args=args or DEFAULT_MCP_SERVER_ARGS,
        env=env,
    )


async def list_mcp_tools(
    *,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    server_params = build_stdio_server_parameters(
        command=command,
        args=args,
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()
            return [tool.name for tool in response.tools]


async def call_mcp_tool(
    *,
    tool_name: str,
    arguments: dict[str, Any],
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    server_params = build_stdio_server_parameters(
        command=command,
        args=args,
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments=arguments)


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
