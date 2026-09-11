from __future__ import annotations

from typing import Any, Iterable

from src.app.business.erp_diagnosis.root_causes import RootCauseCode
from src.app.rag.agentic_graph import invoke_agentic_rag


ERP_POLICY_SOURCE_FILTER = "knowledge/erp"

_POLICY_QUERY_HINTS: dict[RootCauseCode, str] = {
    RootCauseCode.ROLE_MISSING: "角色授权 role permission",
    RootCauseCode.ORG_SCOPE_DENIED: "组织范围 organization scope",
    RootCauseCode.DATA_PERMISSION_DENIED: "数据权限 data permission",
    RootCauseCode.APPROVAL_FLOW_UNBOUND: "审批流绑定 approval flow",
    RootCauseCode.APPROVER_UNRESOLVED: "审批人解析 approver",
    RootCauseCode.TRANSFER_RULE_MISSING: "传单规则 transfer rule",
    RootCauseCode.INVALID_DOCUMENT_STATE: "单据状态 document state",
}

_NON_POLICY_CODES = {
    RootCauseCode.DEPENDENCY_UNAVAILABLE,
    RootCauseCode.INSUFFICIENT_EVIDENCE,
    RootCauseCode.NO_ISSUE_DETECTED,
}


def build_policy_query(code: RootCauseCode) -> str:
    hint = _POLICY_QUERY_HINTS.get(code, "ERP 业务规则")
    # The prefix intentionally drives the existing Agentic-RAG query analyzer
    # onto its retrieval branch; query_rewriter then strips the prefix.
    return f"请检索知识库：{code.value} {hint}"


def retrieve_erp_policy_evidence(
    root_cause_codes: Iterable[RootCauseCode | str],
    *,
    top_k: int = 2,
) -> dict[str, Any]:
    """
    Reuse the existing Agentic RAG workflow for static ERP policy evidence.

    Real-time ERP facts never fall back to this function. It is called only
    after MCP business facts have produced controlled root-cause candidates.
    """
    evidence: list[dict[str, Any]] = []
    citations: list[str] = []
    retrieval_runs: list[dict[str, Any]] = []

    normalized_codes: list[RootCauseCode] = []
    for value in root_cause_codes:
        code = value if isinstance(value, RootCauseCode) else RootCauseCode(value)
        if code in _NON_POLICY_CODES or code in normalized_codes:
            continue
        normalized_codes.append(code)

    for code in normalized_codes:
        result = invoke_agentic_rag(
            query=build_policy_query(code),
            top_k=top_k,
            source_filter=ERP_POLICY_SOURCE_FILTER,
            retrieval_backend="hybrid",
            embedding_provider="deterministic",
            rebuild_index=False,
            graph_dry_run=True,
        )
        retrieval_runs.append(
            {
                "root_cause_code": code.value,
                "retrieval_needed": result.get("retrieval_needed", False),
                "retrieval_backend": result.get("retrieval_backend"),
                "relevance_score": result.get("relevance_score", 0.0),
                "citations": list(result.get("citations", [])),
            }
        )

        result_citations = list(result.get("citations", []))
        retrieval_results = list(result.get("retrieval_results", []))
        if not result_citations or not retrieval_results:
            continue

        citation = str(result_citations[0])
        top_result = retrieval_results[0]
        if citation not in citations:
            citations.append(citation)

        evidence.append(
            {
                "root_cause_code": code.value,
                "citation": citation,
                "source": str(top_result.get("source", "")),
                "relevance_score": float(result.get("relevance_score", 0.0)),
                "excerpt": str(top_result.get("content", ""))[:240],
            }
        )

    return {
        "citations": citations,
        "evidence": evidence,
        "retrieval_runs": retrieval_runs,
        "retrieval_backend": "hybrid",
        "source_filter": ERP_POLICY_SOURCE_FILTER,
    }
