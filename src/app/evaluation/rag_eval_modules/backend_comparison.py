from pathlib import Path
from typing import Any

from src.app.evaluation.rag_eval_modules.cases import DEFAULT_RAG_EVAL_FILE
from src.app.evaluation.rag_eval_modules.metrics import _calculate_metric_delta
from src.app.evaluation.rag_eval_modules.single_backend import evaluate_rag_cases
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER
from src.app.evaluation.rag_report import build_backend_evaluation_report


def _build_metric_deltas(
    backend_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(backend_results) < 2:
        return {}

    return _calculate_metric_delta(
        baseline=backend_results[0],
        comparison=backend_results[1],
    )


def _build_pairwise_metric_deltas(
    backend_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pairwise_deltas: list[dict[str, Any]] = []

    for baseline_index, baseline in enumerate(backend_results):
        for comparison in backend_results[baseline_index + 1:]:
            pairwise_deltas.append(
                _calculate_metric_delta(
                    baseline=baseline,
                    comparison=comparison,
                )
            )

    return pairwise_deltas


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


def _build_pairwise_metric_deltas(
    backend_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pairwise_deltas: list[dict[str, Any]] = []

    for baseline_index, baseline in enumerate(backend_results):
        for comparison in backend_results[baseline_index + 1:]:
            pairwise_deltas.append(
                _calculate_metric_delta(
                    baseline=baseline,
                    comparison=comparison,
                )
            )

    return pairwise_deltas


_COMPARISON_SUMMARY_METRICS = [
    "pass_rate",
    "retrieval_decision_accuracy",
    "expected_terms_hit_rate",
    "citation_hit_rate",
    "average_relevance_score",
]


def _build_metric_rankings(
    backend_results: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    rankings: dict[str, list[dict[str, Any]]] = {}

    for metric_name in _COMPARISON_SUMMARY_METRICS:
        metric_items = [
            {
                "retrieval_backend": backend_result["retrieval_backend"],
                "value": backend_result["metrics"][metric_name],
            }
            for backend_result in backend_results
        ]

        metric_items.sort(
            key=lambda item: item["value"],
            reverse=True,
        )

        rankings[metric_name] = metric_items

    return rankings


def _build_metric_winners(
    backend_results: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    winners: dict[str, dict[str, Any]] = {}

    for metric_name in _COMPARISON_SUMMARY_METRICS:
        values = [
            backend_result["metrics"][metric_name]
            for backend_result in backend_results
        ]

        if not values:
            winners[metric_name] = {
                "value": 0.0,
                "winners": [],
                "tie": False,
            }
            continue

        best_value = max(values)

        metric_winners = [
            backend_result["retrieval_backend"]
            for backend_result in backend_results
            if backend_result["metrics"][metric_name] == best_value
        ]

        winners[metric_name] = {
            "value": best_value,
            "winners": metric_winners,
            "tie": len(metric_winners) > 1,
        }

    return winners


def _build_top_improvement_pairs(
    pairwise_metric_deltas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    improvements: list[dict[str, Any]] = []

    for pairwise_delta in pairwise_metric_deltas:
        baseline_backend = pairwise_delta["baseline_backend"]
        comparison_backend = pairwise_delta["comparison_backend"]

        for metric_name in _COMPARISON_SUMMARY_METRICS:
            delta_key = f"{metric_name}_delta"
            delta_value = float(pairwise_delta.get(delta_key, 0.0))

            if delta_value <= 0:
                continue

            improvements.append(
                {
                    "metric": metric_name,
                    "baseline_backend": baseline_backend,
                    "comparison_backend": comparison_backend,
                    "delta": round(delta_value, 6),
                }
            )

    improvements.sort(
        key=lambda item: item["delta"],
        reverse=True,
    )

    return improvements[:5]


def _build_comparison_summary(
    backend_results: list[dict[str, Any]],
    best_backend_by_pass_rate: str,
    best_backend_by_average_relevance: str,
    pairwise_metric_deltas: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    pairwise_metric_deltas = pairwise_metric_deltas or []

    evaluated_backends = [
        backend_result["retrieval_backend"]
        for backend_result in backend_results
    ]

    metric_rankings = _build_metric_rankings(backend_results)
    metric_winners = _build_metric_winners(backend_results)
    top_improvement_pairs = _build_top_improvement_pairs(
        pairwise_metric_deltas
    )

    notes = _build_multi_backend_summary_notes(
        backend_results=backend_results,
        metric_winners=metric_winners,
        top_improvement_pairs=top_improvement_pairs,
    )

    return {
        "total_backends": len(backend_results),
        "evaluated_backends": evaluated_backends,
        "best_backend_by_pass_rate": best_backend_by_pass_rate,
        "best_backend_by_average_relevance": best_backend_by_average_relevance,
        "metric_winners": metric_winners,
        "metric_rankings": metric_rankings,
        "top_improvement_pairs": top_improvement_pairs,
        "notes": notes,
    }


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
    graph_dry_run: bool = True,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
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
            graph_dry_run=graph_dry_run,
            fusion_graph_weight=fusion_graph_weight,
            fusion_vector_weight=fusion_vector_weight,
            graph_chunk_limit=graph_chunk_limit,
            related_entity_limit=related_entity_limit,
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
    pairwise_metric_deltas = _build_pairwise_metric_deltas(backend_results)
    case_comparisons = _build_case_comparisons(backend_results)
    comparison_summary = _build_comparison_summary(
        backend_results=backend_results,
        best_backend_by_pass_rate=best_backend_by_pass_rate,
        best_backend_by_average_relevance=best_backend_by_average_relevance,
        pairwise_metric_deltas=pairwise_metric_deltas,
    )

    comparison_result = {
        "eval_file": eval_file,
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
        "pairwise_metric_deltas": pairwise_metric_deltas,
        "case_comparisons": case_comparisons,
        "comparison_summary": comparison_summary,
        "results": backend_results,
        "graph_dry_run": graph_dry_run,
        "fusion_graph_weight": fusion_graph_weight,
        "fusion_vector_weight": fusion_vector_weight,
        "graph_chunk_limit": graph_chunk_limit,
        "related_entity_limit": related_entity_limit,
        "graph_evaluation_metadata": {
            "graph_fusion_included": "graph_fusion" in backends,
            "graph_dry_run": graph_dry_run,
            "fusion_graph_weight": fusion_graph_weight,
            "fusion_vector_weight": fusion_vector_weight,
        },
    }

    comparison_result["evaluation_report"] = build_backend_evaluation_report(
        comparison_result
    )

    return comparison_result


def _format_backend_list(
    backends: list[str],
) -> str:
    return ", ".join(backends)


def _build_multi_backend_summary_notes(
    backend_results: list[dict[str, Any]],
    metric_winners: dict[str, dict[str, Any]],
    top_improvement_pairs: list[dict[str, Any]],
) -> list[str]:
    if not backend_results:
        return ["No backend was evaluated."]

    evaluated_backends = [
        backend_result["retrieval_backend"]
        for backend_result in backend_results
    ]

    notes = [
        f"Evaluated {len(evaluated_backends)} backends: "
        f"{_format_backend_list(evaluated_backends)}."
    ]

    pass_rate_winner = metric_winners["pass_rate"]
    pass_rate_winners = pass_rate_winner["winners"]
    pass_rate_value = pass_rate_winner["value"]

    if pass_rate_winner["tie"]:
        notes.append(
            "Pass rate is tied at "
            f"{pass_rate_value} by {_format_backend_list(pass_rate_winners)}."
        )
    else:
        notes.append(
            f"Best pass_rate is {pass_rate_winners[0]} "
            f"with value {pass_rate_value}."
        )

    relevance_winner = metric_winners["average_relevance_score"]
    relevance_winners = relevance_winner["winners"]
    relevance_value = relevance_winner["value"]

    if relevance_winner["tie"]:
        notes.append(
            "Average relevance score is tied at "
            f"{relevance_value} by {_format_backend_list(relevance_winners)}."
        )
    else:
        notes.append(
            f"Best average_relevance_score is {relevance_winners[0]} "
            f"with value {relevance_value}."
        )

    pass_rate_improvements = [
        item
        for item in top_improvement_pairs
        if item["metric"] == "pass_rate"
    ]

    if pass_rate_improvements:
        top_pass_rate_improvement = pass_rate_improvements[0]
        notes.append(
            "Largest pass_rate improvement is "
            f"{top_pass_rate_improvement['baseline_backend']} -> "
            f"{top_pass_rate_improvement['comparison_backend']} "
            f"with delta {top_pass_rate_improvement['delta']}."
        )

    relevance_improvements = [
        item
        for item in top_improvement_pairs
        if item["metric"] == "average_relevance_score"
    ]

    if relevance_improvements:
        top_relevance_improvement = relevance_improvements[0]
        notes.append(
            "Largest average_relevance_score improvement is "
            f"{top_relevance_improvement['baseline_backend']} -> "
            f"{top_relevance_improvement['comparison_backend']} "
            f"with delta {top_relevance_improvement['delta']}."
        )

    return notes


def _build_comparison_summary(
    backend_results: list[dict[str, Any]],
    best_backend_by_pass_rate: str,
    best_backend_by_average_relevance: str,
    pairwise_metric_deltas: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    pairwise_metric_deltas = pairwise_metric_deltas or []

    evaluated_backends = [
        backend_result["retrieval_backend"]
        for backend_result in backend_results
    ]

    metric_rankings = _build_metric_rankings(backend_results)
    metric_winners = _build_metric_winners(backend_results)
    top_improvement_pairs = _build_top_improvement_pairs(
        pairwise_metric_deltas
    )

    notes = _build_multi_backend_summary_notes(
        backend_results=backend_results,
        metric_winners=metric_winners,
        top_improvement_pairs=top_improvement_pairs,
    )

    return {
        "total_backends": len(backend_results),
        "evaluated_backends": evaluated_backends,
        "best_backend_by_pass_rate": best_backend_by_pass_rate,
        "best_backend_by_average_relevance": best_backend_by_average_relevance,
        "metric_winners": metric_winners,
        "metric_rankings": metric_rankings,
        "top_improvement_pairs": top_improvement_pairs,
        "notes": notes,
    }

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
    graph_dry_run: bool = True,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
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
            graph_dry_run=graph_dry_run,
            fusion_graph_weight=fusion_graph_weight,
            fusion_vector_weight=fusion_vector_weight,
            graph_chunk_limit=graph_chunk_limit,
            related_entity_limit=related_entity_limit,
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
    pairwise_metric_deltas = _build_pairwise_metric_deltas(backend_results)
    case_comparisons = _build_case_comparisons(backend_results)
    comparison_summary = _build_comparison_summary(
        backend_results=backend_results,
        best_backend_by_pass_rate=best_backend_by_pass_rate,
        best_backend_by_average_relevance=best_backend_by_average_relevance,
        pairwise_metric_deltas=pairwise_metric_deltas,
    )

    comparison_result = {
        "eval_file": eval_file,
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
        "pairwise_metric_deltas": pairwise_metric_deltas,
        "case_comparisons": case_comparisons,
        "comparison_summary": comparison_summary,
        "results": backend_results,
        "graph_dry_run": graph_dry_run,
        "fusion_graph_weight": fusion_graph_weight,
        "fusion_vector_weight": fusion_vector_weight,
        "graph_chunk_limit": graph_chunk_limit,
        "related_entity_limit": related_entity_limit,
        "graph_evaluation_metadata": {
            "graph_fusion_included": "graph_fusion" in backends,
            "graph_dry_run": graph_dry_run,
            "fusion_graph_weight": fusion_graph_weight,
            "fusion_vector_weight": fusion_vector_weight,
        },
    }

    comparison_result["evaluation_report"] = build_backend_evaluation_report(
        comparison_result
    )

    return comparison_result