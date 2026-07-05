from __future__ import annotations

from typing import Any


DEFAULT_PRODUCTION_BACKEND = "hybrid"
TINY_EVAL_CASE_THRESHOLD = 10


def _get_backend_metrics(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    backend_metrics: list[dict[str, Any]] = []

    for item in comparison.get("results", []):
        metrics = item.get("metrics", {})
        backend_metrics.append(
            {
                "retrieval_backend": item.get("retrieval_backend"),
                "pass_rate": metrics.get("pass_rate", 0.0),
                "retrieval_decision_accuracy": metrics.get(
                    "retrieval_decision_accuracy",
                    0.0,
                ),
                "expected_terms_hit_rate": metrics.get(
                    "expected_terms_hit_rate",
                    0.0,
                ),
                "citation_hit_rate": metrics.get("citation_hit_rate", 0.0),
                "average_relevance_score": metrics.get(
                    "average_relevance_score",
                    0.0,
                ),
                "total_cases": metrics.get("total_cases", 0),
                "passed_cases": metrics.get("passed_cases", 0),
            }
        )

    return backend_metrics


def _get_eval_case_count(backend_metrics: list[dict[str, Any]]) -> int:
    if not backend_metrics:
        return 0

    return max(int(item.get("total_cases", 0)) for item in backend_metrics)


def _get_pass_rate_winners(
    comparison: dict[str, Any],
    backend_metrics: list[dict[str, Any]],
) -> list[str]:
    summary = comparison.get("comparison_summary", {})
    metric_winners = summary.get("metric_winners", {})
    pass_rate_winner_info = metric_winners.get("pass_rate", {})
    winners = pass_rate_winner_info.get("winners")

    if isinstance(winners, list) and winners:
        return [str(item) for item in winners]

    if not backend_metrics:
        return []

    max_pass_rate = max(float(item.get("pass_rate", 0.0)) for item in backend_metrics)
    return [
        str(item["retrieval_backend"])
        for item in backend_metrics
        if float(item.get("pass_rate", 0.0)) == max_pass_rate
    ]


def _choose_recommended_backend(
    comparison: dict[str, Any],
    backend_metrics: list[dict[str, Any]],
) -> str | None:
    if not backend_metrics:
        return None

    best_by_relevance = comparison.get("best_backend_by_average_relevance")
    pass_rate_winners = _get_pass_rate_winners(comparison, backend_metrics)

    if best_by_relevance in pass_rate_winners:
        return str(best_by_relevance)

    best_by_pass_rate = comparison.get("best_backend_by_pass_rate")
    if best_by_pass_rate:
        return str(best_by_pass_rate)

    return str(backend_metrics[0].get("retrieval_backend"))


def _build_backend_rank_summary(
    backend_metrics: list[dict[str, Any]],
    recommended_backend: str | None,
) -> list[dict[str, Any]]:
    ranked = sorted(
        backend_metrics,
        key=lambda item: (
            float(item.get("pass_rate", 0.0)),
            float(item.get("average_relevance_score", 0.0)),
        ),
        reverse=True,
    )

    summary: list[dict[str, Any]] = []

    for item in ranked:
        backend = item.get("retrieval_backend")
        if backend == recommended_backend:
            strength = "recommended candidate on current evaluation"
        elif item.get("pass_rate") == ranked[0].get("pass_rate"):
            strength = "top pass-rate group"
        else:
            strength = "comparison backend"

        summary.append(
            {
                "retrieval_backend": backend,
                "pass_rate": item.get("pass_rate", 0.0),
                "retrieval_decision_accuracy": item.get(
                    "retrieval_decision_accuracy",
                    0.0,
                ),
                "expected_terms_hit_rate": item.get(
                    "expected_terms_hit_rate",
                    0.0,
                ),
                "citation_hit_rate": item.get("citation_hit_rate", 0.0),
                "average_relevance_score": item.get(
                    "average_relevance_score",
                    0.0,
                ),
                "passed_cases": item.get("passed_cases", 0),
                "total_cases": item.get("total_cases", 0),
                "strength": strength,
            }
        )

    return summary


def _build_metric_highlights(comparison: dict[str, Any]) -> list[str]:
    highlights: list[str] = []

    summary = comparison.get("comparison_summary", {})
    metric_winners = summary.get("metric_winners", {})

    pass_rate_info = metric_winners.get("pass_rate", {})
    pass_rate_winners = pass_rate_info.get("winners", [])
    pass_rate_value = pass_rate_info.get("value")

    if pass_rate_winners:
        if pass_rate_info.get("tie"):
            highlights.append(
                "Pass rate is tied at "
                f"{pass_rate_value} by {', '.join(pass_rate_winners)}."
            )
        else:
            highlights.append(
                "Best pass_rate is "
                f"{pass_rate_winners[0]} with value {pass_rate_value}."
            )

    relevance_info = metric_winners.get("average_relevance_score", {})
    relevance_winners = relevance_info.get("winners", [])
    relevance_value = relevance_info.get("value")

    if relevance_winners:
        highlights.append(
            "Best average_relevance_score is "
            f"{relevance_winners[0]} with value {relevance_value}."
        )

    top_improvement_pairs = summary.get("top_improvement_pairs", [])
    if top_improvement_pairs:
        top_pair = top_improvement_pairs[0]
        highlights.append(
            "Largest improvement is "
            f"{top_pair.get('baseline_backend')} -> "
            f"{top_pair.get('comparison_backend')} on "
            f"{top_pair.get('metric')} with delta {top_pair.get('delta')}."
        )

    if not highlights:
        notes = summary.get("notes", [])
        highlights.extend(str(note) for note in notes)

    return highlights


def _build_risk_notes(
    comparison: dict[str, Any],
    eval_case_count: int,
    recommended_backend: str | None,
) -> list[str]:
    risk_notes: list[str] = []

    embedding_provider = comparison.get("embedding_provider", "deterministic")

    if eval_case_count <= TINY_EVAL_CASE_THRESHOLD:
        risk_notes.append(
            "The current eval set is small/tiny, so the report should be treated "
            "as a regression and debugging signal rather than a production-level "
            "benchmark."
        )

    if embedding_provider == "deterministic":
        risk_notes.append(
            "The current run uses deterministic embeddings, which are CI-safe but "
            "do not represent real semantic embedding quality."
        )
    elif embedding_provider in {"sentence_transformers", "sentence-transformers", "local"}:
        risk_notes.append(
            "The current run uses a local sentence_transformers semantic embedding "
            "model, so the result depends on local model availability and may be "
            "skipped in CI."
        )

    if recommended_backend and recommended_backend != DEFAULT_PRODUCTION_BACKEND:
        risk_notes.append(
            f"{recommended_backend} is recommended as an experiment candidate, "
            f"but the default backend should remain {DEFAULT_PRODUCTION_BACKEND} "
            "until a larger eval set validates the change."
        )

    return risk_notes


def build_backend_evaluation_report(comparison: dict[str, Any]) -> dict[str, Any]:
    """Build a human-readable backend selection report from an existing comparison.

    This function is intentionally pure:
    - no FastAPI dependency
    - no Chroma dependency
    - no embedding model loading
    - no evaluation re-run
    """

    backend_metrics = _get_backend_metrics(comparison)
    eval_case_count = _get_eval_case_count(backend_metrics)
    recommended_backend = _choose_recommended_backend(comparison, backend_metrics)

    embedding_provider = comparison.get("embedding_provider", "deterministic")

    is_tiny_eval = eval_case_count <= TINY_EVAL_CASE_THRESHOLD
    uses_deterministic_embedding = embedding_provider == "deterministic"

    default_backend_should_change = bool(
        recommended_backend
        and recommended_backend != DEFAULT_PRODUCTION_BACKEND
        and not is_tiny_eval
        and not uses_deterministic_embedding
    )

    if recommended_backend is None:
        recommendation_reason = "No backend metrics are available for recommendation."
    elif default_backend_should_change:
        recommendation_reason = (
            f"{recommended_backend} is recommended because it performs best under "
            "the current selection policy and the evaluation is not limited to a "
            "tiny deterministic run."
        )
    else:
        recommendation_reason = (
            f"{recommended_backend} is the current experiment candidate, but the "
            f"default backend should remain {DEFAULT_PRODUCTION_BACKEND} until "
            "larger and more representative evaluation data is available."
        )

    return {
        "recommended_backend": recommended_backend,
        "recommendation_reason": recommendation_reason,
        "default_backend": DEFAULT_PRODUCTION_BACKEND,
        "default_backend_should_change": default_backend_should_change,
        "selection_policy": "keep_default_hybrid_until_larger_eval_set",
        "embedding_provider": embedding_provider,
        "embedding_model": comparison.get("embedding_model"),
        "eval_file": comparison.get("eval_file"),
        "eval_case_count": eval_case_count,
        "metric_highlights": _build_metric_highlights(comparison),
        "risk_notes": _build_risk_notes(
            comparison=comparison,
            eval_case_count=eval_case_count,
            recommended_backend=recommended_backend,
        ),
        "backend_rank_summary": _build_backend_rank_summary(
            backend_metrics=backend_metrics,
            recommended_backend=recommended_backend,
        ),
        "interpretation": (
            "This report converts backend evaluation metrics into an engineering "
            "selection summary. It should be used to guide backend experiments, "
            "not as a production benchmark by itself."
        ),
    }