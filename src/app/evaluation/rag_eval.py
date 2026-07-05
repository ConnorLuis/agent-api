import json
from pathlib import Path
from typing import Any

from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER
from src.app.rag.retrieval_backend import DEFAULT_RETRIEVAL_BACKEND


DEFAULT_RAG_EVAL_FILE = Path("eval_cases/rag_agentic_eval.jsonl")


def load_rag_eval_cases(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
) -> list[dict[str, Any]]:
    path = Path(eval_file)

    cases: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()

            if not stripped:
                continue

            cases.append(json.loads(stripped))

    return cases

def _normalize_expected_terms(case: dict[str, Any]) -> list[str]:
    raw_terms = case.get("expected_terms", [])

    return [
        str(term).lower()
        for term in raw_terms
        if str(term).strip()
    ]


def _expected_terms_hit(
    answer: str,
    expected_terms: list[str],
) -> bool:
    normalized_answer = answer.lower()

    return all(
        term in normalized_answer
        for term in expected_terms
    )

def _citation_hit(
    citations: list[str],
    expected_source: str | None,
) -> bool:
    if not expected_source:
        return True

    return any(
        expected_source in citation
        for citation in citations
    )


def _retrieval_decision_hit(
    actual: bool,
    expected: bool,
) -> bool:
    return actual is expected


def _safe_average(values: list[float]) -> float:
    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        6,
    )


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
                "retrieval_metadata": result.get("retrieval_metadata", {}),
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
    }



def _build_metric_deltas(
    backend_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(backend_results) < 2:
        return {}

    baseline = backend_results[0]
    comparison = backend_results[1]

    baseline_metrics = baseline["metrics"]
    comparison_metrics = comparison["metrics"]

    return {
        "baseline_backend": baseline["retrieval_backend"],
        "comparison_backend": comparison["retrieval_backend"],
        "pass_rate_delta": round(
            comparison_metrics["pass_rate"] - baseline_metrics["pass_rate"],
            6,
        ),
        "retrieval_decision_accuracy_delta": round(
            comparison_metrics["retrieval_decision_accuracy"]
            - baseline_metrics["retrieval_decision_accuracy"],
            6,
        ),
        "expected_terms_hit_rate_delta": round(
            comparison_metrics["expected_terms_hit_rate"]
            - baseline_metrics["expected_terms_hit_rate"],
            6,
        ),
        "citation_hit_rate_delta": round(
            comparison_metrics["citation_hit_rate"]
            - baseline_metrics["citation_hit_rate"],
            6,
        ),
        "average_relevance_score_delta": round(
            comparison_metrics["average_relevance_score"]
            - baseline_metrics["average_relevance_score"],
            6,
        ),
    }


def _build_case_comparisons(
    backend_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not backend_results:
        return []

    case_ids: list[str] = []

    for backend_result in backend_results:
        for case in backend_result["cases"]:
            case_id = str(case["case_id"])
            if case_id not in case_ids:
                case_ids.append(case_id)

    comparisons: list[dict[str, Any]] = []

    for case_id in case_ids:
        backend_case_results: list[dict[str, Any]] = []

        for backend_result in backend_results:
            matched_case = next(
                (
                    case
                    for case in backend_result["cases"]
                    if str(case["case_id"]) == case_id
                ),
                None,
            )

            if matched_case is None:
                continue

            backend_case_results.append(
                {
                    "retrieval_backend": backend_result["retrieval_backend"],
                    "passed": bool(matched_case["passed"]),
                    "retrieval_decision_pass": bool(
                        matched_case["retrieval_decision_pass"]
                    ),
                    "expected_terms_pass": bool(
                        matched_case["expected_terms_pass"]
                    ),
                    "citation_pass": bool(matched_case["citation_pass"]),
                    "relevance_score": float(matched_case["relevance_score"]),
                    "citations": list(matched_case.get("citations", [])),
                    "matched_expected_terms": list(
                        matched_case.get("matched_expected_terms", [])
                    ),
                    "steps": list(matched_case.get("steps", [])),
                }
            )

        passing_backends = [
            item["retrieval_backend"]
            for item in backend_case_results
            if item["passed"]
        ]

        if len(passing_backends) == 1:
            winner_by_pass = passing_backends[0]
        elif len(passing_backends) > 1:
            winner_by_pass = "tie"
        else:
            winner_by_pass = "none"

        if backend_case_results:
            winner_by_relevance = max(
                backend_case_results,
                key=lambda item: item["relevance_score"],
            )["retrieval_backend"]
        else:
            winner_by_relevance = "none"

        comparisons.append(
            {
                "case_id": case_id,
                "winner_by_pass": winner_by_pass,
                "winner_by_relevance": winner_by_relevance,
                "backend_results": backend_case_results,
            }
        )

    return comparisons


def _build_comparison_summary(
    backend_results: list[dict[str, Any]],
    best_backend_by_pass_rate: str,
    best_backend_by_average_relevance: str,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "total_backends": len(backend_results),
        "best_backend_by_pass_rate": best_backend_by_pass_rate,
        "best_backend_by_average_relevance": best_backend_by_average_relevance,
        "notes": [],
    }

    if len(backend_results) < 2:
        summary["notes"].append("Only one backend was evaluated.")
        return summary

    baseline = backend_results[0]
    comparison = backend_results[1]

    baseline_backend = baseline["retrieval_backend"]
    comparison_backend = comparison["retrieval_backend"]

    baseline_metrics = baseline["metrics"]
    comparison_metrics = comparison["metrics"]

    if comparison_metrics["pass_rate"] > baseline_metrics["pass_rate"]:
        summary["notes"].append(
            f"{comparison_backend} has a higher pass_rate than {baseline_backend}."
        )
    elif comparison_metrics["pass_rate"] < baseline_metrics["pass_rate"]:
        summary["notes"].append(
            f"{baseline_backend} has a higher pass_rate than {comparison_backend}."
        )
    else:
        summary["notes"].append(
            f"{baseline_backend} and {comparison_backend} have the same pass_rate."
        )

    if (
        comparison_metrics["average_relevance_score"]
        > baseline_metrics["average_relevance_score"]
    ):
        summary["notes"].append(
            f"{comparison_backend} has a higher average_relevance_score than {baseline_backend}."
        )
    elif (
        comparison_metrics["average_relevance_score"]
        < baseline_metrics["average_relevance_score"]
    ):
        summary["notes"].append(
            f"{baseline_backend} has a higher average_relevance_score than {comparison_backend}."
        )
    else:
        summary["notes"].append(
            f"{baseline_backend} and {comparison_backend} have the same average_relevance_score."
        )

    return summary

def compare_rag_retrieval_backends(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
    backends: list[str] | None = None,
    source_filter: str | None = None,
    max_chars: int = 500,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    rebuild_index: bool = True,
) -> dict[str, Any]:
    selected_backends = backends or ["hybrid", "chroma"]

    backend_results = []

    for backend in selected_backends:
        result = evaluate_rag_cases(
            eval_file=eval_file,
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            keyword_weight=keyword_weight,
            vector_weight=vector_weight,
            retrieval_backend=backend,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            rebuild_index=rebuild_index,
        )

        backend_results.append(result)

    best_backend_by_pass_rate = max(
        backend_results,
        key=lambda item: item["metrics"]["pass_rate"],
    )["retrieval_backend"] if backend_results else ""

    best_backend_by_average_relevance = max(
        backend_results,
        key=lambda item: item["metrics"]["average_relevance_score"],
    )["retrieval_backend"] if backend_results else ""

    metric_deltas = _build_metric_deltas(backend_results)
    case_comparisons = _build_case_comparisons(backend_results)
    comparison_summary = _build_comparison_summary(
        backend_results=backend_results,
        best_backend_by_pass_rate=best_backend_by_pass_rate,
        best_backend_by_average_relevance=best_backend_by_average_relevance,
    )

    return {
        "eval_file": str(eval_file),
        "backends": selected_backends,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "rebuild_index": rebuild_index,
        "best_backend_by_pass_rate": best_backend_by_pass_rate,
        "best_backend_by_average_relevance": best_backend_by_average_relevance,
        "metric_deltas": metric_deltas,
        "case_comparisons": case_comparisons,
        "comparison_summary": comparison_summary,
        "results": backend_results,
    }
