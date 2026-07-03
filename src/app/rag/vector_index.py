import math
import re
from typing import Any

from src.app.rag.chunking import DEFAULT_MAX_CHARS, load_knowledge_chunks


DEFAULT_EMBEDDING_DIM = 64


def _stable_bucket(term: str, embedding_dim: int) -> int:
    return sum(ord(char) for char in term) % embedding_dim


def _extract_terms(text: str) -> list[str]:
    normalized = text.strip().lower()

    return re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", normalized)


def build_deterministic_embedding(text: str, embedding_dim: int = DEFAULT_EMBEDDING_DIM) -> list[float]:
    safe_dim = max(embedding_dim, 8)
    vector = [0.0 for _ in range(safe_dim)]

    terms = _extract_terms(text)

    if not terms:
        return vector

    for term in terms:
        bucket = _stable_bucket(term, safe_dim)
        vector[bucket] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b):
        return 0.0

    return sum(a * b for a, b in zip(vector_a, vector_b))


def _get_matched_terms(query: str, content: str) -> list[str]:
    query_terms = set(_extract_terms(query))
    content_terms = set(_extract_terms(content))

    return sorted(query_terms.intersection(content_terms))


def vector_search_knowledge(query: str, top_k: int = 3, source_filter: str | None = None, max_chars: int = DEFAULT_MAX_CHARS, embedding_dim: int = DEFAULT_EMBEDDING_DIM,) -> list[dict[str, Any]]:
    safe_top_k = max(top_k, 1)
    safe_dim = max(embedding_dim, 8)

    query_embedding = build_deterministic_embedding(text=query, embedding_dim=safe_dim,)

    chunks = load_knowledge_chunks(source_filter=source_filter, max_chars=max_chars)

    scored_chunks = []

    for chunk in chunks:
        chunk_embedding = build_deterministic_embedding(text=chunk["content"], embedding_dim=safe_dim,)
        score = cosine_similarity(query_embedding, chunk_embedding)

        scored_chunks.append({**chunk, "score": round(score, 6), "matched_terms": _get_matched_terms(query, chunk["content"]),})

    scored_chunks.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_terms"]),
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
                "score": item["score"],
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
        "total_chunks": len(chunks),
        "results": results,
    }
