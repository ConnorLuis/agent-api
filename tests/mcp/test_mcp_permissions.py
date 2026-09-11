from src.app.mcp_integration.permissions import (
    ERP_DIAGNOSIS_READ_SCOPES,
    MCPPrincipal,
    authorize_mcp_tool,
    get_ci_safe_mcp_principal,
    get_erp_diagnosis_mcp_principal,
    serialize_authorization_decision,
)
from src.app.mcp_integration.registry import get_mcp_tool_spec


def test_ci_safe_principal_allows_core_read_tools():
    principal = get_ci_safe_mcp_principal()

    for tool_name in [
        "agentic_rag_query",
        "graph_fusion_retrieve",
        "multi_agent_eval_trace",
        "erp_check_operation_permission",
    ]:
        decision = authorize_mcp_tool(
            principal=principal,
            tool_spec=get_mcp_tool_spec(tool_name),
        )

        assert decision.allowed is True
        assert decision.reason == "allowed"
        assert decision.enforced_dry_run is False


def test_erp_diagnosis_principal_has_only_erp_read_scopes():
    principal = get_erp_diagnosis_mcp_principal()

    assert principal.scopes == (
        "mcp:tools:list",
        "mcp:resources:read",
        *ERP_DIAGNOSIS_READ_SCOPES,
    )
    assert principal.allow_external_servers is False
    assert principal.allow_write_tools is False
    assert principal.allow_live_neo4j is False
    assert principal.allow_network is False

    for tool_name in [
        "erp_get_user_access_profile",
        "erp_get_document_context",
        "erp_check_operation_permission",
        "erp_get_approval_context",
        "erp_get_transfer_context",
    ]:
        decision = authorize_mcp_tool(
            principal=principal,
            tool_spec=get_mcp_tool_spec(tool_name),
        )
        assert decision.allowed is True


def test_erp_diagnosis_principal_cannot_call_platform_system_tool():
    principal = get_erp_diagnosis_mcp_principal()
    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=get_mcp_tool_spec("mcp_security_report"),
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_scopes"
    assert decision.denied_scopes == ("mcp:security:read",)


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
