import subprocess
import sys
from pathlib import Path

from src.app.business.erp_diagnosis.evaluation import (
    DEFAULT_ERP_GOLDEN_FILE,
    load_erp_golden_cases,
    run_erp_diagnosis_golden_eval,
)


def test_erp_business_golden_file_has_20_unique_cases():
    cases = load_erp_golden_cases(DEFAULT_ERP_GOLDEN_FILE)

    assert len(cases) == 20
    assert len({case["case_id"] for case in cases}) == 20
    assert {case.get("execution_mode", "normal") for case in cases} == {
        "normal",
        "fault_injection",
    }
    assert sum(case.get("execution_mode") == "fault_injection" for case in cases) == 4


def test_erp_business_golden_cases_all_pass():
    report = run_erp_diagnosis_golden_eval()

    assert report["summary"] == {
        "case_count": 20,
        "passed_case_count": 20,
        "failed_case_count": 0,
        "diagnostic_case_count": 14,
        "abstention_case_count": 6,
        "fault_injection_case_count": 4,
        "all_passed": True,
    }

    assert report["metrics"]["case_pass_rate"] == 1.0
    assert report["metrics"]["diagnostic_task_completion_rate"] == 1.0
    assert report["metrics"]["controlled_abstention_accuracy"] == 1.0
    assert report["metrics"]["failure_trace_coverage_rate"] == 1.0
    assert report["metrics"]["root_cause_exact_match"] == 1.0
    assert report["metrics"]["required_tools_hit"] == 1.0
    assert report["metrics"]["read_only_tool_set_only"] == 1.0
    assert report["metrics"]["policy_fallback_boundary"] == 1.0
    assert report["metrics"]["audit_raw_arguments_absent"] == 1.0

    failed = [item for item in report["results"] if not item["case_pass"]]
    assert failed == []


def test_fault_cases_abstain_without_policy_fallback():
    report = run_erp_diagnosis_golden_eval(
        case_ids={
            "erp_fault_permission_017",
            "erp_fault_approval_018",
            "erp_fault_transfer_019",
            "erp_fault_user_access_020",
        }
    )

    assert report["summary"]["case_count"] == 4
    assert report["summary"]["all_passed"] is True
    for item in report["results"]:
        assert item["actual"]["status"] == "dependency_unavailable"
        assert item["actual"]["policy_citations"] == []
        assert item["checks"]["policy_fallback_boundary"] is True
        assert "retrieve_policy" not in item["actual"]["trace_nodes"]


def test_erp_eval_script_is_directly_invokable_from_repo_root():
    project_root = Path(__file__).resolve().parents[3]
    completed = subprocess.run(
        [sys.executable, "scripts/run_erp_diagnosis_eval.py", "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "ERP diagnosis business Golden Cases" in completed.stdout
