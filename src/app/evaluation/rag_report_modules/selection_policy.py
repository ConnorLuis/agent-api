from typing import Any

from src.app.evaluation.rag_report_modules.highlights import TINY_EVAL_CASE_THRESHOLD
from src.app.evaluation.rag_report_modules.ranking import (
    _get_best_relevance_backend,
    _get_eval_case_count,
    _get_pass_rate_winners,
)

def _should_change_default_backend(
    comparison: dict[str, Any],
    recommended_backend: str,
    default_backend: str,
    failure_analysis: dict[str, Any],
) -> bool:
    if not recommended_backend or recommended_backend == default_backend:
        return False

    eval_case_count = _get_eval_case_count(comparison)
    embedding_provider = comparison.get("embedding_provider")
    pass_rate_winners = _get_pass_rate_winners(comparison)
    common_failed_cases = failure_analysis.get("common_failed_cases", [])

    if eval_case_count < TINY_EVAL_CASE_THRESHOLD:
        return False

    if embedding_provider == "deterministic":
        return False

    if recommended_backend not in pass_rate_winners:
        return False

    if common_failed_cases:
        return False

    return True


def _build_selection_policy(
    comparison: dict[str, Any],
    recommended_backend: str,
    default_backend: str,
    default_backend_should_change: bool,
    failure_analysis: dict[str, Any],
) -> str:
    eval_case_count = _get_eval_case_count(comparison)
    embedding_provider = comparison.get("embedding_provider")
    common_failed_cases = failure_analysis.get("common_failed_cases", [])

    if recommended_backend == default_backend:
        return "keep_current_default"

    if eval_case_count < TINY_EVAL_CASE_THRESHOLD:
        return "keep_default_hybrid_until_larger_eval_set"

    if embedding_provider == "deterministic":
        return "keep_default_hybrid_until_semantic_eval"

    if common_failed_cases:
        return "keep_default_hybrid_until_failure_cases_are_reviewed"

    if default_backend_should_change:
        return "candidate_backend_ready_for_default_switch"

    return "keep_default_hybrid_until_policy_thresholds_met"


def _build_selection_policy_evaluation(
    comparison: dict[str, Any],
    recommended_backend: str,
    default_backend: str,
    default_backend_should_change: bool,
    failure_analysis: dict[str, Any],
) -> dict[str, Any]:
    eval_case_count = _get_eval_case_count(comparison)
    embedding_provider = comparison.get("embedding_provider")
    pass_rate_winners = _get_pass_rate_winners(comparison)
    best_relevance_backend = _get_best_relevance_backend(comparison)
    common_failed_cases = failure_analysis.get("common_failed_cases", [])

    supporting_reasons = []
    blocking_reasons = []

    if recommended_backend in pass_rate_winners:
        supporting_reasons.append(
            f"{recommended_backend} is in the top pass-rate group."
        )

    if recommended_backend == best_relevance_backend:
        supporting_reasons.append(
            f"{recommended_backend} has the best average relevance score."
        )

    if eval_case_count >= TINY_EVAL_CASE_THRESHOLD:
        supporting_reasons.append(
            f"The extended eval set has {eval_case_count} cases, so it is no "
            "longer treated as a tiny regression-only eval set."
        )
    else:
        blocking_reasons.append(
            f"The eval set has only {eval_case_count} cases, below the "
            f"{TINY_EVAL_CASE_THRESHOLD}-case threshold."
        )

    if embedding_provider == "deterministic":
        blocking_reasons.append(
            "The run uses deterministic embeddings; semantic embedding "
            "validation is required before switching the default backend."
        )

    if common_failed_cases:
        blocking_reasons.append(
            "Common failed cases must be reviewed before changing the default "
            f"backend: {', '.join(common_failed_cases)}."
        )

    if recommended_backend not in pass_rate_winners:
        blocking_reasons.append(
            f"{recommended_backend} is not in the top pass-rate group."
        )

    if not blocking_reasons and not default_backend_should_change:
        blocking_reasons.append(
            "Default backend switch is disabled by the conservative selection "
            "policy."
        )

    return {
        "policy_name": "pass_rate_first_relevance_tiebreak_conservative",
        "candidate_backend": recommended_backend,
        "default_backend": default_backend,
        "default_backend_should_change": default_backend_should_change,
        "pass_rate_winners": pass_rate_winners,
        "best_relevance_backend": best_relevance_backend,
        "supporting_reasons": supporting_reasons,
        "blocking_reasons": blocking_reasons,
        "policy_thresholds": {
            "min_eval_case_count": TINY_EVAL_CASE_THRESHOLD,
            "require_non_deterministic_embeddings": True,
            "require_candidate_in_top_pass_rate_group": True,
            "require_common_failed_cases_reviewed": True,
        },
    }