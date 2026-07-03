from typing import Any

from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM


def _collect_grounding_terms(
    retrieval_results: list[dict[str, Any]],
) -> list[str]:
    terms = []

    for item in retrieval_results:
        for term in item.get("matched_terms", []):
            normalized = str(term).strip().lower()

            if normalized and normalized not in terms:
                terms.append(normalized)

    return sorted(terms)


def _terms_in_answer(
    final_answer: str,
    terms: list[str],
) -> list[str]:
    normalized_answer = final_answer.lower()

    return [
        term
        for term in terms
        if term.lower() in normalized_answer
    ]


def _confidence_label(
    retrieval_needed: bool,
    verification_pass: bool,
    relevance_score: float,
) -> str:
    if not verification_pass:
        return "low"

    if not retrieval_needed:
        return "high"

    if relevance_score >= 0.35:
        return "high"

    if relevance_score >= 0.1:
        return "medium"

    return "low"


def _build_verification(
    result: dict[str, Any],
) -> dict[str, Any]:
    retrieval_needed = bool(result["retrieval_needed"])
    final_answer = str(result["final_answer"])
    citations = list(result["citations"])
    retrieval_results = list(result["retrieval_results"])
    relevance_score = float(result["relevance_score"])

    retrieved_chunk_ids = [
        item["chunk_id"]
        for item in retrieval_results
    ]

    unsupported_citations = [
        citation
        for citation in citations
        if citation not in retrieved_chunk_ids
    ]

    citation_coverage_pass = len(unsupported_citations) == 0

    cited_in_answer = [
        citation
        for citation in citations
        if citation in final_answer
    ]

    answer_has_citation = (
        len(cited_in_answer) > 0
        or ("引用来源" in final_answer and len(citations) > 0)
    )

    grounding_terms = _collect_grounding_terms(retrieval_results)
    matched_grounding_terms = _terms_in_answer(
        final_answer=final_answer,
        terms=grounding_terms,
    )

    risk_flags = []

    if retrieval_needed:
        if not citations:
            risk_flags.append("no_citations")

        if not citation_coverage_pass:
            risk_flags.append("unsupported_citations")

        if not answer_has_citation:
            risk_flags.append("no_citation_in_answer")

        if relevance_score <= 0:
            risk_flags.append("low_relevance_score")

        if not matched_grounding_terms:
            risk_flags.append("no_grounding_terms")
    else:
        if citations:
            risk_flags.append("direct_path_has_citations")

        if retrieval_results:
            risk_flags.append("direct_path_has_retrieval_results")

        if relevance_score != 0.0:
            risk_flags.append("direct_path_has_relevance_score")

    answer_supported = len(risk_flags) == 0
    verification_pass = answer_supported

    return {
        "verification_mode": "retrieval" if retrieval_needed else "direct",
        "answer_supported": answer_supported,
        "verification_pass": verification_pass,
        "confidence": _confidence_label(
            retrieval_needed=retrieval_needed,
            verification_pass=verification_pass,
            relevance_score=relevance_score,
        ),
        "answer_has_citation": answer_has_citation,
        "citation_coverage_pass": citation_coverage_pass,
        "cited_in_answer": cited_in_answer,
        "unsupported_citations": unsupported_citations,
        "grounding_terms": grounding_terms,
        "matched_grounding_terms": matched_grounding_terms,
        "risk_flags": risk_flags,
    }


def verify_agentic_rag_answer(
    query: str,
    top_k: int = 3,
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
) -> dict[str, Any]:
    result = invoke_agentic_rag(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
    )

    verification = _build_verification(result)

    return {
        "query": result["query"],
        "rewritten_query": result["rewritten_query"],
        "retrieval_needed": result["retrieval_needed"],
        "relevance_score": result["relevance_score"],
        "citations": result["citations"],
        "retrieval_results": result["retrieval_results"],
        "final_answer": result["final_answer"],
        "steps": result["steps"],
        "verification": verification,
    }