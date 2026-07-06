from typing import Any


DEFAULT_PRODUCTION_BACKEND = "hybrid"
TINY_EVAL_CASE_THRESHOLD = 10

METRIC_KEYS = [
    "pass_rate",
    "retrieval_decision_accuracy",
    "expected_terms_hit_rate",
    "citation_hit_rate",
    "average_relevance_score",
]


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


def _build_failure_analysis(comparison: dict[str, Any]) -> dict[str, Any]:
    results = comparison.get("results", [])

    failed_cases_by_backend: dict[str, list[str]] = {}
    passed_cases_by_backend: dict[str, list[str]] = {}
    case_backend_status: dict[str, dict[str, bool]] = {}

    for result in results:
        backend = result.get("retrieval_backend")

        if not backend:
            continue

        failed_cases_by_backend.setdefault(backend, [])
        passed_cases_by_backend.setdefault(backend, [])

        for case in result.get("cases", []):
            case_id = case.get("case_id")

            if not case_id:
                continue

            passed = bool(case.get("passed", False))

            case_backend_status.setdefault(case_id, {})
            case_backend_status[case_id][backend] = passed

            if passed:
                passed_cases_by_backend[backend].append(case_id)
            else:
                failed_cases_by_backend[backend].append(case_id)

    evaluated_backends = list(failed_cases_by_backend.keys())

    common_failed_cases = []
    disagreement_cases = []
    unique_failed_cases_by_backend = {
        backend: []
        for backend in evaluated_backends
    }

    for case_id, backend_status in case_backend_status.items():
        failed_backends = [
            backend
            for backend in evaluated_backends
            if backend_status.get(backend) is False
        ]
        passed_backends = [
            backend
            for backend in evaluated_backends
            if backend_status.get(backend) is True
        ]

        if failed_backends and not passed_backends:
            common_failed_cases.append(case_id)

        if failed_backends and passed_backends:
            disagreement_cases.append(
                {
                    "case_id": case_id,
                    "failed_backends": failed_backends,
                    "passed_backends": passed_backends,
                }
            )

        if len(failed_backends) == 1:
            unique_failed_cases_by_backend[failed_backends[0]].append(case_id)

    failure_count_by_backend = {
        backend: len(failed_cases)
        for backend, failed_cases in failed_cases_by_backend.items()
    }

    if common_failed_cases:
        interpretation = (
            "Some cases fail across all evaluated backends. These failures "
            "are likely caused by eval-case design, chunking, query rewriting, "
            "or answer construction rather than a single retrieval backend."
        )
    elif disagreement_cases:
        interpretation = (
            "Some cases have backend-specific pass/fail differences. These "
            "cases are useful for backend selection analysis."
        )
    else:
        interpretation = (
            "No failed cases were observed in the current backend comparison."
        )

    return {
        "total_case_count": len(case_backend_status),
        "evaluated_backends": evaluated_backends,
        "failed_cases_by_backend": failed_cases_by_backend,
        "passed_cases_by_backend": passed_cases_by_backend,
        "failure_count_by_backend": failure_count_by_backend,
        "common_failed_cases": common_failed_cases,
        "disagreement_cases": disagreement_cases,
        "unique_failed_cases_by_backend": unique_failed_cases_by_backend,
        "interpretation": interpretation,
    }


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
