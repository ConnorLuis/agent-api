from pathlib import Path
from typing import Any

from src.app.rag.chroma_store import (
    DEFAULT_CHROMA_PERSIST_DIR,
    debug_chroma_search,
)
from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM

DEFAULT_RETRIEVAL_BACKEND = "hybrid"

SUPPORTED_RETRIEVAL_BACKENDS = {
    "hybrid",
    "chroma",
}


def normalize_retrieval_backend(
    retrieval_backend: str | None,
) -> str:
    normalized = (retrieval_backend or DEFAULT_RETRIEVAL_BACKEND).strip().lower()

    if normalized in {"default", "deterministic", "hybrid"}:
        return "hybrid"

    if normalized in {"chroma", "chromadb", "vector_db", "vector-db"}:
        return "chroma"

    raise ValueError(
        f"Unsupported retrieval backend: {retrieval_backend}"
    )


def _normalize_hybrid_results(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_results: list[dict[str, Any]] = []

    for item in results:
        score = float(item.get("hybrid_score", item.get("score", 0.0)))

        normalized_results.append(
            {
                "rank": int(item["rank"]),
                "chunk_id": str(item["chunk_id"]),
                "source": str(item["source"]),
                "index": int(item["index"]),
                "score": round(score, 6),
                "content": str(item["content"]),
                "preview": str(item["preview"]),
                "content_length": int(item["content_length"]),
                "matched_terms": list(item.get("matched_terms", [])),
                "retrieval_backend": "hybrid",
                "hybrid_score": float(item.get("hybrid_score", score)),
                "keyword_score": float(item.get("keyword_score", 0.0)),
                "vector_score": float(item.get("vector_score", 0.0)),
            }
        )

    return normalized_results


def _normalize_chroma_results(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_results: list[dict[str, Any]] = []

    for item in results:
        score = float(item.get("score", 0.0))
        distance = float(item.get("distance", 0.0))

        normalized_results.append(
            {
                "rank": int(item["rank"]),
                "chunk_id": str(item["chunk_id"]),
                "source": str(item["source"]),
                "index": int(item["index"]),
                "score": score,
                "content": str(item["content"]),
                "preview": str(item["preview"]),
                "content_length": int(item["content_length"]),
                "matched_terms": [],
                "retrieval_backend": "chroma",

                # Chroma-specific metadata
                "distance": distance,

                # Compatibility fields for RagAgenticDebugResponse.
                # Agentic RAG originally expected hybrid retrieval result shape.
                "hybrid_score": score,
                "keyword_score": 0.0,
                "vector_score": score,
            }
        )

    return normalized_results


def retrieve_agentic_context(
    query: str,
    top_k: int = 3,
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = DEFAULT_RETRIEVAL_BACKEND,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    rebuild_index: bool = True,
    chroma_persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> dict[str, Any]:
    backend = normalize_retrieval_backend(retrieval_backend)

    if backend == "hybrid":
        result = hybrid_search_knowledge(
            query=query,
            top_k=top_k,
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            keyword_weight=keyword_weight,
            vector_weight=vector_weight,
        )

        return {
            "retrieval_backend": "hybrid",
            "query": query,
            "results": _normalize_hybrid_results(result["results"]),
            "metadata": {
                "retrieval_backend": "hybrid",
                "total_chunks": result["total_chunks"],
                "keyword_weight": keyword_weight,
                "vector_weight": vector_weight,
                "embedding_dim": embedding_dim,
            },
        }

    if backend == "chroma":
        result = debug_chroma_search(
            query=query,
            top_k=top_k,
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            rebuild_index=rebuild_index,
            persist_dir=chroma_persist_dir,
        )

        return {
            "retrieval_backend": "chroma",
            "query": query,
            "results": _normalize_chroma_results(result["results"]),
            "metadata": {
                "retrieval_backend": "chroma",
                "collection_name": result["collection_name"],
                "persist_dir": result["persist_dir"],
                "total_indexed_chunks": result["total_indexed_chunks"],
                "embedding_provider": result["embedding_provider"],
                "embedding_model": result["embedding_model"],
                "embedding_dim": result["embedding_dim"],
                "rebuild_index": result["rebuild_index"],
                "index_stats": result["index_stats"],
            },
        }

    raise ValueError(
        f"Unsupported retrieval backend: {retrieval_backend}"
    )