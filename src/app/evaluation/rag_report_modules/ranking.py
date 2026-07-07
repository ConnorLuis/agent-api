from typing import Any


def _get_backend_metrics(comparison: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metrics_by_backend: dict[str, dict[str, Any]] = {}

    for item in comparison.get("results", []):
        backend = item.get("retrieval_backend")
        if backend:
            metrics_by_backend[backend] = item.get("metrics", {})

    return metrics_by_backend


def _get_eval_case_count(comparison: dict[str, Any]) -> int:
    counts = []

    for item in comparison.get("results", []):
        metrics = item.get("metrics", {})
        total_cases = metrics.get("total_cases")
        if isinstance(total_cases, int):
            counts.append(total_cases)

    if counts:
        return max(counts)

    case_ids = {
        case.get("case_id")
        for case in comparison.get("case_comparisons", [])
        if case.get("case_id")
    }

    return len(case_ids)


def _get_pass_rate_winners(comparison: dict[str, Any]) -> list[str]:
    summary = comparison.get("comparison_summary", {})
    metric_winners = summary.get("metric_winners", {})
    pass_rate_info = metric_winners.get("pass_rate", {})
    winners = pass_rate_info.get("winners", [])

    if winners:
        return list(winners)

    metrics_by_backend = _get_backend_metrics(comparison)

    if not metrics_by_backend:
        return []

    max_pass_rate = max(
        metrics.get("pass_rate", 0.0)
        for metrics in metrics_by_backend.values()
    )

    return [
        backend
        for backend, metrics in metrics_by_backend.items()
        if metrics.get("pass_rate", 0.0) == max_pass_rate
    ]


def _get_best_relevance_backend(comparison: dict[str, Any]) -> str:
    summary = comparison.get("comparison_summary", {})
    metric_winners = summary.get("metric_winners", {})
    relevance_info = metric_winners.get("average_relevance_score", {})
    winners = relevance_info.get("winners", [])

    if winners:
        return winners[0]

    best_backend = comparison.get("best_backend_by_average_relevance")
    if best_backend:
        return str(best_backend)

    metrics_by_backend = _get_backend_metrics(comparison)

    if not metrics_by_backend:
        return ""

    return max(
        metrics_by_backend,
        key=lambda backend: metrics_by_backend[backend].get(
            "average_relevance_score",
            0.0,
        ),
    )


def _choose_recommended_backend(comparison: dict[str, Any]) -> str:
    pass_rate_winners = _get_pass_rate_winners(comparison)
    best_relevance_backend = _get_best_relevance_backend(comparison)

    if best_relevance_backend in pass_rate_winners:
        return best_relevance_backend

    if pass_rate_winners:
        return pass_rate_winners[0]

    return best_relevance_backend


def _build_backend_rank_summary(
    comparison: dict[str, Any],
    recommended_backend: str,
) -> list[dict[str, Any]]:
    metrics_by_backend = _get_backend_metrics(comparison)
    pass_rate_winners = set(_get_pass_rate_winners(comparison))

    ranked_backends = sorted(
        metrics_by_backend,
        key=lambda backend: (
            metrics_by_backend[backend].get("pass_rate", 0.0),
            metrics_by_backend[backend].get("average_relevance_score", 0.0),
        ),
        reverse=True,
    )

    summary = []

    for backend in ranked_backends:
        metrics = metrics_by_backend[backend]

        if backend == recommended_backend:
            strength = "recommended candidate on current evaluation"
        elif backend in pass_rate_winners:
            strength = "top pass-rate group"
        else:
            strength = "comparison backend"

        summary.append(
            {
                "retrieval_backend": backend,
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
                "passed_cases": metrics.get("passed_cases", 0),
                "total_cases": metrics.get("total_cases", 0),
                "strength": strength,
            }
        )

    return summary