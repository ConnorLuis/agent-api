from src.app.business.erp_diagnosis.policy import (
    build_policy_query,
    retrieve_erp_policy_evidence,
)
from src.app.business.erp_diagnosis.root_causes import RootCauseCode


def test_policy_query_drives_existing_agentic_rag_retrieval_branch():
    query = build_policy_query(RootCauseCode.ORG_SCOPE_DENIED)
    assert query.startswith("请检索知识库：")
    assert "ORG_SCOPE_DENIED" in query


def test_policy_retrieval_returns_erp_citation_for_permission_code():
    result = retrieve_erp_policy_evidence([RootCauseCode.ORG_SCOPE_DENIED])

    assert result["retrieval_backend"] == "hybrid"
    assert result["source_filter"] == "knowledge/erp"
    assert result["citations"]
    assert result["citations"][0].startswith("knowledge/erp/permission_rules.md::chunk-")
    assert result["evidence"][0]["root_cause_code"] == "ORG_SCOPE_DENIED"


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
