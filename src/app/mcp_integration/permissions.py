from __future__ import annotations

from dataclasses import dataclass, field

from src.app.mcp_integration.registry import MCPToolSpec


ERP_DIAGNOSIS_READ_SCOPES: tuple[str, ...] = (
    "mcp:erp:user_access:read",
    "mcp:erp:document:read",
    "mcp:erp:permission:read",
    "mcp:erp:approval:read",
    "mcp:erp:transfer:read",
)


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
        "mcp:endpoints:read",
        "mcp:resources:read",
        *ERP_DIAGNOSIS_READ_SCOPES,
    ),
    allow_external_servers=False,
    allow_write_tools=False,
    allow_live_neo4j=False,
    allow_network=False,
)


ERP_DIAGNOSIS_MCP_PRINCIPAL = MCPPrincipal(
    principal_id="erp-diagnosis-readonly-principal",
    scopes=(
        "mcp:tools:list",
        "mcp:resources:read",
        *ERP_DIAGNOSIS_READ_SCOPES,
    ),
    allow_external_servers=False,
    allow_write_tools=False,
    allow_live_neo4j=False,
    allow_network=False,
)


ERP_DIAGNOSIS_LOOPBACK_HTTP_PRINCIPAL = MCPPrincipal(
    principal_id="erp-diagnosis-loopback-http-principal",
    scopes=(
        "mcp:tools:list",
        "mcp:resources:read",
        *ERP_DIAGNOSIS_READ_SCOPES,
    ),
    allow_external_servers=False,
    allow_write_tools=False,
    allow_live_neo4j=False,
    # The paired SyntheticERPHttpReadService validates that its base URL is
    # loopback-only before any request is made.
    allow_network=True,
)


def get_ci_safe_mcp_principal() -> MCPPrincipal:
    return CI_SAFE_MCP_PRINCIPAL


def get_erp_diagnosis_mcp_principal() -> MCPPrincipal:
    """Return the no-network least-privilege principal used by default."""

    return ERP_DIAGNOSIS_MCP_PRINCIPAL


def get_erp_diagnosis_loopback_http_mcp_principal() -> MCPPrincipal:
    """
    Return the read-only principal used only by the trusted loopback HTTP adapter.

    Network permission alone is not the host allowlist: the HTTP adapter itself
    enforces localhost / 127.0.0.1 / ::1 and refuses arbitrary remote hosts.
    """

    return ERP_DIAGNOSIS_LOOPBACK_HTTP_PRINCIPAL


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
