from collections import Counter

from src.app.agent.router_graph import _classify_route
from src.app.evaluation.closure_eval import (
    EXPECTED_CATEGORY_COUNTS,
    build_failure_attribution,
    build_formal_metrics,
    load_golden_cases,
    render_markdown_report,
    run_case,
    run_closure_eval,
    validate_golden_cases,
)
from src.app.observability.trace_store import get_trace_events


def _case(case_id: str):
    return next(case for case in load_golden_cases() if case["case_id"] == case_id)



def test_router_classifies_chinese_number_calculation():
    assert (
        _classify_route("二十三加十九等于多少？")
        == "calculator"
    )

def test_agent_closure_golden_set_has_fixed_40_case_inventory():
    cases = load_golden_cases()
    assert len(cases) == 40
    assert Counter(case["category"] for case in cases) == Counter(EXPECTED_CATEGORY_COUNTS)
    assert len({case["case_id"] for case in cases}) == 40


def test_agent_closure_golden_schema_is_valid():
    validation = validate_golden_cases(load_golden_cases())
    assert validation == {
        "valid": True,
        "case_count": 40,
        "category_counts": EXPECTED_CATEGORY_COUNTS,
        "errors": [],
    }


def test_router_cases_execute_without_evaluator_errors(tmp_path):
    cases = [case for case in load_golden_cases() if case["category"] == "router"]
    db = tmp_path / "traces.sqlite"
    results = [run_case(case, trace_db_path=db) for case in cases]
    assert len(results) == 12
    assert all(result["status"] in {"passed", "failed"} for result in results)
    assert all("actual_route" in result for result in results)
    assert all(result["trace_replay_available"] is True for result in results)


def test_formal_metrics_exclude_failure_recovery_from_five_normal_metrics():
    results = [
        {
            "case_id": "router-ok",
            "category": "router",
            "status": "passed",
            "passed": True,
            "metrics": ["router_accuracy"],
            "expected_route": "chat",
            "actual_route": "chat",
            "expected_trace_required": False,
            "trace_replay_available": True,
            "trace_event_count": 2,
            "trace_id": "trace-router-ok",
        },
        {
            "case_id": "tool",
            "category": "tool",
            "status": "passed",
            "passed": True,
            "metrics": ["tool_call_success_rate", "tool_parameter_accuracy", "task_completion_rate"],
            "expected_tool_call_count": 2,
            "tool_call_success_count": 2,
            "tool_parameter_success_count": 2,
            "unexpected_extra_tool_calls": [],
            "task_should_complete": True,
            "expected_trace_required": False,
            "trace_replay_available": True,
            "trace_event_count": 2,
            "trace_id": "trace-tool",
        },
        {
            "case_id": "fault",
            "category": "failure_recovery",
            "status": "passed",
            "passed": True,
            "metrics": ["tool_call_success_rate", "failure_trace_coverage"],
            "expected_tool_call_count": 99,
            "tool_call_success_count": 0,
            "tool_parameter_success_count": 0,
            "unexpected_extra_tool_calls": [{"name": "add"}],
            "task_should_complete": False,
            "fault_type": "duplicate_tool_call",
            "expected_trace_required": True,
            "trace_replay_available": True,
            "trace_event_count": 3,
            "trace_id": "trace-fault",
        },
    ]
    formal = build_formal_metrics(results)["metrics"]
    assert formal["router_accuracy"]["value"] == 1.0
    assert formal["tool_call_success_rate"]["numerator"] == 2
    assert formal["tool_call_success_rate"]["denominator"] == 2
    assert formal["tool_parameter_accuracy"]["value"] == 1.0
    assert formal["task_completion_rate"]["value"] == 1.0
    assert formal["failure_recovery_validation_rate"]["value"] == 1.0
    assert formal["failure_trace_coverage"]["value"] == 1.0


def test_failure_attribution_contains_trace_replay_metadata():
    results = [{
        "case_id": "router-failure",
        "category": "router",
        "status": "failed",
        "passed": False,
        "metrics": ["router_accuracy"],
        "expected_route": "calculator",
        "actual_route": "chat",
        "trace_id": "closure-router-failure-1",
        "trace_replay_path": "/observability/traces/closure-router-failure-1",
        "trace_event_count": 2,
        "trace_replay_available": True,
        "expected_trace_required": False,
    }]
    failures = build_failure_attribution(results)
    assert failures[0]["metric_failures"] == ["router_accuracy"]
    assert failures[0]["trace_id"] == "closure-router-failure-1"
    assert failures[0]["trace_replay_path"].endswith("closure-router-failure-1")
    assert failures[0]["trace_event_count"] == 2


def test_tool_timeout_probe_is_detected_and_replayable(tmp_path):
    db = tmp_path / "timeout.sqlite"
    result = run_case(_case("failure_tool_timeout_001"), trace_db_path=db)
    assert result["status"] == "passed"
    assert result["timeout_observed"] is True
    assert result["trace_replay_available"] is True
    events = get_trace_events(result["trace_id"], db_path=db)
    assert "closure_tool_timeout" in [event["event_type"] for event in events]


def test_tool_exception_probe_is_detected_and_replayable(tmp_path):
    db = tmp_path / "exception.sqlite"
    result = run_case(_case("failure_tool_exception_002"), trace_db_path=db)
    assert result["status"] == "passed"
    assert result["exception_observed"] is True
    assert result["error_type"] == "RuntimeError"
    events = get_trace_events(result["trace_id"], db_path=db)
    assert "closure_tool_exception" in [event["event_type"] for event in events]


def test_duplicate_tool_call_probe_detects_extra_execution_and_is_replayable(tmp_path):
    db = tmp_path / "duplicate.sqlite"
    result = run_case(_case("failure_duplicate_call_003"), trace_db_path=db)
    assert result["status"] == "passed"
    assert result["duplicate_detected"] is True
    assert len(result["unexpected_extra_tool_calls"]) == 1
    assert len(result["actual_tool_sequence"]) == 3
    events = get_trace_events(result["trace_id"], db_path=db)
    assert "closure_duplicate_tool_call_detected" in [event["event_type"] for event in events]


def test_checkpoint_recovery_uses_same_thread_and_recovers_tool_result(tmp_path):
    db = tmp_path / "checkpoint.sqlite"
    result = run_case(_case("recovery_checkpoint_004"), trace_db_path=db)
    assert result["status"] == "passed"
    assert result["checkpoint_recovered"] is True
    assert "13" in result["recovery_answer"]
    events = get_trace_events(result["trace_id"], db_path=db)
    assert "closure_checkpoint_setup_completed" in [event["event_type"] for event in events]
    assert "closure_checkpoint_recovered" in [event["event_type"] for event in events]


def test_full_closure_3_run_has_fixed_metrics_and_100_percent_trace_coverage(tmp_path):
    report = run_closure_eval(load_golden_cases(), trace_db_path=tmp_path / "full.sqlite")
    summary = report["summary"]
    metrics = report["formal_metrics"]

    assert summary["phase"] == "closure_3_robustness_and_trace_replay"
    assert summary["total_cases"] == 40
    assert summary["executed_cases"] == 40
    assert summary["deferred_cases"] == 0
    assert summary["passed_cases"] == 40
    assert summary["failed_or_error_cases"] == 0

    assert metrics["router_accuracy"]["numerator"] == 16
    assert metrics["router_accuracy"]["denominator"] == 16
    assert metrics["router_accuracy"]["value"] == 1.0
    assert metrics["tool_call_success_rate"]["numerator"] == 12
    assert metrics["tool_call_success_rate"]["denominator"] == 12
    assert metrics["tool_parameter_accuracy"]["value"] == 1.0
    assert metrics["rag_recall_at_k"]["numerator"] == 10
    assert metrics["rag_recall_at_k"]["denominator"] == 10
    assert metrics["task_completion_rate"]["numerator"] == 24
    assert metrics["task_completion_rate"]["denominator"] == 24
    assert metrics["failure_recovery_validation_rate"]["numerator"] == 4
    assert metrics["failure_recovery_validation_rate"]["denominator"] == 4
    assert metrics["failure_recovery_validation_rate"]["value"] == 1.0
    assert metrics["failure_trace_coverage"]["numerator"] == 4
    assert metrics["failure_trace_coverage"]["denominator"] == 4
    assert metrics["failure_trace_coverage"]["value"] == 1.0
    assert metrics["failure_trace_coverage"]["uncovered_case_ids"] == []

    assert report["failure_attribution"] == []


def test_markdown_report_renders_robustness_and_trace_replay(tmp_path):
    report = run_closure_eval(load_golden_cases(), trace_db_path=tmp_path / "markdown.sqlite")
    markdown = render_markdown_report(report)
    assert "Router Accuracy: 16/16" in markdown
    assert "Tool Call Success Rate: 12/12" in markdown
    assert "Failure/Recovery Validation Rate: 4/4" in markdown
    assert "Failure Trace Coverage: 4/4" in markdown
    assert "- None" in markdown
    assert "GET /observability/traces/{trace_id}" in markdown
