from src.app.business.erp_diagnosis.mcp_tools import (
    run_erp_check_operation_permission_mcp_tool,
    run_erp_get_approval_context_mcp_tool,
    run_erp_get_document_context_mcp_tool,
    run_erp_get_transfer_context_mcp_tool,
    run_erp_get_user_access_profile_mcp_tool,
)
from src.app.mcp_integration.permissions import MCPPrincipal


def test_erp_user_access_tool_returns_structured_read_only_result():
    payload = run_erp_get_user_access_profile_mcp_tool(
        user_id="SYN-U001",
        trace_id="test-erp-user-access",
    )

    assert payload["allowed"] is True
    assert payload["summary"] == {"status": "completed", "found": True}
    assert payload["result"]["user_id"] == "SYN-U001"
    assert payload["result"]["roles"] == ["PURCHASE_OPERATOR"]
    assert payload["authorization"]["principal_id"] == "erp-diagnosis-readonly-principal"
    assert payload["mcp_boundary"]["read_only"] is True
    assert payload["mcp_boundary"]["network_required"] is False
    assert payload["mcp_boundary"]["write_capability_exposed"] is False
    assert payload["business_audit"]["raw_argument_values_recorded"] is False


def test_erp_permission_tool_returns_controlled_root_cause_evidence():
    payload = run_erp_check_operation_permission_mcp_tool(
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        trace_id="test-erp-permission",
    )

    assert payload["allowed"] is True
    assert payload["summary"]["status"] == "completed"
    assert payload["summary"]["operation_allowed"] is False
    assert "ORG_SCOPE_DENIED" in payload["summary"]["reason_codes"]
    assert payload["result"]["role_granted"] is True
    assert payload["result"]["org_scope_granted"] is False
    assert payload["result"]["data_permission_granted"] is True


def test_erp_document_tool_rejects_unknown_operation_as_structured_input_error():
    payload = run_erp_get_document_context_mcp_tool(
        document_id="SYN-PO-001",
        operation="DELETE_EVERYTHING",
        trace_id="test-erp-invalid-operation",
    )

    assert payload["allowed"] is True
    assert payload["summary"]["status"] == "invalid_request"
    assert payload["summary"]["reason"] == "unsupported_operation"
    assert "SUBMIT" in payload["summary"]["supported_operations"]
    assert payload["result"] is None


def test_erp_approval_and_transfer_tools_use_business_contracts():
    approval = run_erp_get_approval_context_mcp_tool(
        document_id="SYN-PO-001",
        trace_id="test-erp-approval",
    )
    transfer = run_erp_get_transfer_context_mcp_tool(
        document_id="SYN-PR-001",
        target_document_type="PurchaseOrder",
        trace_id="test-erp-transfer",
    )

    assert approval["allowed"] is True
    assert approval["result"]["document_id"] == "SYN-PO-001"
    assert "bound" in approval["result"]

    assert transfer["allowed"] is True
    assert transfer["result"]["document_id"] == "SYN-PR-001"
    assert transfer["result"]["target_document_type"] == "PurchaseOrder"
    assert transfer["result"]["rule_found"] is True


def test_erp_tool_denies_principal_without_exact_scope():
    principal = MCPPrincipal(
        principal_id="wrong-scope-principal",
        scopes=("mcp:erp:document:read",),
    )

    payload = run_erp_check_operation_permission_mcp_tool(
        user_id="SYN-U001",
        document_id="SYN-PO-001",
        operation="SUBMIT",
        trace_id="test-erp-scope-denial",
        principal=principal,
    )

    assert payload["allowed"] is False
    assert payload["summary"]["status"] == "denied"
    assert payload["authorization"]["reason"] == "missing_required_scopes"
    assert payload["result"] is None
    assert payload["business_audit"]["raw_argument_values_recorded"] is False


def test_erp_tool_returns_not_found_without_fabricating_business_fact():
    payload = run_erp_get_user_access_profile_mcp_tool(
        user_id="SYN-UNKNOWN",
        trace_id="test-erp-not-found",
    )

    assert payload["allowed"] is True
    assert payload["summary"] == {"status": "not_found", "found": False}
    assert payload["result"] is None
