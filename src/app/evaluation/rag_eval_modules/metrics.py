from typing import Any


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


def _calculate_metric_delta(
    baseline: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
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