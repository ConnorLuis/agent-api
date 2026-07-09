from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    authorize_mcp_tool,
    get_ci_safe_mcp_principal,
    serialize_authorization_decision,
)
from src.app.mcp_integration.registry import get_mcp_tool_spec


def test_ci_safe_principal_allows_core_read_tools():
    principal = get_ci_safe_mcp_principal()

    for tool_name in [
        "agentic_rag_query",
        "graph_fusion_retrieve",
        "multi_agent_eval_trace",
    ]:
        decision = authorize_mcp_tool(
            principal=principal,
            tool_spec=get_mcp_tool_spec(tool_name),
        )

        assert decision.allowed is True
        assert decision.reason == "allowed"
        assert decision.enforced_dry_run is False


def test_permission_denies_missing_scope():
    principal = MCPPrincipal(
        principal_id="limited-principal",
        scopes=("mcp:tools:list",),
    )

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=get_mcp_tool_spec("agentic_rag_query"),
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_scopes"
    assert decision.denied_scopes == ("mcp:rag:read",)


def test_permission_enforces_dry_run_for_live_neo4j_by_default():
    principal = get_ci_safe_mcp_principal()

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=get_mcp_tool_spec("graph_fusion_retrieve"),
        requested_live_neo4j=True,
    )

    assert decision.allowed is True
    assert decision.reason == "allowed_with_dry_run_enforced_for_live_neo4j"
    assert decision.enforced_dry_run is True


def test_permission_denies_write_tools_for_ci_safe_principal():
    principal = get_ci_safe_mcp_principal()

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=get_mcp_tool_spec("agentic_rag_query"),
        requested_write=True,
    )

    assert decision.allowed is False
    assert decision.reason == "write_tools_are_not_allowed"
    assert decision.enforced_dry_run is True


def test_authorization_decision_serialization_is_json_ready():
    principal = get_ci_safe_mcp_principal()
    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=get_mcp_tool_spec("multi_agent_eval_trace"),
    )

    payload = serialize_authorization_decision(decision)

    assert payload == {
        "allowed": True,
        "reason": "allowed",
        "tool_name": "multi_agent_eval_trace",
        "principal_id": "ci-safe-principal",
        "risk_level": "low",
        "enforced_dry_run": False,
        "denied_scopes": [],
    }
