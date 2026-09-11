from src.app.business.erp_diagnosis.root_causes import RootCauseCode
from src.app.business.erp_diagnosis.service import SyntheticERPReadService
from src.app.business.erp_diagnosis.workflow import (
    build_erp_diagnosis_graph,
    invoke_erp_diagnosis,
)


def test_workflow_diagnoses_org_scope_denied_with_policy_citation(unique_thread):
    result = invoke_erp_diagnosis(
        query="为什么这张采购订单提交不了？",
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        thread_id=unique_thread("erp-org-scope"),
        trace_id="test-erp-org-scope-trace",
    )

    assert result["status"] == "diagnosed"
    assert RootCauseCode.ORG_SCOPE_DENIED.value in result["root_cause_codes"]
    assert result["policy_citations"]
    assert any("permission_rules.md" in item for item in result["policy_citations"])
    assert result["verification_pass"] is True
    assert result["verification_flags"] == []
    assert result["steps"] == [
        "analyze_request",
        "collect_business_evidence",
        "diagnose_root_cause",
        "retrieve_policy",
        "compose_diagnosis",
        "verify_diagnosis",
    ]


def test_workflow_diagnoses_approval_flow_unbound(unique_thread):
    result = invoke_erp_diagnosis(
        query="费用单为什么提交审批失败？",
        user_id="SYN-U005",
        document_id="SYN-EX-002",
        operation="SUBMIT",
        thread_id=unique_thread("erp-approval-unbound"),
        trace_id="test-erp-approval-unbound-trace",
    )

    assert result["status"] == "diagnosed"
    assert result["root_cause_codes"] == [RootCauseCode.APPROVAL_FLOW_UNBOUND.value]
    assert any("approval_rules.md" in item for item in result["policy_citations"])
    assert result["verification_pass"] is True


def test_workflow_diagnoses_approver_unresolved(unique_thread):
    result = invoke_erp_diagnosis(
        query="为什么采购订单审批不下去？",
        user_id="SYN-U007",
        document_id="SYN-PO-004",
        operation="APPROVE",
        thread_id=unique_thread("erp-approver-unresolved"),
        trace_id="test-erp-approver-unresolved-trace",
    )

    assert result["status"] == "diagnosed"
    assert result["root_cause_codes"] == [RootCauseCode.APPROVER_UNRESOLVED.value]
    assert result["verification_pass"] is True


def test_workflow_diagnoses_transfer_rule_missing(unique_thread):
    result = invoke_erp_diagnosis(
        query="这张采购申请为什么不能传成不存在的目标单？",
        user_id="SYN-U001",
        document_id="SYN-PR-001",
        operation="TRANSFER",
        target_document_type="UnknownTargetDocument",
        thread_id=unique_thread("erp-transfer-missing"),
        trace_id="test-erp-transfer-missing-trace",
    )

    assert result["status"] == "diagnosed"
    assert RootCauseCode.TRANSFER_RULE_MISSING.value in result["root_cause_codes"]
    assert any("transfer_rules.md" in item for item in result["policy_citations"])
    assert result["verification_pass"] is True


def test_workflow_returns_no_issue_for_known_good_submit_case(unique_thread):
    result = invoke_erp_diagnosis(
        query="检查这张单据能不能提交",
        user_id="SYN-U001",
        document_id="SYN-PO-001",
        operation="SUBMIT",
        thread_id=unique_thread("erp-no-issue"),
        trace_id="test-erp-no-issue-trace",
    )

    assert result["status"] == "no_issue"
    assert result["root_cause_codes"] == [RootCauseCode.NO_ISSUE_DETECTED.value]
    assert result["policy_citations"] == []
    assert result["verification_pass"] is True


def test_workflow_returns_needs_input_without_required_business_context(unique_thread):
    result = invoke_erp_diagnosis(
        query="为什么审批不了？",
        thread_id=unique_thread("erp-needs-input"),
        trace_id="test-erp-needs-input-trace",
    )

    assert result["status"] == "needs_input"
    assert result["root_cause_codes"] == [RootCauseCode.INSUFFICIENT_EVIDENCE.value]
    assert result["policy_citations"] == []
    assert result["verification_pass"] is True


def test_same_thread_reuses_business_context_from_checkpoint(unique_thread):
    thread_id = unique_thread("erp-memory")
    first = invoke_erp_diagnosis(
        query="这张采购订单为什么提交不了？",
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        thread_id=thread_id,
        trace_id="test-erp-memory-trace-1",
    )
    second = invoke_erp_diagnosis(
        query="再检查一次，为什么还是不行？",
        thread_id=thread_id,
        trace_id="test-erp-memory-trace-2",
    )

    assert first["thread_id"] == second["thread_id"] == thread_id
    assert second["user_id"] == "SYN-U001"
    assert second["document_id"] == "SYN-PO-002"
    assert second["operation"] == "SUBMIT"
    assert RootCauseCode.ORG_SCOPE_DENIED.value in second["root_cause_codes"]


class FailingERPReadService(SyntheticERPReadService):
    def get_user_access_profile(self, user_id: str):
        raise RuntimeError("synthetic dependency failure")


def test_dependency_failure_does_not_fall_back_to_policy_rag(unique_thread):
    graph = build_erp_diagnosis_graph(
        service=FailingERPReadService(),
        with_checkpointer=False,
    )
    result = invoke_erp_diagnosis(
        query="为什么采购订单提交不了？",
        user_id="SYN-U001",
        document_id="SYN-PO-001",
        operation="SUBMIT",
        thread_id=unique_thread("erp-dependency"),
        trace_id="test-erp-dependency-trace",
        graph=graph,
    )

    assert result["status"] == "dependency_unavailable"
    assert result["root_cause_codes"] == [RootCauseCode.DEPENDENCY_UNAVAILABLE.value]
    assert result["policy_citations"] == []
    assert "retrieve_policy" not in result["steps"]
    assert result["verification_pass"] is True
