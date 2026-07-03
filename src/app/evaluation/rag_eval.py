import json
from pathlib import Path
from typing import Any

from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM


DEFAULT_RAG_EVAL_FILE = Path("eval_cases/rag_agentic_eval.jsonl")


def load_rag_eval_cases(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
) -> list[dict[str, Any]]:
    path = Path(eval_file)

    if not path.exists():
        return []

    cases = []

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        item = json.loads(stripped)

        cases.append(
            {
                "case_id": str(item["case_id"]),
                "query": str(item["query"]),
                "expected_retrieval_needed": bool(item["expected_retrieval_needed"]),
                "expected_terms": list(item.get("expected_terms", [])),
                "expected_citation_keywords": list(
                    item.get("expected_citation_keywords", [])
                ),
                "line_number": line_number,
            }
        )

    return cases


def _contains_term(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def _calculate_rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0

    return round(count / total, 6)


def _evaluate_single_case(
    case: dict[str, Any],
    source_filter: str | None,
    max_chars: int,
    embedding_dim: int,
    keyword_weight: float,
    vector_weight: float,
) -> dict[str, Any]:
    result = invoke_agentic_rag(
        query=case["query"],
        top_k=2,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
    )

    final_answer = result["final_answer"]
    citations = result["citations"]

    expected_terms = case["expected_terms"]
    matched_expected_terms = [
        term for term in expected_terms if _contains_term(final_answer, term)
    ]

    expected_terms_pass = len(matched_expected_terms) == len(expected_terms)

    expected_citation_keywords = case["expected_citation_keywords"]
    citations_blob = " ".join(citations)

    citation_pass = all(
        _contains_term(citations_blob, keyword)
        for keyword in expected_citation_keywords
    )

    retrieval_decision_pass = (
        result["retrieval_needed"] == case["expected_retrieval_needed"]
    )

    passed = retrieval_decision_pass and expected_terms_pass and citation_pass

    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "expected_retrieval_needed": case["expected_retrieval_needed"],
        "actual_retrieval_needed": result["retrieval_needed"],
        "retrieval_decision_pass": retrieval_decision_pass,
        "expected_terms": expected_terms,
        "matched_expected_terms": matched_expected_terms,
        "expected_terms_pass": expected_terms_pass,
        "expected_citation_keywords": expected_citation_keywords,
        "citations": citations,
        "citation_pass": citation_pass,
        "relevance_score": result["relevance_score"],
        "steps": result["steps"],
        "final_answer_preview": final_answer[:180],
        "passed": passed,
    }


def evaluate_rag_cases(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
    source_filter: str | None = "agent_basics",
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
) -> dict[str, Any]:
    cases = load_rag_eval_cases(eval_file=eval_file)

    case_results = [
        _evaluate_single_case(
            case=case,
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            keyword_weight=keyword_weight,
            vector_weight=vector_weight,
        )
        for case in cases
    ]

    total_cases = len(case_results)
    passed_cases = sum(1 for item in case_results if item["passed"])
    retrieval_passed = sum(
        1 for item in case_results if item["retrieval_decision_pass"]
    )
    expected_terms_passed = sum(
        1 for item in case_results if item["expected_terms_pass"]
    )
    citation_passed = sum(1 for item in case_results if item["citation_pass"])

    if total_cases == 0:
        average_relevance_score = 0.0
    else:
        average_relevance_score = round(
            sum(float(item["relevance_score"]) for item in case_results)
            / total_cases,
            6,
        )

    return {
        "eval_file": str(eval_file),
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "metrics": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "pass_rate": _calculate_rate(passed_cases, total_cases),
            "retrieval_decision_accuracy": _calculate_rate(
                retrieval_passed,
                total_cases,
            ),
            "expected_terms_hit_rate": _calculate_rate(
                expected_terms_passed,
                total_cases,
            ),
            "citation_hit_rate": _calculate_rate(
                citation_passed,
                total_cases,
            ),
            "average_relevance_score": average_relevance_score,
        },
        "cases": case_results,
    }
