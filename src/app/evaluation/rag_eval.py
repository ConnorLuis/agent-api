from src.app.evaluation.rag_eval_modules.backend_comparison import (
    _COMPARISON_SUMMARY_METRICS,
    _build_case_comparisons,
    _build_comparison_summary,
    _build_metric_deltas,
    _build_metric_rankings,
    _build_metric_winners,
    _build_multi_backend_summary_notes,
    _build_pairwise_metric_deltas,
    _build_top_improvement_pairs,
    _format_backend_list,
    compare_rag_retrieval_backends,
)
from src.app.evaluation.rag_eval_modules.cases import (
    DEFAULT_RAG_EVAL_FILE,
    _normalize_expected_terms,
    load_rag_eval_cases,
)
from src.app.evaluation.rag_eval_modules.metrics import (
    _calculate_metric_delta,
    _citation_hit,
    _expected_terms_hit,
    _retrieval_decision_hit,
    _safe_average,
)
from src.app.evaluation.rag_eval_modules.single_backend import (
    evaluate_rag_cases,
)


__all__ = [
    "DEFAULT_RAG_EVAL_FILE",
    "load_rag_eval_cases",
    "evaluate_rag_cases",
    "compare_rag_retrieval_backends",
    "_normalize_expected_terms",
    "_expected_terms_hit",
    "_citation_hit",
    "_retrieval_decision_hit",
    "_safe_average",
    "_calculate_metric_delta",
    "_build_metric_deltas",
    "_build_pairwise_metric_deltas",
    "_build_case_comparisons",
    "_COMPARISON_SUMMARY_METRICS",
    "_build_metric_rankings",
    "_build_metric_winners",
    "_build_top_improvement_pairs",
    "_format_backend_list",
    "_build_multi_backend_summary_notes",
    "_build_comparison_summary",
]