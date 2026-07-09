from __future__ import annotations

from dataclasses import dataclass, field

from src.app.mcp_integration.registry import MCPToolSpec


@dataclass(frozen=True)
class MCPPrincipal:
    principal_id: str
    scopes: tuple[str, ...] = field(default_factory=tuple)
    allow_external_servers: bool = False
    allow_write_tools: bool = False
    allow_live_neo4j: bool = False
    allow_network: bool = False


@dataclass(frozen=True)
class MCPAuthorizationDecision:
    allowed: bool
    reason: str
    tool_name: str
    principal_id: str
    risk_level: str
    enforced_dry_run: bool
    denied_scopes: tuple[str, ...] = field(default_factory=tuple)


CI_SAFE_MCP_PRINCIPAL = MCPPrincipal(
    principal_id="ci-safe-principal",
    scopes=(
        "mcp:tools:list",
        "mcp:rag:read",
        "mcp:graph:read",
        "mcp:multi_agent:read",
        "mcp:verification:read",
        "mcp:evaluation:read",
        "mcp:system:read",
        "mcp:marketplace:read",
        "mcp:security:read",
        "mcp:resources:read",
    ),
    allow_external_servers=False,
    allow_write_tools=False,
    allow_live_neo4j=False,
    allow_network=False,
)


def get_ci_safe_mcp_principal() -> MCPPrincipal:
    return CI_SAFE_MCP_PRINCIPAL


def authorize_mcp_tool(
    *,
    principal: MCPPrincipal,
    tool_spec: MCPToolSpec,
    requested_live_neo4j: bool = False,
    requested_network: bool = False,
    requested_write: bool = False,
) -> MCPAuthorizationDecision:
    denied_scopes = tuple(
        scope for scope in tool_spec.required_scopes if scope not in principal.scopes
    )

    if denied_scopes:
        return MCPAuthorizationDecision(
            allowed=False,
            reason="missing_required_scopes",
            tool_name=tool_spec.name,
            principal_id=principal.principal_id,
            risk_level=tool_spec.risk_level,
            enforced_dry_run=True,
            denied_scopes=denied_scopes,
        )

    if requested_write and (not principal.allow_write_tools or tool_spec.read_only):
        return MCPAuthorizationDecision(
            allowed=False,
            reason="write_tools_are_not_allowed",
            tool_name=tool_spec.name,
            principal_id=principal.principal_id,
            risk_level=tool_spec.risk_level,
            enforced_dry_run=True,
        )

    if requested_network and not principal.allow_network:
        return MCPAuthorizationDecision(
            allowed=False,
            reason="network_access_is_not_allowed",
            tool_name=tool_spec.name,
            principal_id=principal.principal_id,
            risk_level=tool_spec.risk_level,
            enforced_dry_run=True,
        )

    if requested_live_neo4j and not principal.allow_live_neo4j:
        return MCPAuthorizationDecision(
            allowed=True,
            reason="allowed_with_dry_run_enforced_for_live_neo4j",
            tool_name=tool_spec.name,
            principal_id=principal.principal_id,
            risk_level=tool_spec.risk_level,
            enforced_dry_run=True,
        )

    return MCPAuthorizationDecision(
        allowed=True,
        reason="allowed",
        tool_name=tool_spec.name,
        principal_id=principal.principal_id,
        risk_level=tool_spec.risk_level,
        enforced_dry_run=False,
    )


def serialize_authorization_decision(
    decision: MCPAuthorizationDecision,
) -> dict:
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
        "tool_name": decision.tool_name,
        "principal_id": decision.principal_id,
        "risk_level": decision.risk_level,
        "enforced_dry_run": decision.enforced_dry_run,
        "denied_scopes": list(decision.denied_scopes),
    }
