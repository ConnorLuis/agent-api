from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel

from src.app.business.erp_diagnosis.audit import record_erp_tool_audit
from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.service import (
    ERPReadService,
    get_default_erp_read_service,
)
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    authorize_mcp_tool,
    get_erp_diagnosis_loopback_http_mcp_principal,
    get_erp_diagnosis_mcp_principal,
    serialize_authorization_decision,
)
from src.app.mcp_integration.registry import get_mcp_tool_spec
from src.app.mcp_integration.security import evaluate_mcp_tool_security


ERP_MCP_SERVER_NAME = "agent-api-mcp"


def _json_ready(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _service_requires_network(service: ERPReadService) -> bool:
    return bool(getattr(service, "network_required", False))


def _default_principal_for_service(service: ERPReadService) -> MCPPrincipal:
    if _service_requires_network(service):
        # Only trusted internal adapters should advertise network_required=True.
        # The committed Synthetic HTTP adapter also enforces a loopback-only URL.
        return get_erp_diagnosis_loopback_http_mcp_principal()
    return get_erp_diagnosis_mcp_principal()


def _business_boundary(
    tool_name: str,
    *,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    network_required = (
        _service_requires_network(service)
        if service is not None
        else False
    )
    return {
        "server": ERP_MCP_SERVER_NAME,
        "tool_name": tool_name,
        "protocol_boundary": "mcp_erp_business_adapter",
        "read_only": True,
        "synthetic_reference_application": True,
        "network_required": network_required,
        "service_adapter_kind": getattr(
            service,
            "adapter_kind",
            "synthetic_in_process",
        ),
        "loopback_only": bool(getattr(service, "loopback_only", True)),
        "write_capability_exposed": False,
    }


def _security_payload(
    *,
    tool_name: str,
    trace_id: str,
    principal: MCPPrincipal,
    requested_network: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    tool_spec = get_mcp_tool_spec(tool_name)
    authorization_decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=tool_spec,
        requested_live_neo4j=False,
        requested_network=requested_network,
        requested_write=False,
    )
    authorization = serialize_authorization_decision(authorization_decision)

    security = evaluate_mcp_tool_security(
        tool_name=tool_name,
        principal=principal,
        requested_write=False,
        requested_network=requested_network,
        requested_live_neo4j=False,
        requested_graph_mutation=False,
        requested_dry_run=True,
        trace_id=trace_id,
    )
    security_audit_trace = security.get("audit_trace", {})
    security_decision = {
        key: value
        for key, value in security.items()
        if key != "audit_trace"
    }
    return authorization, security_decision, security_audit_trace


def _run_read_tool(
    *,
    tool_name: str,
    trace_id: str,
    parameters: dict[str, Any],
    lookup: Callable[[ERPReadService], Any],
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    erp_service = service or get_default_erp_read_service()
    requested_network = _service_requires_network(erp_service)
    principal = principal or _default_principal_for_service(erp_service)

    authorization, security_decision, security_audit_trace = _security_payload(
        tool_name=tool_name,
        trace_id=trace_id,
        principal=principal,
        requested_network=requested_network,
    )

    if not authorization["allowed"] or not security_decision["allowed"]:
        audit_event = record_erp_tool_audit(
            trace_id=trace_id,
            tool_name=tool_name,
            principal_id=principal.principal_id,
            allowed=False,
            authorization_reason=authorization["reason"],
            parameters=parameters,
            outcome="denied",
        )
        return {
            "tool_name": tool_name,
            "trace_id": trace_id,
            "allowed": False,
            "authorization": authorization,
            "security_decision": security_decision,
            "security_audit_trace": security_audit_trace,
            "result": None,
            "summary": {
                "status": "denied",
                "found": False,
                "reason": authorization["reason"],
            },
            "business_audit": {
                "event_id": audit_event["event_id"],
                "event_type": audit_event["event_type"],
                "parameter_fingerprint": audit_event["payload"]["parameter_fingerprint"],
                "raw_argument_values_recorded": False,
            },
            "mcp_boundary": _business_boundary(
                tool_name,
                service=erp_service,
            ),
        }

    try:
        result = lookup(erp_service)
    except Exception as exc:
        audit_event = record_erp_tool_audit(
            trace_id=trace_id,
            tool_name=tool_name,
            principal_id=principal.principal_id,
            allowed=True,
            authorization_reason=authorization["reason"],
            parameters=parameters,
            outcome="dependency_error",
            result_summary={"error_type": type(exc).__name__},
        )
        return {
            "tool_name": tool_name,
            "trace_id": trace_id,
            "allowed": True,
            "authorization": authorization,
            "security_decision": security_decision,
            "security_audit_trace": security_audit_trace,
            "result": None,
            "summary": {
                "status": "dependency_unavailable",
                "found": False,
                "error_type": type(exc).__name__,
            },
            "business_audit": {
                "event_id": audit_event["event_id"],
                "event_type": audit_event["event_type"],
                "parameter_fingerprint": audit_event["payload"]["parameter_fingerprint"],
                "raw_argument_values_recorded": False,
            },
            "mcp_boundary": _business_boundary(
                tool_name,
                service=erp_service,
            ),
        }

    found = result is not None
    result_payload = _json_ready(result) if found else None
    result_summary: dict[str, Any] = {"found": found}

    if tool_name == "erp_check_operation_permission" and found:
        result_summary["allowed"] = bool(result_payload.get("allowed"))
        result_summary["reason_codes"] = list(result_payload.get("reasons", []))

    audit_event = record_erp_tool_audit(
        trace_id=trace_id,
        tool_name=tool_name,
        principal_id=principal.principal_id,
        allowed=True,
        authorization_reason=authorization["reason"],
        parameters=parameters,
        outcome="completed" if found else "not_found",
        result_summary=result_summary,
    )

    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": True,
        "authorization": authorization,
        "security_decision": security_decision,
        "security_audit_trace": security_audit_trace,
        "result": result_payload,
        "summary": {
            "status": "completed" if found else "not_found",
            "found": found,
            **(
                {
                    "operation_allowed": result_summary.get("allowed"),
                    "reason_codes": result_summary.get("reason_codes", []),
                }
                if tool_name == "erp_check_operation_permission" and found
                else {}
            ),
        },
        "business_audit": {
            "event_id": audit_event["event_id"],
            "event_type": audit_event["event_type"],
            "parameter_fingerprint": audit_event["payload"]["parameter_fingerprint"],
            "raw_argument_values_recorded": False,
        },
        "mcp_boundary": _business_boundary(
            tool_name,
            service=erp_service,
        ),
    }


def _normalize_operation(operation: str | ERPOperation) -> ERPOperation:
    if isinstance(operation, ERPOperation):
        return operation
    return ERPOperation(str(operation).strip().upper())


def _invalid_operation_response(
    *,
    tool_name: str,
    trace_id: str,
    parameters: dict[str, Any],
    principal: MCPPrincipal | None,
) -> dict[str, Any]:
    principal = principal or get_erp_diagnosis_mcp_principal()
    authorization, security_decision, security_audit_trace = _security_payload(
        tool_name=tool_name,
        trace_id=trace_id,
        principal=principal,
        requested_network=False,
    )
    audit_event = record_erp_tool_audit(
        trace_id=trace_id,
        tool_name=tool_name,
        principal_id=principal.principal_id,
        allowed=bool(authorization["allowed"] and security_decision["allowed"]),
        authorization_reason=authorization["reason"],
        parameters=parameters,
        outcome="invalid_request",
        result_summary={"validation_error": "unsupported_operation"},
    )
    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": bool(authorization["allowed"] and security_decision["allowed"]),
        "authorization": authorization,
        "security_decision": security_decision,
        "security_audit_trace": security_audit_trace,
        "result": None,
        "summary": {
            "status": "invalid_request",
            "found": False,
            "reason": "unsupported_operation",
            "supported_operations": [item.value for item in ERPOperation],
        },
        "business_audit": {
            "event_id": audit_event["event_id"],
            "event_type": audit_event["event_type"],
            "parameter_fingerprint": audit_event["payload"]["parameter_fingerprint"],
            "raw_argument_values_recorded": False,
        },
        "mcp_boundary": _business_boundary(tool_name),
    }


def run_erp_get_user_access_profile_mcp_tool(
    *,
    user_id: str,
    trace_id: str = "mcp-erp-user-access-trace",
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    return _run_read_tool(
        tool_name="erp_get_user_access_profile",
        trace_id=trace_id,
        parameters={"user_id": user_id},
        lookup=lambda erp_service: erp_service.get_user_access_profile(user_id),
        principal=principal,
        service=service,
    )


def run_erp_get_document_context_mcp_tool(
    *,
    document_id: str,
    operation: str | ERPOperation,
    trace_id: str = "mcp-erp-document-context-trace",
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    try:
        normalized_operation = _normalize_operation(operation)
    except ValueError:
        return _invalid_operation_response(
            tool_name="erp_get_document_context",
            trace_id=trace_id,
            parameters={
                "document_id": document_id,
                "operation": str(operation),
            },
            principal=principal,
        )

    return _run_read_tool(
        tool_name="erp_get_document_context",
        trace_id=trace_id,
        parameters={
            "document_id": document_id,
            "operation": normalized_operation.value,
        },
        lookup=lambda erp_service: erp_service.get_document_context(
            document_id=document_id,
            operation=normalized_operation,
        ),
        principal=principal,
        service=service,
    )


def run_erp_check_operation_permission_mcp_tool(
    *,
    user_id: str,
    document_id: str,
    operation: str | ERPOperation,
    trace_id: str = "mcp-erp-permission-check-trace",
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    try:
        normalized_operation = _normalize_operation(operation)
    except ValueError:
        return _invalid_operation_response(
            tool_name="erp_check_operation_permission",
            trace_id=trace_id,
            parameters={
                "user_id": user_id,
                "document_id": document_id,
                "operation": str(operation),
            },
            principal=principal,
        )

    return _run_read_tool(
        tool_name="erp_check_operation_permission",
        trace_id=trace_id,
        parameters={
            "user_id": user_id,
            "document_id": document_id,
            "operation": normalized_operation.value,
        },
        lookup=lambda erp_service: erp_service.check_operation_permission(
            user_id=user_id,
            document_id=document_id,
            operation=normalized_operation,
        ),
        principal=principal,
        service=service,
    )


def run_erp_get_approval_context_mcp_tool(
    *,
    document_id: str,
    trace_id: str = "mcp-erp-approval-context-trace",
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    return _run_read_tool(
        tool_name="erp_get_approval_context",
        trace_id=trace_id,
        parameters={"document_id": document_id},
        lookup=lambda erp_service: erp_service.resolve_approval_context(document_id),
        principal=principal,
        service=service,
    )


def run_erp_get_transfer_context_mcp_tool(
    *,
    document_id: str,
    target_document_type: str,
    trace_id: str = "mcp-erp-transfer-context-trace",
    principal: MCPPrincipal | None = None,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    return _run_read_tool(
        tool_name="erp_get_transfer_context",
        trace_id=trace_id,
        parameters={
            "document_id": document_id,
            "target_document_type": target_document_type,
        },
        lookup=lambda erp_service: erp_service.resolve_transfer_context(
            document_id=document_id,
            target_document_type=target_document_type,
        ),
        principal=principal,
        service=service,
    )
