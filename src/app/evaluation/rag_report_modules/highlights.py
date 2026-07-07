from typing import Any

from src.app.evaluation.rag_report_modules.ranking import _get_eval_case_count

TINY_EVAL_CASE_THRESHOLD = 10


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
    top_pair = None

    if isinstance(top_improvement_pairs, list) and top_improvement_pairs:
        top_pair = top_improvement_pairs[0]
    elif isinstance(top_improvement_pairs, dict):
        relevance_pairs = top_improvement_pairs.get(
            "average_relevance_score",
            [],
        )
        if relevance_pairs:
            top_pair = relevance_pairs[0]
        else:
            for pairs in top_improvement_pairs.values():
                if isinstance(pairs, list) and pairs:
                    top_pair = pairs[0]
                    break

    if isinstance(top_pair, dict):
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


def _build_recommendation_reason(
    comparison: dict[str, Any],
    recommended_backend: str,
    default_backend: str,
    default_backend_should_change: bool,
    failure_analysis: dict[str, Any],
) -> str:
    eval_case_count = _get_eval_case_count(comparison)
    embedding_provider = comparison.get("embedding_provider")
    common_failed_cases = failure_analysis.get("common_failed_cases", [])

    if not recommended_backend:
        return "No recommended backend could be selected from the current comparison."

    if recommended_backend == default_backend:
        return (
            f"{recommended_backend} remains the recommended backend because it "
            "is already the default and remains competitive on the current "
            "evaluation result."
        )

    if default_backend_should_change:
        return (
            f"{recommended_backend} is ready to replace {default_backend} under "
            "the current backend selection policy."
        )

    if eval_case_count < TINY_EVAL_CASE_THRESHOLD:
        return (
            f"{recommended_backend} is the current experiment candidate, but "
            f"the default backend should remain {default_backend} until larger "
            "and more representative evaluation data is available."
        )

    if embedding_provider == "deterministic":
        return (
            f"{recommended_backend} is the current experiment candidate, but "
            f"the default backend should remain {default_backend} until semantic "
            "embedding evaluation validates the change."
        )

    if common_failed_cases:
        return (
            f"{recommended_backend} is the current experiment candidate, but "
            f"the default backend should remain {default_backend} until common "
            "failed cases are reviewed."
        )

    return (
        f"{recommended_backend} is the current experiment candidate, but "
        f"the default backend should remain {default_backend} until all "
        "selection policy thresholds are met."
    )


def _build_risk_notes(
    comparison: dict[str, Any],
    recommended_backend: str,
    default_backend: str,
    default_backend_should_change: bool,
    failure_analysis: dict[str, Any],
) -> list[str]:
    notes = []

    eval_case_count = _get_eval_case_count(comparison)
    embedding_provider = comparison.get("embedding_provider")
    common_failed_cases = failure_analysis.get("common_failed_cases", [])

    if eval_case_count < TINY_EVAL_CASE_THRESHOLD:
        notes.append(
            "The current eval set is small/tiny, so the report should be "
            "treated as a regression and debugging signal rather than a "
            "production-level benchmark."
        )

    if embedding_provider == "deterministic":
        notes.append(
            "The current run uses deterministic embeddings, which are CI-safe "
            "but do not represent real semantic embedding quality."
        )

    if common_failed_cases:
        notes.append(
            "The current evaluation still has common failed cases across all "
            "evaluated backends: "
            f"{', '.join(common_failed_cases)}."
        )

    if recommended_backend != default_backend and not default_backend_should_change:
        notes.append(
            f"{recommended_backend} is recommended as an experiment candidate, "
            f"but the default backend should remain {default_backend} until the "
            "selection policy blockers are resolved."
        )

    return notes