import re
from typing import Any

DEFAULT_ORIGINAL_SCORE_WEIGHT = 0.7
DEFAULT_KEYWORD_SCORE_WEIGHT = 0.3

_RERANK_STOP_TERMS = {
    "请",
    "搜",
    "索",
    "知",
    "识",
    "库",
    "是",
    "什",
    "么",
    "的",
    "了",
    "吗",
    "呢",
}


def extract_rerank_terms(
    query: str,
) -> list[str]:
    normalized_query = query.lower()

    raw_terms = re.findall(
        r"[a-z0-9][a-z0-9_\-\.]*|[\u4e00-\u9fff]",
        normalized_query,
    )

    terms: list[str] = []

    for term in raw_terms:
        if term in _RERANK_STOP_TERMS:
            continue

        if term not in terms:
            terms.append(term)

    return terms


def calculate_keyword_rerank_score(
    query_terms: list[str],
    content: str,
) -> tuple[float, list[str]]:
    if not query_terms:
        return 0.0, []

    normalized_content = content.lower()

    matched_terms = [
        term
        for term in query_terms
        if term in normalized_content
    ]

    score = round(
        len(matched_terms) / len(query_terms),
        6,
    )

    return score, matched_terms


def rerank_retrieval_results(
    query: str,
    results: list[dict[str, Any]],
    original_score_weight: float = DEFAULT_ORIGINAL_SCORE_WEIGHT,
    keyword_score_weight: float = DEFAULT_KEYWORD_SCORE_WEIGHT,
) -> list[dict[str, Any]]:
    query_terms = extract_rerank_terms(query)

    reranked_results: list[dict[str, Any]] = []

    for result in results:
        original_score = float(
            result.get(
                "score",
                result.get("hybrid_score", result.get("vector_score", 0.0)),
            )
        )

        keyword_score, matched_terms = calculate_keyword_rerank_score(
            query_terms=query_terms,
            content=str(result.get("content", "")),
        )

        rerank_score = round(
            original_score_weight * original_score
            + keyword_score_weight * keyword_score,
            6,
        )

        reranked_item = {
            **result,
            "original_rank": int(result["rank"]),
            "original_score": original_score,
            "rerank_score": rerank_score,
            "rerank_keyword_score": keyword_score,
            "rerank_matched_terms": matched_terms,
            "score": rerank_score,
            "hybrid_score": rerank_score,
            "keyword_score": keyword_score,
            "vector_score": original_score,
        }

        reranked_results.append(reranked_item)

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    for index, item in enumerate(reranked_results, start=1):
        item["rank"] = index

    return reranked_results