import re
from typing import Any

from src.app.rag.retriever import search_knowledge


def _normalize_query(query: str) -> str:
    return query.strip().lower()


def _extract_query_terms(query: str) -> list[str]:
    normalized = _normalize_query(query)

    terms = re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+", normalized)

    return [term for term in terms if term]


def _get_value(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


def _get_matched_terms(query_terms: list[str], content: str) -> list[str]:
    lowered_content = content.lower()

    matched_terms = []

    for term in query_terms:
        if term and term in lowered_content:
            matched_terms.append(term)

    return matched_terms


def explain_search_knowledge(query: str, k: int = 3) -> dict:
    normalized_query = _normalize_query(query)
    query_terms = _extract_query_terms(query)

    raw_results = search_knowledge(query=query, k=k)

    explained_results = []

    for index, item in enumerate(raw_results, start=1):
        source = str(_get_value(item, "source", ""))
        content = str(_get_value(item, "content", ""))
        score = int(_get_value(item, "score", 0))

        explained_results.append(
            {
                "rank": index,
                "source": source,
                "score": score,
                "content": content,
                "preview": content[:160],
                "matched_terms": _get_matched_terms(query_terms, content),
                "content_length": len(content),
            }
        )

    return {
        "query": query,
        "normalized_query": normalized_query,
        "k": k,
        "results": explained_results,
    }