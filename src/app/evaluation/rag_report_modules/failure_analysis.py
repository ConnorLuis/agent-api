from typing import Any


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