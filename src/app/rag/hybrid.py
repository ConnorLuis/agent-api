import re
from typing import Any

from src.app.rag.chunking import DEFAULT_MAX_CHARS, load_knowledge_chunks
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM, build_deterministic_embedding, cosine_similarity


def _extract_terms(text: str) -> list[str]:
    normalized = text.strip().lower()

    return re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+", normalized)


def _get_matched_terms(query: str, content: str) -> list[str]:
    query_terms = set(_extract_terms(query))
    content_terms = set(_extract_terms(content))

    return sorted(query_terms.intersection(content_terms))


def _keyword_score(query: str, content: str, matched_terms: list[str]) -> float:
    query_terms = set(_extract_terms(query))

    if not query_terms:
        return 0.0

    return round(len(matched_terms) / len(query_terms), 6)


def _normalize_weights(keyword_weight: float, vector_weight: float) -> tuple[float, float]:
    safe_keyword_weight = max(keyword_weight, 0.0)
    safe_vector_weight = max(vector_weight, 0.0)

    total = safe_keyword_weight + safe_vector_weight

    if total == 0:
        return 0.5, 0.5

    return (
        round(safe_keyword_weight / total, 6)
        , round(safe_vector_weight / total, 6)
    )


def hybrid_search_knowledge(query: str, top_k: int = 3, source_filter: str | None = None, max_chars: int = DEFAULT_MAX_CHARS, embedding_dim: int = DEFAULT_EMBEDDING_DIM, keyword_weight: float = 0.5, vector_weight: float = 0.5) ->dict[str, Any]:
    safe_top_k = max(top_k, 1)
    safe_dim = max(embedding_dim, 8)

    normalized_keyword_weight, normalized_vector_weight = _normalize_weights(keyword_weight=keyword_weight, vector_weight=vector_weight)

    query_embedding = build_deterministic_embedding(text=query, embedding_dim=safe_dim,)

    chunks = load_knowledge_chunks(source_filter=source_filter, max_chars=max_chars)

    scored_chunks = []

    for chunk in chunks:
        content = chunk["content"]
        matched_terms = _get_matched_terms(query, content)

        keyword_score = _keyword_score(query=query, content=content, matched_terms=matched_terms)

        chunk_embedding = build_deterministic_embedding(text=content, embedding_dim=safe_dim,)

        vector_score = round(cosine_similarity(query_embedding, chunk_embedding), 6)

        hybrid_score = round(normalized_keyword_weight * keyword_score + normalized_vector_weight * vector_score, 6)

        scored_chunks.append({**chunk, "hybrid_score": hybrid_score, "keyword_score": keyword_score, "vector_score": vector_score, "matched_terms": matched_terms,})

    scored_chunks.sort(
        key=lambda item: (
            item["hybrid_score"],
            item["keyword_score"],
            item["vector_score"],
            -item["index"],
        ),
        reverse=True,
    )

    results = []

    for rank, item in enumerate(scored_chunks[:safe_top_k], start=1):
        results.append(
            {
                "rank": rank,
                "chunk_id": item["chunk_id"],
                "source": item["source"],
                "index": item["index"],
                "hybrid_score": item["hybrid_score"],
                "keyword_score": item["keyword_score"],
                "vector_score": item["vector_score"],
                "content": item["content"],
                "preview": item["preview"],
                "matched_terms": item["matched_terms"],
                "content_length": item["content_length"],
            }
        )

    return {
        "query": query,
        "top_k": safe_top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": safe_dim,
        "keyword_weight": normalized_keyword_weight,
        "vector_weight": normalized_vector_weight,
        "total_chunks": len(chunks),
        "results": results,
    }

