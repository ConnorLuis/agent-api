from collections import Counter

from src.app.evaluation.closure_eval import (
    EXPECTED_CATEGORY_COUNTS,
    load_golden_cases,
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


def test_failure_and_recovery_cases_are_explicitly_deferred_in_closure_1():
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
