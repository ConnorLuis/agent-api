from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.app.mcp_integration.marketplace import (
    list_marketplace_servers,
    serialize_marketplace_server,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
)
from src.app.mcp_integration.registry import (
    MCPToolSpec,
    get_mcp_tool_spec,
    list_mcp_tool_names,
    list_mcp_tool_specs,
)


@dataclass(frozen=True)
class MCPSecurityPolicy:
    policy_name: str
    policy_version: str
    allowed_tool_names: tuple[str, ...]
    blocked_tool_names: tuple[str, ...] = field(default_factory=tuple)
    allowed_external_server_ids: tuple[str, ...] = ("agent-api-local",)
    require_graph_dry_run: bool = True
    block_destructive_tools: bool = True
    audit_enabled: bool = True


def build_default_mcp_security_policy() -> MCPSecurityPolicy:
    return MCPSecurityPolicy(
        policy_name="agent-api MCP security policy",
        policy_version="day70_mcp_security_policy_v1",
        allowed_tool_names=tuple(list_mcp_tool_names()),
        blocked_tool_names=(),
        allowed_external_server_ids=("agent-api-local",),
        require_graph_dry_run=True,
        block_destructive_tools=True,
        audit_enabled=True,
    )


def classify_mcp_tool_security(tool_spec: MCPToolSpec) -> dict[str, Any]:
    risk_flags: list[str] = []

    if tool_spec.read_only:
        risk_flags.append("read_only")
    else:
        risk_flags.extend(["write", "destructive"])

    if tool_spec.requires_network:
        risk_flags.extend(["external_access", "network"])

    if tool_spec.requires_neo4j:
        risk_flags.append("live_neo4j_capable")

    if tool_spec.category == "graphrag":
        risk_flags.append("graph_access")

    if tool_spec.risk_level in {"medium", "high"}:
        risk_flags.append(f"{tool_spec.risk_level}_risk")

    return {
        "tool_name": tool_spec.name,
        "category": tool_spec.category,
        "risk_level": tool_spec.risk_level,
        "read_only": tool_spec.read_only,
        "requires_network": tool_spec.requires_network,
        "requires_neo4j": tool_spec.requires_neo4j,
        "default_ci_safe": tool_spec.default_ci_safe,
        "required_scopes": list(tool_spec.required_scopes),
        "risk_flags": sorted(set(risk_flags)),
    }


def _build_audit_trace(
    *,
    trace_id: str,
    target_type: str,
    target_id: str,
    principal: MCPPrincipal,
    policy: MCPSecurityPolicy,
    allowed: bool,
    blocked_reasons: list[str],
) -> dict[str, Any]:
    return {
        "event_type": "mcp_security_decision",
        "trace_id": trace_id,
        "target_type": target_type,
        "target_id": target_id,
        "principal_id": principal.principal_id,
        "policy_version": policy.policy_version,
        "allowed": allowed,
        "blocked_reasons": blocked_reasons,
        "audit_enabled": policy.audit_enabled,
    }


def evaluate_mcp_tool_security(
    *,
    tool_name: str,
    principal: MCPPrincipal | None = None,
    policy: MCPSecurityPolicy | None = None,
    requested_write: bool = False,
    requested_network: bool = False,
    requested_live_neo4j: bool = False,
    requested_graph_mutation: bool = False,
    requested_dry_run: bool = True,
    trace_id: str = "mcp-security-tool-eval-trace",
) -> dict[str, Any]:
    principal = principal or get_ci_safe_mcp_principal()
    policy = policy or build_default_mcp_security_policy()

    blocked_reasons: list[str] = []
    missing_scopes: list[str] = []
    security_profile: dict[str, Any] | None = None

    try:
        tool_spec = get_mcp_tool_spec(tool_name)
        security_profile = classify_mcp_tool_security(tool_spec)
    except KeyError:
        tool_spec = None
        blocked_reasons.append("unknown_tool")

    if tool_spec is not None:
        required_scopes = set(tool_spec.required_scopes)
        principal_scopes = set(principal.scopes)
        missing_scopes = sorted(required_scopes - principal_scopes)

        if tool_name not in policy.allowed_tool_names:
            blocked_reasons.append("tool_not_in_allowlist")

        if tool_name in policy.blocked_tool_names:
            blocked_reasons.append("tool_explicitly_blocked")

        if missing_scopes:
            blocked_reasons.append("missing_required_scopes")

        if requested_write or not tool_spec.read_only:
            if not principal.allow_write_tools:
                blocked_reasons.append("write_tools_disabled_by_principal")
            if policy.block_destructive_tools:
                blocked_reasons.append("destructive_tools_blocked_by_policy")

        if requested_network or tool_spec.requires_network:
            if not principal.allow_network:
                blocked_reasons.append("network_access_disabled_by_principal")

        if requested_live_neo4j:
            if not principal.allow_live_neo4j:
                blocked_reasons.append("live_neo4j_disabled_by_principal")

        if requested_graph_mutation and policy.require_graph_dry_run and not requested_dry_run:
            blocked_reasons.append("graph_mutation_requires_dry_run")

    blocked_reasons = sorted(set(blocked_reasons))
    allowed = len(blocked_reasons) == 0

    return {
        "target_type": "tool",
        "tool_name": tool_name,
        "allowed": allowed,
        "reason": "allowed" if allowed else blocked_reasons[0],
        "blocked_reasons": blocked_reasons,
        "missing_scopes": missing_scopes,
        "requested_access": {
            "requested_write": requested_write,
            "requested_network": requested_network,
            "requested_live_neo4j": requested_live_neo4j,
            "requested_graph_mutation": requested_graph_mutation,
            "requested_dry_run": requested_dry_run,
        },
        "security_profile": security_profile,
        "audit_trace": _build_audit_trace(
            trace_id=trace_id,
            target_type="tool",
            target_id=tool_name,
            principal=principal,
            policy=policy,
            allowed=allowed,
            blocked_reasons=blocked_reasons,
        ),
    }


def evaluate_mcp_server_security(
    *,
    server_id: str,
    principal: MCPPrincipal | None = None,
    policy: MCPSecurityPolicy | None = None,
    trace_id: str = "mcp-security-server-eval-trace",
) -> dict[str, Any]:
    principal = principal or get_ci_safe_mcp_principal()
    policy = policy or build_default_mcp_security_policy()

    blocked_reasons: list[str] = []
    server_payload: dict[str, Any] | None = None

    servers = {
        server.server_id: server
        for server in list_marketplace_servers()
    }
    server = servers.get(server_id)

    if server is None:
        blocked_reasons.append("unknown_server")
    else:
        server_payload = serialize_marketplace_server(server)

        if server.trust_level != "internal":
            if not principal.allow_external_servers:
                blocked_reasons.append("external_servers_disabled_by_principal")

            if server_id not in policy.allowed_external_server_ids:
                blocked_reasons.append("external_server_not_in_allowlist")

        if server.requires_network and not principal.allow_network:
            blocked_reasons.append("network_access_disabled_by_principal")

    blocked_reasons = sorted(set(blocked_reasons))
    allowed = len(blocked_reasons) == 0

    return {
        "target_type": "server",
        "server_id": server_id,
        "allowed": allowed,
        "reason": "allowed" if allowed else blocked_reasons[0],
        "blocked_reasons": blocked_reasons,
        "server": server_payload,
        "audit_trace": _build_audit_trace(
            trace_id=trace_id,
            target_type="server",
            target_id=server_id,
            principal=principal,
            policy=policy,
            allowed=allowed,
            blocked_reasons=blocked_reasons,
        ),
    }


def build_mcp_security_report(
    *,
    principal: MCPPrincipal | None = None,
    policy: MCPSecurityPolicy | None = None,
    trace_id: str = "mcp-security-report-trace",
) -> dict[str, Any]:
    principal = principal or get_ci_safe_mcp_principal()
    policy = policy or build_default_mcp_security_policy()

    tool_profiles = [
        classify_mcp_tool_security(tool_spec)
        for tool_spec in list_mcp_tool_specs()
    ]

    tool_decisions = [
        evaluate_mcp_tool_security(
            tool_name=tool_spec.name,
            principal=principal,
            policy=policy,
            trace_id=f"{trace_id}:{tool_spec.name}",
        )
        for tool_spec in list_mcp_tool_specs()
    ]

    server_decisions = [
        evaluate_mcp_server_security(
            server_id=server.server_id,
            principal=principal,
            policy=policy,
            trace_id=f"{trace_id}:{server.server_id}",
        )
        for server in list_marketplace_servers()
    ]

    allowed_tool_names = [
        item["tool_name"]
        for item in tool_decisions
        if item["allowed"]
    ]
    denied_tool_names = [
        item["tool_name"]
        for item in tool_decisions
        if not item["allowed"]
    ]
    allowed_server_ids = [
        item["server_id"]
        for item in server_decisions
        if item["allowed"]
    ]
    denied_server_ids = [
        item["server_id"]
        for item in server_decisions
        if not item["allowed"]
    ]

    return {
        "report_name": "agent-api MCP security report",
        "report_version": "day70_mcp_security_report_v1",
        "policy": {
            "policy_name": policy.policy_name,
            "policy_version": policy.policy_version,
            "allowed_tool_names": list(policy.allowed_tool_names),
            "blocked_tool_names": list(policy.blocked_tool_names),
            "allowed_external_server_ids": list(policy.allowed_external_server_ids),
            "require_graph_dry_run": policy.require_graph_dry_run,
            "block_destructive_tools": policy.block_destructive_tools,
            "audit_enabled": policy.audit_enabled,
        },
        "principal": {
            "principal_id": principal.principal_id,
            "scopes": list(principal.scopes),
            "allow_external_servers": principal.allow_external_servers,
            "allow_write_tools": principal.allow_write_tools,
            "allow_live_neo4j": principal.allow_live_neo4j,
            "allow_network": principal.allow_network,
        },
        "summary": {
            "tool_count": len(tool_profiles),
            "allowed_tool_count": len(allowed_tool_names),
            "denied_tool_count": len(denied_tool_names),
            "allowed_tool_names": allowed_tool_names,
            "denied_tool_names": denied_tool_names,
            "server_count": len(server_decisions),
            "allowed_server_ids": allowed_server_ids,
            "denied_server_ids": denied_server_ids,
            "external_servers_allowed_by_default": [],
            "external_servers_executed_in_ci": False,
            "write_tools_enabled_in_ci": False,
            "live_neo4j_required_in_ci": False,
            "network_required_in_ci": False,
        },
        "tool_profiles": tool_profiles,
        "tool_decisions": tool_decisions,
        "server_decisions": server_decisions,
        "safety": {
            "ci_safe": True,
            "external_servers_executed_in_ci": False,
            "write_tools_enabled_in_ci": False,
            "destructive_tools_allowed_in_ci": False,
            "graph_mutation_requires_dry_run": policy.require_graph_dry_run,
            "audit_trace_enabled": policy.audit_enabled,
        },
    }
