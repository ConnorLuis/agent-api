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

    invocation_results: list[dict[str, Any]] = []
    for index, expected_call in enumerate(expected_sequence):
        actual_call = actual_sequence[index] if index < len(actual_sequence) else None
        tool_name_hit = (
            actual_call is not None
            and actual_call.get("name") == expected_call.get("name")
        )
        args_hit = (
            tool_name_hit
            and actual_call.get("args", {}) == expected_call.get("args", {})
        )
        invocation_results.append({
            "index": index,
            "expected": expected_call,
            "actual": actual_call,
            "tool_name_hit": tool_name_hit,
            "parameter_hit": bool(args_hit),
        })

    unexpected_extra_calls = actual_sequence[len(expected_sequence):]
    tool_call_successes = sum(
        1 for item in invocation_results if item["tool_name_hit"]
    )
    parameter_successes = sum(
        1 for item in invocation_results if item["parameter_hit"]
    )
    tool_sequence_hit = (
        tool_call_successes == len(expected_sequence)
        and not unexpected_extra_calls
    )
    parameter_sequence_hit = (
        parameter_successes == len(expected_sequence)
        and not unexpected_extra_calls
    )

    answer = str(debug_result.get("final_answer", ""))
    answer_hit = _contains_all(answer, case.get("expected_answer_contains", []))
    passed = tool_sequence_hit and parameter_sequence_hit and answer_hit

    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "tool_sequence_hit": tool_sequence_hit,
        "parameter_sequence_hit": parameter_sequence_hit,
        "answer_hit": answer_hit,
        "expected_tool_sequence": expected_sequence,
        "actual_tool_sequence": actual_sequence,
        "tool_invocation_results": invocation_results,
        "expected_tool_call_count": len(expected_sequence),
        "tool_call_success_count": tool_call_successes,
        "tool_parameter_success_count": parameter_successes,
        "unexpected_extra_tool_calls": unexpected_extra_calls,
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
        "source_hit_count": source_hits,
        "expected_source_count": len(expected_sources),
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
        "task_should_complete": case.get("task_should_complete"),
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
    except Exception as exc:
        detail = {
            "status": "error",
            "passed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    return {**base, **detail}


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _metric_cases(
    results: list[dict[str, Any]],
    metric_name: str,
) -> list[dict[str, Any]]:
    return [
        item
        for item in results
        if item.get("status") != "deferred"
        and metric_name in item.get("metrics", [])
    ]


def _build_router_metric(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_cases = _metric_cases(results, "router_accuracy")
    hits = sum(
        1
        for item in metric_cases
        if item.get("actual_route") == item.get("expected_route")
    )

    dedicated = [
        item
        for item in metric_cases
        if item.get("category") == "router"
    ]
    dedicated_hits = sum(
        1
        for item in dedicated
        if item.get("actual_route") == item.get("expected_route")
    )

    return {
        "name": "router_accuracy",
        "value": _ratio(hits, len(metric_cases)),
        "numerator": hits,
        "denominator": len(metric_cases),
        "dedicated_router_value": _ratio(dedicated_hits, len(dedicated)),
        "dedicated_router_numerator": dedicated_hits,
        "dedicated_router_denominator": len(dedicated),
    }


def _build_tool_call_metric(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_cases = _metric_cases(results, "tool_call_success_rate")
    denominator = sum(
        int(item.get("expected_tool_call_count", 0))
        for item in metric_cases
    )
    numerator = sum(
        int(item.get("tool_call_success_count", 0))
        for item in metric_cases
    )
    extra_calls = sum(
        len(item.get("unexpected_extra_tool_calls", []))
        for item in metric_cases
    )
    return {
        "name": "tool_call_success_rate",
        "value": _ratio(numerator, denominator),
        "numerator": numerator,
        "denominator": denominator,
        "unexpected_extra_call_count": extra_calls,
    }


def _build_tool_parameter_metric(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_cases = _metric_cases(results, "tool_parameter_accuracy")
    denominator = sum(
        int(item.get("expected_tool_call_count", 0))
        for item in metric_cases
    )
    numerator = sum(
        int(item.get("tool_parameter_success_count", 0))
        for item in metric_cases
    )
    return {
        "name": "tool_parameter_accuracy",
        "value": _ratio(numerator, denominator),
        "numerator": numerator,
        "denominator": denominator,
        "matching_rule": "ordered tool-name match plus exact args equality",
    }


def _build_rag_metric(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_cases = _metric_cases(results, "rag_recall_at_k")
    ks = sorted({
        int(item["k"])
        for item in metric_cases
        if item.get("k") is not None
    })
    numerator = sum(
        int(item.get("source_hit_count", 0))
        for item in metric_cases
    )
    denominator = sum(
        int(item.get("expected_source_count", 0))
        for item in metric_cases
    )
    macro = (
        round(
            sum(float(item.get("recall_at_k", 0.0)) for item in metric_cases)
            / len(metric_cases),
            6,
        )
        if metric_cases
        else None
    )
    return {
        "name": "rag_recall_at_k",
        "value": _ratio(numerator, denominator),
        "numerator": numerator,
        "denominator": denominator,
        "k_values": ks,
        "macro_mean_source_recall": macro,
        "scope": "source-level recall over the local golden KB",
        "limitation": (
            "Current closure KB contains one committed knowledge document; "
            "this validates retrieval correctness, not large-corpus retrieval quality."
        ),
    }


def _build_task_completion_metric(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_cases = _metric_cases(results, "task_completion_rate")
    normal_cases = [
        item
        for item in metric_cases
        if item.get("category") != "failure_recovery"
    ]
    numerator = sum(
        1
        for item in normal_cases
        if item.get("task_should_complete") is True
        and item.get("passed") is True
    )
    denominator = sum(
        1
        for item in normal_cases
        if item.get("task_should_complete") is True
    )
    return {
        "name": "task_completion_rate",
        "value": _ratio(numerator, denominator),
        "numerator": numerator,
        "denominator": denominator,
        "scope": "normal executable cases tagged task_completion_rate",
        "failure_recovery_cases_included": False,
    }


def _infer_metric_failures(item: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    if "router_accuracy" in item.get("metrics", []):
        if item.get("actual_route") != item.get("expected_route"):
            failures.append("router_accuracy")

    if "tool_call_success_rate" in item.get("metrics", []):
        expected = int(item.get("expected_tool_call_count", 0))
        actual_success = int(item.get("tool_call_success_count", 0))
        if (
            actual_success != expected
            or item.get("unexpected_extra_tool_calls")
        ):
            failures.append("tool_call_success_rate")

    if "tool_parameter_accuracy" in item.get("metrics", []):
        expected = int(item.get("expected_tool_call_count", 0))
        actual_success = int(item.get("tool_parameter_success_count", 0))
        if (
            actual_success != expected
            or item.get("unexpected_extra_tool_calls")
        ):
            failures.append("tool_parameter_accuracy")

    if "rag_recall_at_k" in item.get("metrics", []):
        if float(item.get("recall_at_k", 0.0)) < 1.0:
            failures.append("rag_recall_at_k")

    if "task_completion_rate" in item.get("metrics", []):
        if item.get("task_should_complete") is True and item.get("passed") is not True:
            failures.append("task_completion_rate")

    return failures


def _compact_expected_actual(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    expected: dict[str, Any] = {}
    actual: dict[str, Any] = {}

    if "expected_route" in item:
        expected["route"] = item.get("expected_route")
        actual["route"] = item.get("actual_route")

    if "expected_tool_sequence" in item:
        expected["tool_sequence"] = item.get("expected_tool_sequence")
        actual["tool_sequence"] = item.get("actual_tool_sequence")

    if "expected_sources" in item:
        expected["sources"] = item.get("expected_sources")
        actual["sources"] = item.get("actual_sources")

    if "error_type" in item:
        actual["error_type"] = item.get("error_type")
        actual["error"] = item.get("error")

    return expected, actual


def build_failure_attribution(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for item in results:
        if item.get("status") not in {"failed", "error"}:
            continue
        expected, actual = _compact_expected_actual(item)
        failures.append({
            "case_id": item.get("case_id"),
            "category": item.get("category"),
            "status": item.get("status"),
            "metric_failures": _infer_metric_failures(item),
            "expected": expected,
            "actual": actual,
            "thread_id": item.get("thread_id"),
        })
    return failures


def build_formal_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "router_accuracy": _build_router_metric(results),
        "tool_call_success_rate": _build_tool_call_metric(results),
        "tool_parameter_accuracy": _build_tool_parameter_metric(results),
        "rag_recall_at_k": _build_rag_metric(results),
        "task_completion_rate": _build_task_completion_metric(results),
    }
    return {
        "phase": "closure_2_formal_metrics",
        "metrics": metrics,
        "failure_attribution": build_failure_attribution(results),
    }


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    executed = [item for item in results if item["status"] != "deferred"]
    formal = build_formal_metrics(results)
    return {
        "phase": "closure_2_formal_metrics",
        "total_cases": len(results),
        "executed_cases": len(executed),
        "deferred_cases": len(results) - len(executed),
        "passed_cases": sum(1 for item in executed if item.get("passed") is True),
        "failed_or_error_cases": sum(1 for item in executed if item.get("passed") is False),
        "router_accuracy": formal["metrics"]["router_accuracy"]["value"],
        "tool_call_success_rate": formal["metrics"]["tool_call_success_rate"]["value"],
        "tool_parameter_accuracy": formal["metrics"]["tool_parameter_accuracy"]["value"],
        "rag_recall_at_k": formal["metrics"]["rag_recall_at_k"]["value"],
        "task_completion_rate": formal["metrics"]["task_completion_rate"]["value"],
        "failure_count": len(formal["failure_attribution"]),
        "failure_trace_coverage": None,
        "note": (
            "Failure/recovery cases remain deferred until Closure-3; "
            "failure trace coverage is intentionally not claimed yet."
        ),
    }


def run_closure_eval(cases: list[dict[str, Any]]) -> dict[str, Any]:
    validation = validate_golden_cases(cases)
    if not validation["valid"]:
        raise ValueError("golden set validation failed: " + "; ".join(validation["errors"]))
    results = [run_case(case) for case in cases]
    formal = build_formal_metrics(results)
    return {
        "validation": validation,
        "summary": build_summary(results),
        "formal_metrics": formal["metrics"],
        "failure_attribution": formal["failure_attribution"],
        "results": results,
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    metrics = report["formal_metrics"]
    failures = report["failure_attribution"]

    def pct(value: float | None) -> str:
        if value is None:
            return "N/A"
        return f"{value * 100:.2f}%"

    lines = [
        "# agent-api Closure Evaluation",
        "",
        "## Summary",
        "",
        f"- Total golden cases: {summary['total_cases']}",
        f"- Executed: {summary['executed_cases']}",
        f"- Deferred: {summary['deferred_cases']}",
        f"- Passed: {summary['passed_cases']}",
        f"- Failed/error: {summary['failed_or_error_cases']}",
        "",
        "## Formal Metrics",
        "",
        (
            "- Router Accuracy: "
            f"{metrics['router_accuracy']['numerator']}/"
            f"{metrics['router_accuracy']['denominator']} "
            f"({pct(metrics['router_accuracy']['value'])})"
        ),
        (
            "  - Dedicated Router suite: "
            f"{metrics['router_accuracy']['dedicated_router_numerator']}/"
            f"{metrics['router_accuracy']['dedicated_router_denominator']} "
            f"({pct(metrics['router_accuracy']['dedicated_router_value'])})"
        ),
        (
            "- Tool Call Success Rate: "
            f"{metrics['tool_call_success_rate']['numerator']}/"
            f"{metrics['tool_call_success_rate']['denominator']} "
            f"({pct(metrics['tool_call_success_rate']['value'])})"
        ),
        (
            "- Tool Parameter Accuracy: "
            f"{metrics['tool_parameter_accuracy']['numerator']}/"
            f"{metrics['tool_parameter_accuracy']['denominator']} "
            f"({pct(metrics['tool_parameter_accuracy']['value'])})"
        ),
        (
            "- RAG source Recall@k: "
            f"{metrics['rag_recall_at_k']['numerator']}/"
            f"{metrics['rag_recall_at_k']['denominator']} "
            f"({pct(metrics['rag_recall_at_k']['value'])}); "
            f"k={metrics['rag_recall_at_k']['k_values']}"
        ),
        (
            "- Task Completion Rate: "
            f"{metrics['task_completion_rate']['numerator']}/"
            f"{metrics['task_completion_rate']['denominator']} "
            f"({pct(metrics['task_completion_rate']['value'])})"
        ),
        "",
        "## RAG Scope",
        "",
        f"- {metrics['rag_recall_at_k']['scope']}",
        f"- Limitation: {metrics['rag_recall_at_k']['limitation']}",
        "",
        "## Failure Attribution",
        "",
    ]

    if not failures:
        lines.append("- None")
    else:
        for failure in failures:
            lines.extend([
                f"### {failure['case_id']}",
                "",
                f"- Category: {failure['category']}",
                f"- Status: {failure['status']}",
                f"- Metric failures: {', '.join(failure['metric_failures']) or 'unclassified'}",
                f"- Expected: `{json.dumps(failure['expected'], ensure_ascii=False, sort_keys=True)}`",
                f"- Actual: `{json.dumps(failure['actual'], ensure_ascii=False, sort_keys=True)}`",
                "",
            ])

    lines.extend([
        "## Closure-3 Boundary",
        "",
        "- tool timeout / exception / duplicate-call / checkpoint-recovery cases are still deferred.",
        "- Failure Trace Coverage is not reported until those four deterministic fault/recovery cases execute.",
        "",
    ])
    return "\n".join(lines)
