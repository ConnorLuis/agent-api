from typing import Any

from src.app.evaluation.rag_report_modules.failure_analysis import (
    _build_failure_analysis,
)
from src.app.evaluation.rag_report_modules.highlights import (
    _build_metric_highlights,
    _build_recommendation_reason,
    _build_risk_notes,
)
from src.app.evaluation.rag_report_modules.ranking import (
    _build_backend_rank_summary,
    _choose_recommended_backend, _get_eval_case_count,
)
from src.app.evaluation.rag_report_modules.selection_policy import (
    _build_selection_policy,
    _build_selection_policy_evaluation, _should_change_default_backend,
)

DEFAULT_PRODUCTION_BACKEND = "hybrid"


def build_backend_evaluation_report(comparison: dict[str, Any]) -> dict[str, Any]:
    recommended_backend = _choose_recommended_backend(comparison)
    default_backend = DEFAULT_PRODUCTION_BACKEND
    failure_analysis = _build_failure_analysis(comparison)

    default_backend_should_change = _should_change_default_backend(
        comparison=comparison,
        recommended_backend=recommended_backend,
        default_backend=default_backend,
        failure_analysis=failure_analysis,
    )

    selection_policy = _build_selection_policy(
        comparison=comparison,
        recommended_backend=recommended_backend,
        default_backend=default_backend,
        default_backend_should_change=default_backend_should_change,
        failure_analysis=failure_analysis,
    )

    recommendation_reason = _build_recommendation_reason(
        comparison=comparison,
        recommended_backend=recommended_backend,
        default_backend=default_backend,
        default_backend_should_change=default_backend_should_change,
        failure_analysis=failure_analysis,
    )

    selection_policy_evaluation = _build_selection_policy_evaluation(
        comparison=comparison,
        recommended_backend=recommended_backend,
        default_backend=default_backend,
        default_backend_should_change=default_backend_should_change,
        failure_analysis=failure_analysis,
    )

    return {
        "recommended_backend": recommended_backend,
        "recommendation_reason": recommendation_reason,
        "default_backend": default_backend,
        "default_backend_should_change": default_backend_should_change,
        "selection_policy": selection_policy,
        "selection_policy_evaluation": selection_policy_evaluation,
        "embedding_provider": comparison.get("embedding_provider"),
        "embedding_model": comparison.get("embedding_model"),
        "eval_file": str(comparison.get("eval_file")),
        "eval_case_count": _get_eval_case_count(comparison),
        "metric_highlights": _build_metric_highlights(comparison),
        "risk_notes": _build_risk_notes(
            comparison=comparison,
            recommended_backend=recommended_backend,
            default_backend=default_backend,
            default_backend_should_change=default_backend_should_change,
            failure_analysis=failure_analysis,
        ),
        "failure_analysis": failure_analysis,
        "backend_rank_summary": _build_backend_rank_summary(
            comparison=comparison,
            recommended_backend=recommended_backend,
        ),
        "interpretation": (
            "This report converts backend evaluation metrics into an engineering "
            "selection summary. It should be used to guide backend experiments, "
            "not as a production benchmark by itself."
        ),
    }