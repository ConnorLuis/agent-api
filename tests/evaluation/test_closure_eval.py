from collections import Counter

from src.app.evaluation.closure_eval import (
    EXPECTED_CATEGORY_COUNTS,
    build_failure_attribution,
    build_formal_metrics,
    load_golden_cases,
    render_markdown_report,
    run_case,
    validate_golden_cases,
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


def test_failure_and_recovery_cases_are_explicitly_deferred_until_closure_3():
    cases = [case for case in load_golden_cases() if case["category"] == "failure_recovery"]
    results = [run_case(case) for case in cases]
    assert len(results) == 4
    assert all(result["status"] == "deferred" for result in results)
    assert all(result["passed"] is None for result in results)


def test_router_cases_execute_without_evaluator_errors():
    cases = [case for case in load_golden_cases() if case["category"] == "router"]
    results = [run_case(case) for case in cases]
    assert len(results) == 12
    assert all(result["status"] in {"passed", "failed"} for result in results)
    assert all("actual_route" in result for result in results)


def test_formal_metrics_use_fixed_denominators_and_call_level_tool_scoring():
    results = [
        {
            "case_id": "router-ok",
            "category": "router",
            "status": "passed",
            "passed": True,
            "metrics": ["router_accuracy"],
            "expected_route": "chat",
            "actual_route": "chat",
        },
        {
            "case_id": "router-bad",
            "category": "end_to_end",
            "status": "failed",
            "passed": False,
            "metrics": ["router_accuracy", "task_completion_rate"],
            "expected_route": "rag",
            "actual_route": "chat",
            "task_should_complete": True,
        },
        {
            "case_id": "tool",
            "category": "tool",
            "status": "failed",
            "passed": False,
            "metrics": [
                "tool_call_success_rate",
                "tool_parameter_accuracy",
                "task_completion_rate",
            ],
            "expected_tool_call_count": 2,
            "tool_call_success_count": 2,
            "tool_parameter_success_count": 1,
            "unexpected_extra_tool_calls": [],
            "task_should_complete": True,
        },
        {
            "case_id": "rag",
            "category": "rag",
            "status": "passed",
            "passed": True,
            "metrics": ["rag_recall_at_k", "task_completion_rate"],
            "k": 3,
            "source_hit_count": 1,
            "expected_source_count": 1,
            "recall_at_k": 1.0,
            "task_should_complete": True,
        },
        {
            "case_id": "deferred",
            "category": "failure_recovery",
            "status": "deferred",
            "passed": None,
            "metrics": ["task_completion_rate"],
            "task_should_complete": False,
        },
    ]

    formal = build_formal_metrics(results)["metrics"]

    assert formal["router_accuracy"]["numerator"] == 1
    assert formal["router_accuracy"]["denominator"] == 2
    assert formal["router_accuracy"]["value"] == 0.5

    assert formal["tool_call_success_rate"]["numerator"] == 2
    assert formal["tool_call_success_rate"]["denominator"] == 2
    assert formal["tool_call_success_rate"]["value"] == 1.0

    assert formal["tool_parameter_accuracy"]["numerator"] == 1
    assert formal["tool_parameter_accuracy"]["denominator"] == 2
    assert formal["tool_parameter_accuracy"]["value"] == 0.5

    assert formal["rag_recall_at_k"]["numerator"] == 1
    assert formal["rag_recall_at_k"]["denominator"] == 1
    assert formal["rag_recall_at_k"]["value"] == 1.0

    assert formal["task_completion_rate"]["numerator"] == 1
    assert formal["task_completion_rate"]["denominator"] == 3
    assert formal["task_completion_rate"]["value"] == 0.333333


def test_failure_attribution_maps_failed_assertions_to_metric_names():
    results = [
        {
            "case_id": "router-failure",
            "category": "router",
            "status": "failed",
            "passed": False,
            "metrics": ["router_accuracy"],
            "expected_route": "calculator",
            "actual_route": "chat",
        },
        {
            "case_id": "tool-failure",
            "category": "tool",
            "status": "failed",
            "passed": False,
            "metrics": ["tool_call_success_rate", "tool_parameter_accuracy"],
            "expected_tool_sequence": [{"name": "add", "args": {"a": 1, "b": 2}}],
            "actual_tool_sequence": [{"name": "multiply", "args": {"a": 1, "b": 2}}],
            "expected_tool_call_count": 1,
            "tool_call_success_count": 0,
            "tool_parameter_success_count": 0,
            "unexpected_extra_tool_calls": [],
        },
    ]

    failures = build_failure_attribution(results)
    assert failures[0]["metric_failures"] == ["router_accuracy"]
    assert failures[0]["expected"]["route"] == "calculator"
    assert failures[0]["actual"]["route"] == "chat"

    assert failures[1]["metric_failures"] == [
        "tool_call_success_rate",
        "tool_parameter_accuracy",
    ]


def test_markdown_report_renders_metric_counts_and_failure_section():
    report = {
        "summary": {
            "total_cases": 40,
            "executed_cases": 36,
            "deferred_cases": 4,
            "passed_cases": 35,
            "failed_or_error_cases": 1,
        },
        "formal_metrics": {
            "router_accuracy": {
                "value": 0.9375,
                "numerator": 15,
                "denominator": 16,
                "dedicated_router_value": 0.916667,
                "dedicated_router_numerator": 11,
                "dedicated_router_denominator": 12,
            },
            "tool_call_success_rate": {
                "value": 1.0,
                "numerator": 12,
                "denominator": 12,
            },
            "tool_parameter_accuracy": {
                "value": 1.0,
                "numerator": 12,
                "denominator": 12,
            },
            "rag_recall_at_k": {
                "value": 1.0,
                "numerator": 10,
                "denominator": 10,
                "k_values": [3],
                "scope": "source-level recall",
                "limitation": "single document",
            },
            "task_completion_rate": {
                "value": 1.0,
                "numerator": 24,
                "denominator": 24,
            },
        },
        "failure_attribution": [
            {
                "case_id": "router_calc_chinese_num_012",
                "category": "router",
                "status": "failed",
                "metric_failures": ["router_accuracy"],
                "expected": {"route": "calculator"},
                "actual": {"route": "chat"},
            }
        ],
    }

    markdown = render_markdown_report(report)
    assert "15/16" in markdown
    assert "12/12" in markdown
    assert "10/10" in markdown
    assert "24/24" in markdown
    assert "router_calc_chinese_num_012" in markdown
