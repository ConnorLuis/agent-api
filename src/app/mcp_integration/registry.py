from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


MCPToolCategory = Literal[
    "rag",
    "graphrag",
    "multi_agent",
    "observability",
    "evaluation",
    "verification",
    "system",
]

MCPRiskLevel = Literal[
    "low",
    "medium",
    "high",
]


@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    description: str
    category: MCPToolCategory
    risk_level: MCPRiskLevel
    read_only: bool
    requires_network: bool
    requires_neo4j: bool
    default_ci_safe: bool
    required_scopes: tuple[str, ...] = field(default_factory=tuple)


CORE_MCP_TOOL_SPECS: tuple[MCPToolSpec, ...] = (
    MCPToolSpec(
        name="agentic_rag_query",
        description=(
            "Run the existing Agentic RAG debug workflow through a standard MCP tool boundary."
        ),
        category="rag",
        risk_level="low",
        read_only=True,
        requires_network=False,
        requires_neo4j=False,
        default_ci_safe=True,
        required_scopes=("mcp:rag:read",),
    ),
    MCPToolSpec(
        name="graph_fusion_retrieve",
        description=(
            "Run the existing GraphRAG + VectorRAG fusion retrieval workflow through a standard MCP tool boundary."
        ),
        category="graphrag",
        risk_level="medium",
        read_only=True,
        requires_network=False,
        requires_neo4j=True,
        default_ci_safe=True,
        required_scopes=("mcp:graph:read",),
    ),
    MCPToolSpec(
        name="multi_agent_eval_trace",
        description=(
            "Run the deterministic Multi-Agent eval / trace workflow through a standard MCP tool boundary."
        ),
        category="multi_agent",
        risk_level="low",
        read_only=True,
        requires_network=False,
        requires_neo4j=False,
        default_ci_safe=True,
        required_scopes=("mcp:multi_agent:read",),
    ),
    MCPToolSpec(
        name="answer_verify",
        description=(
            "Run Agentic RAG answer verification through a standard MCP tool boundary."
        ),
        category="verification",
        risk_level="low",
        read_only=True,
        requires_network=False,
        requires_neo4j=True,
        default_ci_safe=True,
        required_scopes=("mcp:verification:read",),
    ),
    MCPToolSpec(
        name="rag_backend_eval",
        description=(
            "Run RAG backend evaluation and comparison through a standard MCP tool boundary."
        ),
        category="evaluation",
        risk_level="medium",
        read_only=True,
        requires_network=False,
        requires_neo4j=True,
        default_ci_safe=True,
        required_scopes=("mcp:evaluation:read",),
    ),
    MCPToolSpec(
        name="mcp_registry_summary",
        description=(
            "Return the current MCP tool registry, permission, and local marketplace summary."
        ),
        category="system",
        risk_level="low",
        read_only=True,
        requires_network=False,
        requires_neo4j=False,
        default_ci_safe=True,
        required_scopes=("mcp:system:read",),
    ),
)


def list_mcp_tool_specs() -> list[MCPToolSpec]:
    return list(CORE_MCP_TOOL_SPECS)


def get_mcp_tool_spec(tool_name: str) -> MCPToolSpec:
    for spec in CORE_MCP_TOOL_SPECS:
        if spec.name == tool_name:
            return spec

    raise KeyError(f"Unknown MCP tool: {tool_name}")


def list_mcp_tool_names() -> list[str]:
    return [spec.name for spec in CORE_MCP_TOOL_SPECS]


def summarize_mcp_tool_registry() -> dict:
    specs = list_mcp_tool_specs()
    return {
        "tool_count": len(specs),
        "tool_names": [spec.name for spec in specs],
        "categories": sorted({spec.category for spec in specs}),
        "ci_safe_tool_names": [
            spec.name for spec in specs if spec.default_ci_safe
        ],
        "read_only_tool_names": [
            spec.name for spec in specs if spec.read_only
        ],
        "requires_neo4j_tool_names": [
            spec.name for spec in specs if spec.requires_neo4j
        ],
    }
