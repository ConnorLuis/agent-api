from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from src.app.agent.graph import debug_agent
from src.app.agent.router_graph import _classify_route
from src.app.agent.smart_router import invoke_smart_agent
from src.app.rag.retriever import search_knowledge

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GOLDEN_PATH = PROJECT_ROOT / "eval_cases" / "agent_closure_golden.jsonl"
EXPECTED_CATEGORY_COUNTS = {
    "router": 12,
    "tool": 10,
    "rag": 10,
    "end_to_end": 4,
    "failure_recovery": 4,
}
SUPPORTED_CATEGORIES = set(EXPECTED_CATEGORY_COUNTS)


def load_golden_cases(path: Path | str = DEFAULT_GOLDEN_PATH) -> list[dict[str, Any]]:
    path = Path(path)
    cases: list[dict[str, Any]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_no}: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"line {line_no} must be a JSON object")
        cases.append(item)
    return cases


def validate_golden_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    ids: list[str] = []
    categories: list[str] = []

    for index, case in enumerate(cases, start=1):
        case_id = case.get("case_id")
        category = case.get("category")
        query = case.get("query")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"case #{index}: missing case_id")
        else:
            ids.append(case_id)
        if category not in SUPPORTED_CATEGORIES:
            errors.append(f"{case_id or index}: unsupported category={category!r}")
        else:
            categories.append(category)
        if not isinstance(query, str) or not query.strip():
            errors.append(f"{case_id or index}: missing query")
        metrics = case.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            errors.append(f"{case_id or index}: metrics must be a non-empty list")

        if category in {"router", "end_to_end"} and not case.get("expected_route"):
            errors.append(f"{case_id or index}: expected_route is required")
        if category == "tool" and not case.get("expected_tool_sequence"):
            errors.append(f"{case_id or index}: expected_tool_sequence is required")
        if category == "rag":
            if not case.get("expected_sources"):
                errors.append(f"{case_id or index}: expected_sources is required")
            recall_k = case.get("recall_k")
            if not isinstance(recall_k, int) or recall_k < 1:
                errors.append(f"{case_id or index}: recall_k must be a positive integer")
        if category == "failure_recovery" and case.get("execution_mode") not in {
            "fault_injection",
            "checkpoint_recovery",
        }:
            errors.append(f"{case_id or index}: invalid failure/recovery execution_mode")

    duplicates = sorted(case_id for case_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate case_id values: {duplicates}")

    counts = dict(Counter(categories))
    if len(cases) != 40:
        errors.append(f"expected exactly 40 cases, got {len(cases)}")
    if counts != EXPECTED_CATEGORY_COUNTS:
        errors.append(f"category counts mismatch: expected={EXPECTED_CATEGORY_COUNTS}, actual={counts}")

    return {
        "valid": not errors,
        "case_count": len(cases),
        "category_counts": counts,
        "errors": errors,
    }


def _contains_all(text: str, expected: Iterable[str]) -> bool:
    lowered = text.lower()
    return all(str(term).lower() in lowered for term in expected)


def _run_router_case(case: dict[str, Any]) -> dict[str, Any]:
    actual_route = _classify_route(case["query"])
    expected_route = case["expected_route"]
    passed = actual_route == expected_route
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "actual_route": actual_route,
        "expected_route": expected_route,
    }


def _extract_tool_calls(debug_result: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for step in debug_result.get("steps", []):
        for message in step.get("messages", []):
            for tool_call in message.get("tool_calls") or []:
                calls.append({
                    "name": tool_call.get("name"),
                    "args": tool_call.get("args") or {},
                })
    return calls


def _run_tool_case(case: dict[str, Any]) -> dict[str, Any]:
    debug_result = debug_agent(
        message=case["query"],
        thread_id=f"closure-{case['case_id']}-{uuid4().hex[:8]}",
    )
    actual_sequence = _extract_tool_calls(debug_result)
    expected_sequence = case["expected_tool_sequence"]
    tool_sequence_hit = actual_sequence == expected_sequence
    answer = str(debug_result.get("final_answer", ""))
    answer_hit = _contains_all(answer, case.get("expected_answer_contains", []))
    passed = tool_sequence_hit and answer_hit
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "tool_sequence_hit": tool_sequence_hit,
        "answer_hit": answer_hit,
        "expected_tool_sequence": expected_sequence,
        "actual_tool_sequence": actual_sequence,
        "final_answer": answer,
        "thread_id": debug_result.get("thread_id"),
    }


def _run_rag_case(case: dict[str, Any]) -> dict[str, Any]:
    k = int(case["recall_k"])
    results = search_knowledge(case["query"], k=k)
    actual_sources = [item.source for item in results]
    expected_sources = list(case["expected_sources"])
    returned_source_set = set(actual_sources)
    source_hits = sum(1 for source in expected_sources if source in returned_source_set)
    recall_at_k = source_hits / len(expected_sources) if expected_sources else 1.0
    retrieved_text = "\n".join(item.content for item in results)
    terms_hit = _contains_all(retrieved_text, case.get("expected_retrieved_terms", []))
    passed = recall_at_k >= 1.0 and terms_hit
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "recall_at_k": round(recall_at_k, 6),
        "k": k,
        "terms_hit": terms_hit,
        "expected_sources": expected_sources,
        "actual_sources": actual_sources,
        "result_count": len(results),
    }


def _run_e2e_case(case: dict[str, Any]) -> dict[str, Any]:
    result = invoke_smart_agent(
        message=case["query"],
        thread_id=f"closure-{case['case_id']}-{uuid4().hex[:8]}",
        router_mode="deterministic",
    )
    actual_route = result.get("route")
    route_hit = actual_route == case["expected_route"]
    answer = str(result.get("answer", ""))
    answer_hit = _contains_all(answer, case.get("expected_answer_contains", []))
    passed = route_hit and answer_hit
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "route_hit": route_hit,
        "answer_hit": answer_hit,
        "expected_route": case["expected_route"],
        "actual_route": actual_route,
        "answer": answer,
        "thread_id": result.get("thread_id"),
    }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    category = case["category"]
    base = {
        "case_id": case["case_id"],
        "category": category,
        "query": case["query"],
        "metrics": case["metrics"],
    }
    try:
        if category == "router":
            detail = _run_router_case(case)
        elif category == "tool":
            detail = _run_tool_case(case)
        elif category == "rag":
            detail = _run_rag_case(case)
        elif category == "end_to_end":
            detail = _run_e2e_case(case)
        elif category == "failure_recovery":
            detail = {
                "status": "deferred",
                "passed": None,
                "execution_mode": case.get("execution_mode"),
                "fault_type": case.get("fault_type"),
                "reason": "reserved_for_closure_3_failure_and_recovery_validation",
            }
        else:
            raise ValueError(f"unsupported category: {category}")
    except Exception as exc:  # evaluator records failures instead of hiding them
        detail = {
            "status": "error",
            "passed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    return {**base, **detail}


def _rate(values: list[bool]) -> float | None:
    if not values:
        return None
    return round(sum(1 for value in values if value) / len(values), 6)


def build_preliminary_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    executed = [item for item in results if item["status"] != "deferred"]
    router = [item for item in results if item["category"] == "router"]
    tools = [item for item in results if item["category"] == "tool"]
    rag = [item for item in results if item["category"] == "rag"]
    e2e = [item for item in results if item["category"] == "end_to_end"]
    return {
        "phase": "closure_1_preliminary",
        "total_cases": len(results),
        "executed_cases": len(executed),
        "deferred_cases": len(results) - len(executed),
        "passed_cases": sum(1 for item in executed if item.get("passed") is True),
        "failed_or_error_cases": sum(1 for item in executed if item.get("passed") is False),
        "router_accuracy_preliminary": _rate([bool(item.get("passed")) for item in router]),
        "tool_case_pass_rate_preliminary": _rate([bool(item.get("passed")) for item in tools]),
        "rag_case_pass_rate_preliminary": _rate([bool(item.get("passed")) for item in rag]),
        "rag_mean_source_recall_at_k_preliminary": (
            round(sum(float(item.get("recall_at_k", 0.0)) for item in rag) / len(rag), 6)
            if rag else None
        ),
        "end_to_end_completion_rate_preliminary": _rate([bool(item.get("passed")) for item in e2e]),
        "note": "Final metric definitions and failure-trace coverage are completed in Closure-2/3.",
    }


def run_closure_eval(cases: list[dict[str, Any]]) -> dict[str, Any]:
    validation = validate_golden_cases(cases)
    if not validation["valid"]:
        raise ValueError("golden set validation failed: " + "; ".join(validation["errors"]))
    results = [run_case(case) for case in cases]
    return {
        "validation": validation,
        "summary": build_preliminary_summary(results),
        "results": results,
    }
