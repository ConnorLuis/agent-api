from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.app.business.erp_diagnosis.failure_injection import (
    FaultInjectingERPReadService,
)
from src.app.business.erp_diagnosis.service import SyntheticERPReadService
from src.app.business.erp_diagnosis.workflow import (
    build_erp_diagnosis_graph,
    invoke_erp_diagnosis,
)
from src.app.observability.trace_store import get_trace_events


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ERP_GOLDEN_FILE = PROJECT_ROOT / "eval_cases" / "erp_diagnosis_golden.jsonl"

ERP_ALLOWED_READ_TOOL_NAMES = {
    "erp_get_user_access_profile",
    "erp_get_document_context",
    "erp_check_operation_permission",
    "erp_get_approval_context",
    "erp_get_transfer_context",
}


class ERPGoldenCaseError(ValueError):
    pass


def load_erp_golden_cases(
    eval_file: Path | str = DEFAULT_ERP_GOLDEN_FILE,
) -> list[dict[str, Any]]:
    path = Path(eval_file)
    cases: list[dict[str, Any]] = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ERPGoldenCaseError(
                f"Invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc

        for required in (
            "case_id",
            "category",
            "query",
            "expected_status",
            "expected_root_cause_codes",
            "expected_tools",
            "expected_trace_nodes",
        ):
            if required not in case:
                raise ERPGoldenCaseError(
                    f"Missing {required!r} at {path}:{line_number}"
                )
        cases.append(case)

    case_ids = [str(case["case_id"]) for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ERPGoldenCaseError("Duplicate ERP Golden Case case_id detected")
    return cases


def _build_case_graph(case: dict[str, Any]):
    execution_mode = str(case.get("execution_mode", "normal"))
    if execution_mode == "normal":
        service = SyntheticERPReadService()
    elif execution_mode == "fault_injection":
        fault_point = case.get("fault_point")
        if not fault_point:
            raise ERPGoldenCaseError(
                f"fault_injection case {case['case_id']} requires fault_point"
            )
        service = FaultInjectingERPReadService(fault_point=fault_point)
    else:
        raise ERPGoldenCaseError(
            f"Unsupported execution_mode={execution_mode!r} for {case['case_id']}"
        )

    return build_erp_diagnosis_graph(
        service=service,
        with_checkpointer=False,
    )


def _called_tool_names(result: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(item.get("source_id"))
            for item in result.get("evidence", [])
            if item.get("source_type") == "tool" and item.get("source_id")
        }
    )


def _trace_nodes(trace_id: str) -> list[str]:
    nodes: list[str] = []
    for event in get_trace_events(trace_id):
        if event.get("event_type") != "erp_diagnosis_step":
            continue
        node = (event.get("payload") or {}).get("node")
        if node and node not in nodes:
            nodes.append(str(node))
    return nodes


def _business_audit_events(trace_id: str) -> list[dict[str, Any]]:
    return [
        event
        for event in get_trace_events(trace_id)
        if event.get("event_type") == "erp_mcp_tool_audit"
    ]


def _root_cause_exact_match(actual: list[str], expected: list[str]) -> bool:
    return len(actual) == len(expected) and set(actual) == set(expected)


def _policy_source_hit(citations: list[str], expected_sources: list[str]) -> bool:
    return all(
        any(expected_source in citation for citation in citations)
        for expected_source in expected_sources
    )


def evaluate_erp_golden_case(case: dict[str, Any]) -> dict[str, Any]:
    trace_id = f"erp-golden-{case['case_id']}-{uuid4().hex[:8]}"
    thread_id = f"erp-golden-thread-{case['case_id']}-{uuid4().hex[:8]}"
    graph = _build_case_graph(case)

    result = invoke_erp_diagnosis(
        query=str(case["query"]),
        user_id=case.get("user_id"),
        document_id=case.get("document_id"),
        operation=case.get("operation"),
        target_document_type=case.get("target_document_type"),
        thread_id=thread_id,
        trace_id=trace_id,
        graph=graph,
    )

    actual_codes = list(result.get("root_cause_codes", []))
    expected_codes = list(case.get("expected_root_cause_codes", []))
    called_tools = _called_tool_names(result)
    expected_tools = list(case.get("expected_tools", []))
    forbidden_tools = list(case.get("forbidden_tools", []))
    citations = list(result.get("policy_citations", []))
    expected_policy_sources = list(case.get("expected_policy_sources", []))
    trace_nodes = _trace_nodes(trace_id)
    expected_trace_nodes = list(case.get("expected_trace_nodes", []))
    audit_events = _business_audit_events(trace_id)

    expected_abstention = bool(case.get("expected_abstention", False))
    actual_abstention = result.get("status") in {
        "needs_input",
        "dependency_unavailable",
    }

    checks = {
        "status_match": result.get("status") == case.get("expected_status"),
        "root_cause_exact_match": _root_cause_exact_match(
            actual_codes,
            expected_codes,
        ),
        "required_tools_hit": set(expected_tools).issubset(called_tools),
        "forbidden_tools_absent": not set(forbidden_tools).intersection(called_tools),
        "read_only_tool_set_only": set(called_tools).issubset(
            ERP_ALLOWED_READ_TOOL_NAMES
        ),
        "policy_source_hit": _policy_source_hit(
            citations,
            expected_policy_sources,
        ),
        "policy_fallback_boundary": (
            not expected_abstention or len(citations) == 0
        ),
        "abstention_match": actual_abstention == expected_abstention,
        "verification_pass": bool(result.get("verification_pass", False)),
        "trace_coverage": set(expected_trace_nodes).issubset(trace_nodes),
        "audit_event_count_match": len(audit_events) == len(called_tools),
        "audit_raw_arguments_absent": all(
            (event.get("payload") or {}).get("raw_argument_values_recorded") is False
            for event in audit_events
        ),
    }

    case_pass = all(checks.values())
    diagnostic_task_eligible = case.get("expected_status") in {
        "diagnosed",
        "no_issue",
    }
    diagnostic_task_pass = (
        checks["status_match"]
        and checks["root_cause_exact_match"]
        and checks["required_tools_hit"]
        and checks["policy_source_hit"]
        and checks["verification_pass"]
    ) if diagnostic_task_eligible else None

    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "execution_mode": case.get("execution_mode", "normal"),
        "fault_point": case.get("fault_point"),
        "case_pass": case_pass,
        "checks": checks,
        "expected": {
            "status": case.get("expected_status"),
            "root_cause_codes": expected_codes,
            "tools": expected_tools,
            "policy_sources": expected_policy_sources,
            "abstention": expected_abstention,
            "trace_nodes": expected_trace_nodes,
        },
        "actual": {
            "status": result.get("status"),
            "root_cause_codes": actual_codes,
            "tools": called_tools,
            "policy_citations": citations,
            "abstention": actual_abstention,
            "trace_nodes": trace_nodes,
            "audit_event_count": len(audit_events),
            "verification_flags": result.get("verification_flags", []),
        },
        "diagnostic_task_eligible": diagnostic_task_eligible,
        "diagnostic_task_pass": diagnostic_task_pass,
        "trace_id": trace_id,
    }


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return round(numerator / denominator, 6)


def run_erp_diagnosis_golden_eval(
    eval_file: Path | str = DEFAULT_ERP_GOLDEN_FILE,
    *,
    case_ids: set[str] | None = None,
) -> dict[str, Any]:
    cases = load_erp_golden_cases(eval_file)
    if case_ids:
        cases = [case for case in cases if str(case["case_id"]) in case_ids]

    results = [evaluate_erp_golden_case(case) for case in cases]
    case_count = len(results)
    passed_cases = sum(1 for item in results if item["case_pass"])

    diagnostic_items = [
        item for item in results if item["diagnostic_task_eligible"]
    ]
    diagnostic_passed = sum(
        1 for item in diagnostic_items if item["diagnostic_task_pass"]
    )

    abstention_items = [
        item for item in results if item["expected"]["abstention"]
    ]
    abstention_passed = sum(
        1 for item in abstention_items if item["checks"]["abstention_match"]
    )

    fault_items = [
        item for item in results if item["execution_mode"] == "fault_injection"
    ]
    failure_trace_passed = sum(
        1 for item in fault_items if item["checks"]["trace_coverage"]
    )

    metric_keys = [
        "status_match",
        "root_cause_exact_match",
        "required_tools_hit",
        "forbidden_tools_absent",
        "read_only_tool_set_only",
        "policy_source_hit",
        "policy_fallback_boundary",
        "verification_pass",
        "trace_coverage",
        "audit_event_count_match",
        "audit_raw_arguments_absent",
    ]
    metrics = {
        key: _ratio(
            sum(1 for item in results if item["checks"][key]),
            case_count,
        )
        for key in metric_keys
    }
    metrics.update(
        {
            "case_pass_rate": _ratio(passed_cases, case_count),
            "diagnostic_task_completion_rate": _ratio(
                diagnostic_passed,
                len(diagnostic_items),
            ),
            "controlled_abstention_accuracy": _ratio(
                abstention_passed,
                len(abstention_items),
            ),
            "failure_trace_coverage_rate": _ratio(
                failure_trace_passed,
                len(fault_items),
            ),
        }
    )

    return {
        "report_name": "ERP diagnosis business Golden Case evaluation",
        "eval_file": str(Path(eval_file)),
        "summary": {
            "case_count": case_count,
            "passed_case_count": passed_cases,
            "failed_case_count": case_count - passed_cases,
            "diagnostic_case_count": len(diagnostic_items),
            "abstention_case_count": len(abstention_items),
            "fault_injection_case_count": len(fault_items),
            "all_passed": passed_cases == case_count,
        },
        "metrics": metrics,
        "results": results,
        "boundaries": {
            "synthetic_data_only": True,
            "write_tools_exposed": False,
            "llm_required_for_root_cause_classification": False,
            "dependency_failure_never_replaced_by_policy_rag": True,
            "production_scale_claimed": False,
        },
    }
