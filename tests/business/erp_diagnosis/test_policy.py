from src.app.business.erp_diagnosis.policy import (
    build_policy_query,
    get_policy_source_filter,
    retrieve_erp_policy_evidence,
)
from src.app.business.erp_diagnosis.root_causes import RootCauseCode


def test_policy_query_drives_existing_agentic_rag_retrieval_branch():
    query = build_policy_query(RootCauseCode.ORG_SCOPE_DENIED)
    assert query.startswith("请检索知识库：")
    assert "ORG_SCOPE_DENIED" in query


def test_permission_root_causes_route_to_authoritative_permission_policy():
    for code in (
        RootCauseCode.ROLE_MISSING,
        RootCauseCode.ORG_SCOPE_DENIED,
        RootCauseCode.DATA_PERMISSION_DENIED,
        RootCauseCode.INVALID_DOCUMENT_STATE,
    ):
        assert get_policy_source_filter(code) == "knowledge/erp/permission_rules.md"


def test_policy_retrieval_returns_erp_citation_for_permission_code():
    result = retrieve_erp_policy_evidence([RootCauseCode.ORG_SCOPE_DENIED])

    assert result["retrieval_backend"] == "hybrid"
    assert result["source_filter"] == "knowledge/erp"
    assert result["citations"]
    assert result["citations"][0].startswith("knowledge/erp/permission_rules.md::chunk-")
    assert result["evidence"][0]["root_cause_code"] == "ORG_SCOPE_DENIED"
    assert result["retrieval_runs"][0]["source_filter"] == "knowledge/erp/permission_rules.md"


def test_role_missing_retrieval_cannot_drift_to_approval_policy():
    result = retrieve_erp_policy_evidence([RootCauseCode.ROLE_MISSING])

    assert result["citations"]
    assert result["citations"][0].startswith("knowledge/erp/permission_rules.md::chunk-")
    assert all("approval_rules.md" not in citation for citation in result["citations"])


def test_approval_and_transfer_codes_route_to_their_policy_domains():
    assert (
        get_policy_source_filter(RootCauseCode.APPROVAL_FLOW_UNBOUND)
        == "knowledge/erp/approval_rules.md"
    )
    assert (
        get_policy_source_filter(RootCauseCode.APPROVER_UNRESOLVED)
        == "knowledge/erp/approval_rules.md"
    )
    assert (
        get_policy_source_filter(RootCauseCode.TRANSFER_RULE_MISSING)
        == "knowledge/erp/transfer_rules.md"
    )


def test_policy_retrieval_skips_dependency_and_insufficient_evidence_codes():
    result = retrieve_erp_policy_evidence(
        [
            RootCauseCode.DEPENDENCY_UNAVAILABLE,
            RootCauseCode.INSUFFICIENT_EVIDENCE,
        ]
    )
    assert result["citations"] == []
    assert result["evidence"] == []
    assert result["retrieval_runs"] == []
