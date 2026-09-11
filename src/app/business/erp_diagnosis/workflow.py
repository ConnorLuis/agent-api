from __future__ import annotations

import re
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from src.app.business.erp_diagnosis.mcp_tools import (
    run_erp_check_operation_permission_mcp_tool,
    run_erp_get_approval_context_mcp_tool,
    run_erp_get_document_context_mcp_tool,
    run_erp_get_transfer_context_mcp_tool,
    run_erp_get_user_access_profile_mcp_tool,
)
from src.app.business.erp_diagnosis.memory import build_erp_diagnosis_checkpointer
from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.policy import retrieve_erp_policy_evidence
from src.app.business.erp_diagnosis.root_causes import (
    RootCauseCode,
    get_root_cause_definition,
)
from src.app.business.erp_diagnosis.service import ERPReadService
from src.app.observability.trace_store import record_trace_event


class ERPDiagnosisState(TypedDict, total=False):
    query: str
    thread_id: str
    trace_id: str

    request_user_id: str | None
    request_document_id: str | None
    request_operation: str | None
    request_target_document_type: str | None

    user_id: str
    document_id: str
    operation: str
    target_document_type: str | None
    missing_fields: list[str]

    tool_payloads: dict[str, dict[str, Any]]
    root_cause_codes: list[str]
    policy_citations: list[str]
    policy_evidence: list[dict[str, Any]]
    policy_retrieval_runs: list[dict[str, Any]]

    status: str
    root_cause_summary: str
    evidence: list[dict[str, Any]]
    recommendations: list[str]
    requires_human: bool

    verification_pass: bool
    verification_flags: list[str]
    steps: list[str]


_DOCUMENT_ID_PATTERN = re.compile(r"\bSYN-(?:PO|PR|EX|SO|ST|PE)-\d{3}\b", re.IGNORECASE)
_USER_ID_PATTERN = re.compile(r"\bSYN-U\d{3}\b", re.IGNORECASE)

_TARGET_DOCUMENT_TYPES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("传成采购订单", "下推采购订单", "生成采购订单", "to purchaseorder", "to purchase order"), "PurchaseOrder"),
    (("传成销售订单", "下推销售订单", "生成销售订单", "to salesorder", "to sales order"), "SalesOrder"),
    (("传成送货单", "下推送货单", "生成送货单", "to deliveryorder", "to delivery order"), "DeliveryOrder"),
    (("传成入库单", "下推入库单", "生成入库单", "to warehousereceipt", "to warehouse receipt"), "WarehouseReceipt"),
    (("传成付款申请", "下推付款申请", "生成付款申请", "to paymentrequest", "to payment request"), "PaymentRequest"),
)


def _append_step(state: ERPDiagnosisState, step: str) -> list[str]:
    return [*state.get("steps", []), step]


def _record_step(state: ERPDiagnosisState, node: str, **payload: Any) -> None:
    trace_id = state.get("trace_id")
    if not trace_id:
        return
    safe_payload = {
        "node": node,
        "thread_id": state.get("thread_id"),
        **payload,
    }
    record_trace_event(
        trace_id=trace_id,
        event_type="erp_diagnosis_step",
        payload=safe_payload,
    )


def _extract_user_id(query: str) -> str | None:
    match = _USER_ID_PATTERN.search(query)
    return match.group(0).upper() if match else None


def _extract_document_id(query: str) -> str | None:
    match = _DOCUMENT_ID_PATTERN.search(query)
    return match.group(0).upper() if match else None


def _infer_operation(query: str) -> ERPOperation | None:
    normalized = query.strip().lower()
    rules: tuple[tuple[ERPOperation, tuple[str, ...]], ...] = (
        (ERPOperation.TRANSFER, ("传单", "下推", "生成下游", "transfer")),
        (ERPOperation.SUBMIT, ("提交", "送审", "submit")),
        (ERPOperation.APPROVE, ("审批", "审核", "approve")),
        (ERPOperation.CREATE, ("创建", "新建", "create")),
        (ERPOperation.VIEW, ("查看", "看不到", "查询", "view")),
    )
    for operation, keywords in rules:
        if any(keyword in normalized for keyword in keywords):
            return operation
    return None


def _infer_target_document_type(query: str) -> str | None:
    normalized = query.strip().lower()
    for aliases, target_type in _TARGET_DOCUMENT_TYPES:
        if any(alias in normalized for alias in aliases):
            return target_type
    return None


def _normalize_operation(value: str | ERPOperation | None) -> ERPOperation | None:
    if value is None:
        return None
    if isinstance(value, ERPOperation):
        return value
    try:
        return ERPOperation(str(value).strip().upper())
    except ValueError:
        return None


def analyze_request_node(state: ERPDiagnosisState) -> dict[str, Any]:
    query = state.get("query", "")
    operation_from_request = _normalize_operation(state.get("request_operation"))
    operation_from_query = _infer_operation(query)
    operation_from_context = _normalize_operation(state.get("operation"))
    operation = operation_from_request or operation_from_query or operation_from_context

    user_id = (
        state.get("request_user_id")
        or _extract_user_id(query)
        or state.get("user_id")
    )
    document_id = (
        state.get("request_document_id")
        or _extract_document_id(query)
        or state.get("document_id")
    )
    target_document_type = (
        state.get("request_target_document_type")
        or _infer_target_document_type(query)
        or state.get("target_document_type")
    )

    missing_fields: list[str] = []
    if not user_id:
        missing_fields.append("user_id")
    if not document_id:
        missing_fields.append("document_id")
    if operation is None:
        missing_fields.append("operation")
    if operation == ERPOperation.TRANSFER and not target_document_type:
        missing_fields.append("target_document_type")

    update: dict[str, Any] = {
        "missing_fields": missing_fields,
        "steps": _append_step(state, "analyze_request"),
    }
    if user_id:
        update["user_id"] = user_id
    if document_id:
        update["document_id"] = document_id
    if operation is not None:
        update["operation"] = operation.value
    if operation == ERPOperation.TRANSFER:
        update["target_document_type"] = target_document_type
    else:
        # Do not leak a previous transfer target into a non-transfer follow-up.
        update["target_document_type"] = None

    if missing_fields:
        update.update(
            {
                "status": "needs_input",
                "root_cause_codes": [RootCauseCode.INSUFFICIENT_EVIDENCE.value],
            }
        )

    _record_step(
        state,
        "analyze_request",
        missing_fields=missing_fields,
        operation=operation.value if operation else None,
    )
    return update


def route_after_analysis(state: ERPDiagnosisState) -> str:
    return "needs_input" if state.get("missing_fields") else "collect"


def _tool_status(payload: dict[str, Any]) -> str:
    return str((payload.get("summary") or {}).get("status", "unknown"))


def collect_business_evidence_node(
    state: ERPDiagnosisState,
    *,
    service: ERPReadService | None = None,
) -> dict[str, Any]:
    user_id = state["user_id"]
    document_id = state["document_id"]
    operation = state["operation"]
    trace_id = state["trace_id"]

    payloads: dict[str, dict[str, Any]] = {}
    payloads["user_access"] = run_erp_get_user_access_profile_mcp_tool(
        user_id=user_id,
        trace_id=trace_id,
        service=service,
    )
    payloads["document_context"] = run_erp_get_document_context_mcp_tool(
        document_id=document_id,
        operation=operation,
        trace_id=trace_id,
        service=service,
    )
    payloads["permission"] = run_erp_check_operation_permission_mcp_tool(
        user_id=user_id,
        document_id=document_id,
        operation=operation,
        trace_id=trace_id,
        service=service,
    )

    normalized_operation = ERPOperation(operation)
    if normalized_operation in {ERPOperation.SUBMIT, ERPOperation.APPROVE}:
        payloads["approval"] = run_erp_get_approval_context_mcp_tool(
            document_id=document_id,
            trace_id=trace_id,
            service=service,
        )
    elif normalized_operation == ERPOperation.TRANSFER:
        payloads["transfer"] = run_erp_get_transfer_context_mcp_tool(
            document_id=document_id,
            target_document_type=state["target_document_type"],
            trace_id=trace_id,
            service=service,
        )

    statuses = {name: _tool_status(payload) for name, payload in payloads.items()}
    _record_step(
        state,
        "collect_business_evidence",
        tool_names=sorted(payload.get("tool_name", "") for payload in payloads.values()),
        tool_statuses=statuses,
    )
    return {
        "tool_payloads": payloads,
        "steps": _append_step(state, "collect_business_evidence"),
    }


def _dedupe_codes(codes: list[RootCauseCode]) -> list[RootCauseCode]:
    result: list[RootCauseCode] = []
    for code in codes:
        if code not in result:
            result.append(code)
    return result


def diagnose_root_cause_node(state: ERPDiagnosisState) -> dict[str, Any]:
    payloads = state.get("tool_payloads", {})
    statuses = [_tool_status(payload) for payload in payloads.values()]

    if any(status == "dependency_unavailable" for status in statuses):
        codes = [RootCauseCode.DEPENDENCY_UNAVAILABLE]
    elif any(status in {"denied", "invalid_request", "not_found", "unknown"} for status in statuses):
        codes = [RootCauseCode.INSUFFICIENT_EVIDENCE]
    else:
        codes: list[RootCauseCode] = []
        permission_result = (payloads.get("permission") or {}).get("result") or {}
        for value in permission_result.get("reasons", []):
            try:
                codes.append(RootCauseCode(value))
            except ValueError:
                continue

        operation = ERPOperation(state["operation"])
        if operation in {ERPOperation.SUBMIT, ERPOperation.APPROVE}:
            approval_result = (payloads.get("approval") or {}).get("result") or {}
            if approval_result:
                if not approval_result.get("bound", False):
                    codes.append(RootCauseCode.APPROVAL_FLOW_UNBOUND)
                elif not approval_result.get("approver_resolved", False):
                    codes.append(RootCauseCode.APPROVER_UNRESOLVED)

        if operation == ERPOperation.TRANSFER:
            transfer_result = (payloads.get("transfer") or {}).get("result") or {}
            if transfer_result and not transfer_result.get("rule_found", False):
                codes.append(RootCauseCode.TRANSFER_RULE_MISSING)

        codes = _dedupe_codes(codes)
        if not codes:
            codes = [RootCauseCode.NO_ISSUE_DETECTED]

    serialized = [code.value for code in codes]
    _record_step(state, "diagnose_root_cause", root_cause_codes=serialized)
    return {
        "root_cause_codes": serialized,
        "steps": _append_step(state, "diagnose_root_cause"),
    }


def route_after_diagnosis(state: ERPDiagnosisState) -> str:
    codes = set(state.get("root_cause_codes", []))
    if RootCauseCode.DEPENDENCY_UNAVAILABLE.value in codes:
        return "compose"
    if RootCauseCode.INSUFFICIENT_EVIDENCE.value in codes:
        return "compose"
    if codes == {RootCauseCode.NO_ISSUE_DETECTED.value}:
        return "compose"
    return "policy"


def retrieve_policy_node(state: ERPDiagnosisState) -> dict[str, Any]:
    policy = retrieve_erp_policy_evidence(state.get("root_cause_codes", []))
    _record_step(
        state,
        "retrieve_policy",
        citation_count=len(policy["citations"]),
        retrieval_backend=policy["retrieval_backend"],
    )
    return {
        "policy_citations": policy["citations"],
        "policy_evidence": policy["evidence"],
        "policy_retrieval_runs": policy["retrieval_runs"],
        "steps": _append_step(state, "retrieve_policy"),
    }


def _build_tool_evidence(state: ERPDiagnosisState) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    payloads = state.get("tool_payloads", {})

    for name, payload in payloads.items():
        result = payload.get("result") or {}
        tool_name = str(payload.get("tool_name", name))
        status = _tool_status(payload)
        details: dict[str, Any] = {"status": status}
        summary = f"{tool_name} 返回状态 {status}。"

        if name == "permission" and result:
            details.update(
                {
                    "allowed": bool(result.get("allowed")),
                    "role_granted": bool(result.get("role_granted")),
                    "org_scope_granted": bool(result.get("org_scope_granted")),
                    "data_permission_granted": bool(result.get("data_permission_granted")),
                    "state_allowed": bool(result.get("state_allowed")),
                    "reason_codes": list(result.get("reasons", [])),
                }
            )
            summary = "权限检查返回结构化角色、组织范围、数据权限和单据状态判定。"
        elif name == "approval" and result:
            details.update(
                {
                    "bound": bool(result.get("bound")),
                    "approver_resolved": bool(result.get("approver_resolved")),
                    "flow_id": result.get("flow_id"),
                }
            )
            summary = "审批上下文返回流程绑定与有效审批人解析状态。"
        elif name == "transfer" and result:
            details.update(
                {
                    "rule_found": bool(result.get("rule_found")),
                    "rule_id": result.get("rule_id"),
                    "target_document_type": result.get("target_document_type"),
                }
            )
            summary = "传单上下文返回源单到目标单据类型的规则解析状态。"
        elif name == "document_context" and result:
            document = result.get("document") or {}
            details.update(
                {
                    "document_type": document.get("document_type"),
                    "org_id": document.get("org_id"),
                    "state": document.get("state"),
                }
            )
            summary = "单据上下文返回单据类型、组织和生命周期状态。"
        elif name == "user_access" and result:
            details.update(
                {
                    "active": bool(result.get("active")),
                    "role_count": len(result.get("roles", [])),
                    "org_scope_count": len(result.get("org_scope", [])),
                }
            )
            summary = "用户访问上下文返回用户有效状态及授权范围摘要。"

        evidence.append(
            {
                "source_type": "tool",
                "source_id": tool_name,
                "summary": summary,
                "details": details,
            }
        )

    return evidence


def compose_diagnosis_node(state: ERPDiagnosisState) -> dict[str, Any]:
    codes = [RootCauseCode(value) for value in state.get("root_cause_codes", [])]
    if not codes:
        codes = [RootCauseCode.INSUFFICIENT_EVIDENCE]

    if RootCauseCode.DEPENDENCY_UNAVAILABLE in codes:
        status = "dependency_unavailable"
    elif RootCauseCode.INSUFFICIENT_EVIDENCE in codes:
        status = "needs_input"
    elif codes == [RootCauseCode.NO_ISSUE_DETECTED]:
        status = "no_issue"
    else:
        status = "diagnosed"

    definitions = [get_root_cause_definition(code) for code in codes]
    if status == "diagnosed":
        titles = "、".join(item.title for item in definitions)
        summary = f"基于实时业务工具证据，识别到：{titles}。"
    elif status == "no_issue":
        summary = definitions[0].description
    elif status == "dependency_unavailable":
        summary = (
            "实时 ERP 业务事实不可用，系统拒绝使用静态知识库替代实时权限或流程状态，"
            "因此暂不推断业务根因。"
        )
    else:
        missing = state.get("missing_fields", [])
        suffix = f" 缺少字段：{', '.join(missing)}。" if missing else ""
        summary = f"当前证据不足，无法形成可靠业务诊断。{suffix}".strip()

    recommendations = [item.default_recommendation for item in definitions]
    requires_human = any(item.requires_human for item in definitions)
    evidence = _build_tool_evidence(state)

    for item in state.get("policy_evidence", []):
        evidence.append(
            {
                "source_type": "policy",
                "source_id": item["citation"],
                "summary": item["excerpt"],
                "details": {
                    "root_cause_code": item["root_cause_code"],
                    "relevance_score": item["relevance_score"],
                    "source": item["source"],
                },
            }
        )

    if status in {"needs_input", "dependency_unavailable"}:
        evidence.append(
            {
                "source_type": "system",
                "source_id": status,
                "summary": summary,
                "details": {"missing_fields": state.get("missing_fields", [])},
            }
        )

    _record_step(
        state,
        "compose_diagnosis",
        status=status,
        root_cause_codes=[code.value for code in codes],
        policy_citation_count=len(state.get("policy_citations", [])),
    )
    return {
        "status": status,
        "root_cause_summary": summary,
        "evidence": evidence,
        "recommendations": recommendations,
        "requires_human": requires_human,
        "steps": _append_step(state, "compose_diagnosis"),
    }


def verify_diagnosis_node(state: ERPDiagnosisState) -> dict[str, Any]:
    flags: list[str] = []
    status = state.get("status")
    codes = set(state.get("root_cause_codes", []))
    tool_payloads = state.get("tool_payloads", {})

    if not codes:
        flags.append("missing_root_cause_code")

    for payload in tool_payloads.values():
        boundary = payload.get("mcp_boundary") or {}
        if boundary and (not boundary.get("read_only", False) or boundary.get("write_capability_exposed", True)):
            flags.append("unsafe_tool_boundary")
        if not payload.get("allowed", False):
            flags.append("tool_authorization_denied")

    if status == "diagnosed":
        if not any(item.get("source_type") == "tool" for item in state.get("evidence", [])):
            flags.append("missing_tool_evidence")
        if not state.get("policy_citations"):
            flags.append("missing_policy_citation")

    if status == "dependency_unavailable":
        if state.get("policy_citations"):
            flags.append("dependency_path_used_static_policy_fallback")
        if RootCauseCode.DEPENDENCY_UNAVAILABLE.value not in codes:
            flags.append("dependency_status_without_dependency_code")

    if status == "needs_input" and RootCauseCode.INSUFFICIENT_EVIDENCE.value not in codes:
        flags.append("needs_input_without_insufficient_evidence_code")

    if status == "no_issue":
        permission = (tool_payloads.get("permission") or {}).get("result") or {}
        if not permission.get("allowed", False):
            flags.append("no_issue_without_successful_permission_check")

    flags = sorted(set(flags))
    verification_pass = not flags
    _record_step(
        state,
        "verify_diagnosis",
        verification_pass=verification_pass,
        verification_flags=flags,
    )
    return {
        "verification_pass": verification_pass,
        "verification_flags": flags,
        "steps": _append_step(state, "verify_diagnosis"),
    }


def build_erp_diagnosis_graph(
    *,
    service: ERPReadService | None = None,
    with_checkpointer: bool = True,
):
    builder = StateGraph(ERPDiagnosisState)
    builder.add_node("analyze_request", analyze_request_node)
    builder.add_node(
        "collect_business_evidence",
        lambda state: collect_business_evidence_node(state, service=service),
    )
    builder.add_node("diagnose_root_cause", diagnose_root_cause_node)
    builder.add_node("retrieve_policy", retrieve_policy_node)
    builder.add_node("compose_diagnosis", compose_diagnosis_node)
    builder.add_node("verify_diagnosis", verify_diagnosis_node)

    builder.add_edge(START, "analyze_request")
    builder.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "needs_input": "compose_diagnosis",
            "collect": "collect_business_evidence",
        },
    )
    builder.add_edge("collect_business_evidence", "diagnose_root_cause")
    builder.add_conditional_edges(
        "diagnose_root_cause",
        route_after_diagnosis,
        {
            "policy": "retrieve_policy",
            "compose": "compose_diagnosis",
        },
    )
    builder.add_edge("retrieve_policy", "compose_diagnosis")
    builder.add_edge("compose_diagnosis", "verify_diagnosis")
    builder.add_edge("verify_diagnosis", END)

    if with_checkpointer:
        return builder.compile(checkpointer=build_erp_diagnosis_checkpointer())
    return builder.compile()


erp_diagnosis_graph = build_erp_diagnosis_graph()


def _build_config(thread_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": thread_id}}


def _initial_state(
    *,
    query: str,
    thread_id: str,
    trace_id: str,
    user_id: str | None,
    document_id: str | None,
    operation: ERPOperation | str | None,
    target_document_type: str | None,
) -> ERPDiagnosisState:
    operation_value: str | None
    if isinstance(operation, ERPOperation):
        operation_value = operation.value
    elif operation is None:
        operation_value = None
    else:
        operation_value = str(operation)

    return {
        "query": query,
        "thread_id": thread_id,
        "trace_id": trace_id,
        "request_user_id": user_id,
        "request_document_id": document_id,
        "request_operation": operation_value,
        "request_target_document_type": target_document_type,
        # Reset per-run outputs while preserving durable business context fields.
        "missing_fields": [],
        "tool_payloads": {},
        "root_cause_codes": [],
        "policy_citations": [],
        "policy_evidence": [],
        "policy_retrieval_runs": [],
        "evidence": [],
        "recommendations": [],
        "verification_flags": [],
        "steps": [],
    }


def invoke_erp_diagnosis(
    *,
    query: str,
    user_id: str | None = None,
    document_id: str | None = None,
    operation: ERPOperation | str | None = None,
    target_document_type: str | None = None,
    thread_id: str | None = None,
    trace_id: str | None = None,
    graph=None,
) -> dict[str, Any]:
    final_thread_id = thread_id or f"erp-thread-{uuid4().hex[:8]}"
    final_trace_id = trace_id or f"erp-trace-{uuid4().hex[:8]}"
    target_graph = graph or erp_diagnosis_graph

    result = target_graph.invoke(
        _initial_state(
            query=query,
            thread_id=final_thread_id,
            trace_id=final_trace_id,
            user_id=user_id,
            document_id=document_id,
            operation=operation,
            target_document_type=target_document_type,
        ),
        config=_build_config(final_thread_id) if graph is None else _build_config(final_thread_id),
    )

    return {
        "status": result.get("status", "needs_input"),
        "root_cause_codes": result.get("root_cause_codes", []),
        "root_cause_summary": result.get("root_cause_summary", ""),
        "evidence": result.get("evidence", []),
        "policy_citations": result.get("policy_citations", []),
        "recommendations": result.get("recommendations", []),
        "requires_human": bool(result.get("requires_human", False)),
        "trace_id": final_trace_id,
        "thread_id": final_thread_id,
        "user_id": result.get("user_id"),
        "document_id": result.get("document_id"),
        "operation": result.get("operation"),
        "target_document_type": result.get("target_document_type"),
        "steps": result.get("steps", []),
        "verification_pass": bool(result.get("verification_pass", False)),
        "verification_flags": result.get("verification_flags", []),
    }
