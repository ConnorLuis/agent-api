from typing import Any


MIN_SEMANTIC_EVAL_CASE_COUNT = 10


def _get_metrics_by_backend(comparison: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metrics_by_backend: dict[str, dict[str, Any]] = {}

    for item in comparison.get("results", []):
        backend = item.get("retrieval_backend")
        if backend:
            metrics_by_backend[backend] = item.get("metrics", {})

    return metrics_by_backend


def _get_failed_case_details(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    failed_case_details = []

    for case in comparison.get("case_comparisons", []):
        backend_results = case.get("backend_results", [])
        failed_results = [
            result
            for result in backend_results
            if result.get("passed") is False
        ]

        if not failed_results:
            continue

        failed_case_details.append(
            {
                "case_id": case.get("case_id"),
                "winner_by_pass": case.get("winner_by_pass"),
                "winner_by_relevance": case.get("winner_by_relevance"),
                "failed_backends": [
                    result.get("retrieval_backend")
                    for result in failed_results
                ],
                "backend_results": [
                    {
                        "retrieval_backend": result.get("retrieval_backend"),
                        "passed": result.get("passed"),
                        "expected_terms_pass": result.get(
                            "expected_terms_pass",
                        ),
                        "matched_expected_terms": result.get(
                            "matched_expected_terms",
                            [],
                        ),
                        "citation_pass": result.get("citation_pass"),
                        "retrieval_decision_pass": result.get(
                            "retrieval_decision_pass",
                        ),
                        "relevance_score": result.get("relevance_score"),
                        "citations": result.get("citations", []),
                        "steps": result.get("steps", []),
                    }
                    for result in backend_results
                ],
            }
        )

    return failed_case_details


def build_semantic_backend_review(comparison: dict[str, Any]) -> dict[str, Any]:
    report = comparison.get("evaluation_report", {})
    policy = report.get("selection_policy_evaluation", {})
    failure_analysis = report.get("failure_analysis", {})

    candidate_backend = report.get("recommended_backend")
    default_backend = report.get("default_backend")
    embedding_provider = report.get("embedding_provider")
    eval_case_count = report.get("eval_case_count", 0)

    pass_rate_winners = policy.get("pass_rate_winners", [])
    best_relevance_backend = policy.get("best_relevance_backend")
    common_failed_cases = failure_analysis.get("common_failed_cases", [])
    blocking_reasons = policy.get("blocking_reasons", [])

    semantic_eval_used = embedding_provider not in {None, "deterministic"}

    candidate_in_top_pass_rate_group = candidate_backend in pass_rate_winners
    candidate_best_by_relevance = candidate_backend == best_relevance_backend

    semantic_candidate_validated = (
        semantic_eval_used
        and eval_case_count >= MIN_SEMANTIC_EVAL_CASE_COUNT
        and candidate_in_top_pass_rate_group
        and candidate_best_by_relevance
    )

    if not semantic_candidate_validated:
        review_decision = "keep_default_backend"
    elif common_failed_cases:
        review_decision = "review_common_failure_cases_before_default_switch"
    else:
        review_decision = "candidate_ready_for_default_switch_review"

    return {
        "review_decision": review_decision,
        "semantic_candidate_validated": semantic_candidate_validated,
        "candidate_backend": candidate_backend,
        "default_backend": default_backend,
        "default_backend_should_change": report.get(
            "default_backend_should_change",
            False,
        ),
        "selection_policy": report.get("selection_policy"),
        "embedding_provider": embedding_provider,
        "embedding_model": report.get("embedding_model"),
        "eval_file": report.get("eval_file"),
        "eval_case_count": eval_case_count,
        "pass_rate_winners": pass_rate_winners,
        "best_relevance_backend": best_relevance_backend,
        "candidate_in_top_pass_rate_group": candidate_in_top_pass_rate_group,
        "candidate_best_by_relevance": candidate_best_by_relevance,
        "common_failed_cases": common_failed_cases,
        "failure_count_by_backend": failure_analysis.get(
            "failure_count_by_backend",
            {},
        ),
        "unique_failed_cases_by_backend": failure_analysis.get(
            "unique_failed_cases_by_backend",
            {},
        ),
        "blocking_reasons": blocking_reasons,
        "supporting_reasons": policy.get("supporting_reasons", []),
        "metrics_by_backend": _get_metrics_by_backend(comparison),
        "failed_case_details": _get_failed_case_details(comparison),
        "interpretation": (
            "Semantic evaluation validates the candidate backend only when "
            "the run uses a non-deterministic embedding provider, the eval set "
            "has enough cases, the candidate is in the top pass-rate group, "
            "and the candidate has the best average relevance score. Common "
            "failed cases still require manual review before a default backend "
            "switch is considered."
        ),
    }


def render_semantic_backend_review_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Day41 Semantic Backend Review",
        "",
        "## Summary",
        "",
        f"- Review decision: `{review['review_decision']}`",
        f"- Semantic candidate validated: `{review['semantic_candidate_validated']}`",
        f"- Candidate backend: `{review['candidate_backend']}`",
        f"- Default backend: `{review['default_backend']}`",
        f"- Default backend should change: `{review['default_backend_should_change']}`",
        f"- Selection policy: `{review['selection_policy']}`",
        f"- Embedding provider: `{review['embedding_provider']}`",
        f"- Eval file: `{review['eval_file']}`",
        f"- Eval case count: `{review['eval_case_count']}`",
        "",
        "## Backend Metrics",
        "",
    ]

    for backend, metrics in review["metrics_by_backend"].items():
        lines.extend(
            [
                f"### {backend}",
                "",
                f"- Passed cases: `{metrics.get('passed_cases')}/{metrics.get('total_cases')}`",
                f"- Pass rate: `{metrics.get('pass_rate')}`",
                f"- Expected terms hit rate: `{metrics.get('expected_terms_hit_rate')}`",
                f"- Citation hit rate: `{metrics.get('citation_hit_rate')}`",
                f"- Average relevance score: `{metrics.get('average_relevance_score')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Failure Analysis",
            "",
            f"- Common failed cases: `{review['common_failed_cases']}`",
            f"- Failure count by backend: `{review['failure_count_by_backend']}`",
            f"- Unique failed cases by backend: `{review['unique_failed_cases_by_backend']}`",
            "",
            "## Supporting Reasons",
            "",
        ]
    )

    for reason in review["supporting_reasons"]:
        lines.append(f"- {reason}")

    lines.extend(["", "## Blocking Reasons", ""])

    for reason in review["blocking_reasons"]:
        lines.append(f"- {reason}")

    lines.extend(["", "## Failed Case Details", ""])

    for case in review["failed_case_details"]:
        lines.extend(
            [
                f"### {case['case_id']}",
                "",
                f"- Winner by pass: `{case['winner_by_pass']}`",
                f"- Winner by relevance: `{case['winner_by_relevance']}`",
                f"- Failed backends: `{case['failed_backends']}`",
                "",
            ]
        )

        for result in case["backend_results"]:
            lines.extend(
                [
                    f"#### {result['retrieval_backend']}",
                    "",
                    f"- Passed: `{result['passed']}`",
                    f"- Expected terms pass: `{result['expected_terms_pass']}`",
                    f"- Matched expected terms: `{result['matched_expected_terms']}`",
                    f"- Citation pass: `{result['citation_pass']}`",
                    f"- Retrieval decision pass: `{result['retrieval_decision_pass']}`",
                    f"- Relevance score: `{result['relevance_score']}`",
                    f"- Citations: `{result['citations']}`",
                    f"- Steps: `{result['steps']}`",
                    "",
                ]
            )

    lines.extend(["## Interpretation", "", review["interpretation"], ""])

    return "\n".join(lines)
