from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.app.graph.schema import get_graph_schema
from src.app.mcp_integration.discovery import build_marketplace_discovery_report
from src.app.mcp_integration.marketplace import summarize_marketplace
from src.app.mcp_integration.registry import summarize_mcp_tool_registry


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)


def read_markdown_file(relative_path: str) -> str:
    path = PROJECT_ROOT / relative_path

    if not path.exists():
        return f"# Missing resource\n\nFile not found: `{relative_path}`\n"

    return path.read_text(encoding="utf-8")


def get_mcp_tool_registry_resource() -> str:
    return _json_text(
        {
            "resource": "agent-api://mcp/tool-registry",
            "description": "Current agent-api MCP tool registry summary.",
            "registry": summarize_mcp_tool_registry(),
        }
    )


def get_mcp_marketplace_resource() -> str:
    return _json_text(
        {
            "resource": "agent-api://mcp/marketplace",
            "description": "Current agent-api local MCP marketplace catalog summary.",
            "marketplace": summarize_marketplace(),
        }
    )


def get_mcp_marketplace_discovery_resource() -> str:
    return _json_text(
        {
            "resource": "agent-api://mcp/marketplace-discovery",
            "description": "CI-safe MCP marketplace discovery report.",
            "discovery_report": build_marketplace_discovery_report(),
        }
    )


def get_graph_schema_resource() -> str:
    schema = get_graph_schema()

    return _json_text(
        {
            "resource": "agent-api://graph/schema",
            "description": "Current GraphRAG schema exposed as an MCP resource.",
            "schema": schema,
        }
    )


def get_graphrag_docs_resource() -> str:
    return read_markdown_file("docs/GRAPHRAG.md")


def get_multi_agent_docs_resource() -> str:
    return read_markdown_file("docs/MULTI_AGENT.md")


def get_mcp_plan_resource() -> str:
    return """# MCP Integration Plan

## Current status

Day67 completed MCP Foundation.

Day68 expands MCP core tools and resources.

## Completed in Day67

- Official MCP Python SDK installed and pinned.
- Standard FastMCP server.
- Real stdio MCP client.
- MCP tool registry foundation.
- MCP permission foundation.
- Local MCP marketplace foundation.
- Three core MCP tools:
  - agentic_rag_query
  - graph_fusion_retrieve
  - multi_agent_eval_trace

## Day68 target

- Expand MCP tools.
- Add MCP resources.
- Add MCP client resource reading.
- Keep CI-safe boundaries.
- Keep graph_fusion non-default.

## Future milestones

Day69:
  Complete MCP client wrapper, marketplace discovery report, and external server marketplace.

Day70:
  Advanced MCP permission and security layer.

Day71:
  Broader MCP endpoint coverage.

Day72:
  Main Agent MCP integration with config-controlled fallback.
"""
