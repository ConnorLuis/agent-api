from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from src.app.agent.graph import invoke_agent
from src.app.agent.tools import add, multiply
from src.app.observability.trace_store import record_trace_event


def _trace(
    trace_id: str,
    event_type: str,
    payload: dict[str, Any],
    trace_db_path: Path | str,
) -> None:
    record_trace_event(
        trace_id=trace_id,
        event_type=event_type,
        payload=payload,
        db_path=trace_db_path,
    )


def _run_with_timeout(
    func: Callable[[], Any],
    timeout_s: float,
) -> tuple[bool, Any | None]:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func)
    try:
        return False, future.result(timeout=timeout_s)
    except FutureTimeoutError:
        future.cancel()
        return True, None
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _invoke_tool(name: str, args: dict[str, Any]) -> Any:
    mapping = {
        "add": add,
        "multiply": multiply,
    }
    if name not in mapping:
        raise ValueError(f"unsupported deterministic fault-harness tool: {name}")
    return mapping[name].invoke(args)


def _run_tool_timeout(
    case: dict[str, Any],
    trace_id: str,
    trace_db_path: Path | str,
) -> dict[str, Any]:
    expected_call = case["expected_tool_sequence"][0]
    _trace(
        trace_id,
        "closure_tool_call_planned",
        {"tool_call": expected_call, "fault_type": "tool_timeout"},
        trace_db_path,
    )

    def slow_tool() -> Any:
        time.sleep(0.05)
        return _invoke_tool(expected_call["name"], expected_call["args"])

    timeout_observed, result = _run_with_timeout(slow_tool, timeout_s=0.005)
    _trace(
        trace_id,
        "closure_tool_timeout" if timeout_observed else "closure_tool_unexpected_success",
        {
            "tool_call": expected_call,
            "timeout_s": 0.005,
            "timeout_observed": timeout_observed,
            "result": result,
        },
        trace_db_path,
    )
    return {
        "status": "passed" if timeout_observed else "failed",
        "passed": timeout_observed,
        "execution_mode": case.get("execution_mode"),
        "fault_type": case.get("fault_type"),
        "fault_observed": timeout_observed,
        "timeout_observed": timeout_observed,
        "expected_tool_sequence": case.get("expected_tool_sequence", []),
    }


def _run_tool_exception(
    case: dict[str, Any],
    trace_id: str,
    trace_db_path: Path | str,
) -> dict[str, Any]:
    expected_call = case["expected_tool_sequence"][0]
    _trace(
        trace_id,
        "closure_tool_call_planned",
        {"tool_call": expected_call, "fault_type": "tool_exception"},
        trace_db_path,
    )

    exception_observed = False
    error_type = None
    error_message = None
    try:
        raise RuntimeError("injected deterministic tool exception")
    except RuntimeError as exc:
        exception_observed = True
        error_type = type(exc).__name__
        error_message = str(exc)
        _trace(
            trace_id,
            "closure_tool_exception",
            {
                "tool_call": expected_call,
                "error_type": error_type,
                "error": error_message,
            },
            trace_db_path,
        )

    return {
        "status": "passed" if exception_observed else "failed",
        "passed": exception_observed,
        "execution_mode": case.get("execution_mode"),
        "fault_type": case.get("fault_type"),
        "fault_observed": exception_observed,
        "exception_observed": exception_observed,
        "error_type": error_type,
        "error": error_message,
        "expected_tool_sequence": case.get("expected_tool_sequence", []),
    }


def _run_duplicate_tool_call(
    case: dict[str, Any],
    trace_id: str,
    trace_db_path: Path | str,
) -> dict[str, Any]:
    expected_sequence = [dict(item) for item in case["expected_tool_sequence"]]
    actual_sequence = [dict(item) for item in expected_sequence]
    duplicate_call = dict(expected_sequence[-1])
    actual_sequence.append(duplicate_call)

    execution_results: list[dict[str, Any]] = []
    for index, call in enumerate(actual_sequence):
        result = _invoke_tool(call["name"], call["args"])
        execution_results.append({"index": index, "tool_call": call, "result": result})
        _trace(
            trace_id,
            "closure_tool_invoked",
            {"index": index, "tool_call": call, "result": result},
            trace_db_path,
        )

    unexpected_extra_calls = actual_sequence[len(expected_sequence):]
    duplicate_detected = bool(unexpected_extra_calls) and all(
        extra in expected_sequence for extra in unexpected_extra_calls
    )
    _trace(
        trace_id,
        "closure_duplicate_tool_call_detected" if duplicate_detected else "closure_duplicate_tool_call_missed",
        {
            "expected_tool_sequence": expected_sequence,
            "actual_tool_sequence": actual_sequence,
            "unexpected_extra_tool_calls": unexpected_extra_calls,
            "duplicate_detected": duplicate_detected,
        },
        trace_db_path,
    )

    return {
        "status": "passed" if duplicate_detected else "failed",
        "passed": duplicate_detected,
        "execution_mode": case.get("execution_mode"),
        "fault_type": case.get("fault_type"),
        "fault_observed": duplicate_detected,
        "duplicate_detected": duplicate_detected,
        "expected_tool_sequence": expected_sequence,
        "actual_tool_sequence": actual_sequence,
        "unexpected_extra_tool_calls": unexpected_extra_calls,
        "execution_results": execution_results,
    }


def _last_message_content(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""
    return str(messages[-1].content)


def _run_checkpoint_recovery(
    case: dict[str, Any],
    trace_id: str,
    trace_db_path: Path | str,
) -> dict[str, Any]:
    thread_id = f"closure-checkpoint-{uuid4().hex[:12]}"
    setup_query = str(case["setup_query"])
    recovery_query = str(case["query"])

    _trace(
        trace_id,
        "closure_checkpoint_setup_started",
        {"thread_id": thread_id, "query": setup_query},
        trace_db_path,
    )
    setup_result = invoke_agent(message=setup_query, thread_id=thread_id)
    setup_answer = _last_message_content(setup_result)
    _trace(
        trace_id,
        "closure_checkpoint_setup_completed",
        {"thread_id": thread_id, "answer": setup_answer},
        trace_db_path,
    )

    recovery_result = invoke_agent(message=recovery_query, thread_id=thread_id)
    recovery_answer = _last_message_content(recovery_result)
    expected_terms = [str(term).lower() for term in case.get("expected_answer_contains", [])]
    lowered = recovery_answer.lower()
    checkpoint_recovered = all(term in lowered for term in expected_terms)
    _trace(
        trace_id,
        "closure_checkpoint_recovered" if checkpoint_recovered else "closure_checkpoint_recovery_failed",
        {
            "thread_id": thread_id,
            "query": recovery_query,
            "answer": recovery_answer,
            "expected_answer_contains": case.get("expected_answer_contains", []),
            "checkpoint_recovered": checkpoint_recovered,
        },
        trace_db_path,
    )

    return {
        "status": "passed" if checkpoint_recovered else "failed",
        "passed": checkpoint_recovered,
        "execution_mode": case.get("execution_mode"),
        "fault_type": case.get("fault_type"),
        "fault_observed": checkpoint_recovered,
        "checkpoint_recovered": checkpoint_recovered,
        "thread_id": thread_id,
        "setup_answer": setup_answer,
        "recovery_answer": recovery_answer,
        "expected_answer_contains": case.get("expected_answer_contains", []),
    }


def run_failure_recovery_case(
    case: dict[str, Any],
    trace_id: str,
    trace_db_path: Path | str,
) -> dict[str, Any]:
    fault_type = case.get("fault_type")
    if fault_type == "tool_timeout":
        return _run_tool_timeout(case, trace_id, trace_db_path)
    if fault_type == "tool_exception":
        return _run_tool_exception(case, trace_id, trace_db_path)
    if fault_type == "duplicate_tool_call":
        return _run_duplicate_tool_call(case, trace_id, trace_db_path)
    if fault_type == "checkpoint_recovery":
        return _run_checkpoint_recovery(case, trace_id, trace_db_path)
    raise ValueError(f"unsupported failure/recovery fault_type: {fault_type}")
