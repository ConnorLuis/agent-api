from pathlib import Path
from typing import Any

from src.app.evaluation.rag_eval_modules.cases import (
    DEFAULT_RAG_EVAL_FILE,
    _normalize_expected_terms,
    load_rag_eval_cases,
)
from src.app.evaluation.rag_eval_modules.metrics import (
    _citation_hit,
    _expected_terms_hit,
    _retrieval_decision_hit,
    _safe_average,
)
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER
from src.app.rag.graph_fusion_metadata import build_graph_vector_contribution
from src.app.rag.retrieval_backend import DEFAULT_RETRIEVAL_BACKEND


def evaluate_rag_cases(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
    source_filter: str | None = None,
    max_chars: int = 500,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = DEFAULT_RETRIEVAL_BACKEND,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    rebuild_index: bool = True,
    graph_dry_run: bool = True,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
) -> dict[str, Any]:
    cases = load_rag_eval_cases(eval_file=eval_file)

    case_results: list[dict[str, Any]] = []

    retrieval_decision_hits = 0
    expected_terms_hits = 0
    citation_hits = 0
    passed_cases = 0
    relevance_scores: list[float] = []

    for case in cases:
        query = str(case["query"])
        expected_retrieval_needed = bool(case.get("expected_retrieval_needed", True))
        expected_terms = _normalize_expected_terms(case)
        expected_source = case.get("expected_source")

        result = invoke_agentic_rag(
            query=query,
            top_k=int(case.get("top_k", 2)),
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            keyword_weight=keyword_weight,
            vector_weight=vector_weight,
            retrieval_backend=retrieval_backend,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            rebuild_index=rebuild_index,
            graph_dry_run=graph_dry_run,
            fusion_graph_weight=fusion_graph_weight,
            fusion_vector_weight=fusion_vector_weight,
            graph_chunk_limit=graph_chunk_limit,
            related_entity_limit=related_entity_limit,
        )

        final_answer = result["final_answer"]
        retrieval_needed = bool(result["retrieval_needed"])
        citations = list(result["citations"])
        relevance_score = float(result["relevance_score"])

        retrieval_decision_pass = _retrieval_decision_hit(
            actual=retrieval_needed,
            expected=expected_retrieval_needed,
        )
        expected_terms_pass = _expected_terms_hit(
            answer=final_answer,
            expected_terms=expected_terms,
        )
        citation_pass = _citation_hit(
            citations=citations,
            expected_source=expected_source,
        )

        case_pass = (
            retrieval_decision_pass
            and expected_terms_pass
            and citation_pass
        )

        retrieval_decision_hits += int(retrieval_decision_pass)
        expected_terms_hits += int(expected_terms_pass)
        citation_hits += int(citation_pass)
        passed_cases += int(case_pass)
        relevance_scores.append(relevance_score)

        normalized_answer = final_answer.lower()

        matched_expected_terms = [
            term
            for term in expected_terms
            if term in normalized_answer
        ]

        expected_citation_keywords = [
            str(keyword)
            for keyword in case.get("expected_citation_keywords", [])
            if str(keyword).strip()
        ]

        retrieval_metadata = result.get("retrieval_metadata", {}) or {}
        actual_backend = result.get("retrieval_backend", retrieval_backend)

        graph_vector_contribution = build_graph_vector_contribution(
            retrieval_backend=actual_backend,
            retrieval_metadata=retrieval_metadata,
        )

        case_results.append(
            {
                "case_id": case.get("case_id", ""),
                "query": query,
                "expected_retrieval_needed": expected_retrieval_needed,
                "actual_retrieval_needed": retrieval_needed,
                "retrieval_decision_pass": retrieval_decision_pass,

                # Existing Day25 schema fields.
                "expected_terms": expected_terms,
                "matched_expected_terms": matched_expected_terms,
                "expected_citation_keywords": expected_citation_keywords,
                "final_answer_preview": final_answer[:200],
                "passed": case_pass,

                # Extra fields kept for Day33 backend-aware debugging.
                "expected_terms_pass": expected_terms_pass,
                "expected_source": expected_source,
                "citations": citations,
                "citation_pass": citation_pass,
                "relevance_score": relevance_score,
                "pass": case_pass,
                "final_answer": final_answer,
                "retrieval_backend": result.get("retrieval_backend", retrieval_backend),
                "retrieval_metadata": retrieval_metadata,
                "graph_vector_contribution": graph_vector_contribution,
                "steps": result.get("steps", []),
            }
        )

    total_cases = len(cases)

    metrics = {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "pass_rate": round(
            passed_cases / total_cases,
            6,
        )
        if total_cases
        else 0.0,
        "retrieval_decision_accuracy": round(
            retrieval_decision_hits / total_cases,
            6,
        )
        if total_cases
        else 0.0,
        "expected_terms_hit_rate": round(
            expected_terms_hits / total_cases,
            6,
        )
        if total_cases
        else 0.0,
        "citation_hit_rate": round(
            citation_hits / total_cases,
            6,
        )
        if total_cases
        else 0.0,
        "average_relevance_score": _safe_average(relevance_scores),
    }

    return {
        "eval_file": str(eval_file),
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "retrieval_backend": retrieval_backend,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "rebuild_index": rebuild_index,
        "metrics": metrics,
        "cases": case_results,
        "graph_dry_run": graph_dry_run,
        "fusion_graph_weight": fusion_graph_weight,
        "fusion_vector_weight": fusion_vector_weight,
        "graph_chunk_limit": graph_chunk_limit,
        "related_entity_limit": related_entity_limit,
        "graph_evaluation_metadata": {
            "graph_fusion_enabled": retrieval_backend == "graph_fusion",
            "graph_dry_run": graph_dry_run,
            "fusion_graph_weight": fusion_graph_weight,
            "fusion_vector_weight": fusion_vector_weight,
        },
    }