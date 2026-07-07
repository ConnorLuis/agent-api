from typing import Any


def _normalize_graph_fusion_results(
    fusion_results: list[dict],
) -> list[dict]:
    normalized_results = []

    for index, item in enumerate(fusion_results, start=1):
        fusion_score = float(item.get("fusion_score", 0.0))
        graph_score = float(item.get("graph_score", 0.0))
        vector_score = float(item.get("vector_score", 0.0))

        vector_metadata = item.get("vector_metadata", {}) or {}
        graph_metadata = item.get("graph_metadata", {}) or {}

        normalized_results.append(
            {
                "rank": item.get("rank", index),
                "chunk_id": item.get("chunk_id"),
                "source": item.get("source"),
                "index": item.get("index"),
                "content": item.get("content", ""),
                "preview": item.get("preview", ""),
                "content_length": item.get("content_length", 0),

                # Keep compatibility with existing Agentic RAG scoring code.
                "hybrid_score": fusion_score,
                "keyword_score": graph_score,
                "vector_score": vector_score,
                "score": fusion_score,

                # Graph fusion specific metadata.
                "fusion_score": fusion_score,
                "graph_score": graph_score,
                "vector_score": vector_score,
                "retrieval_sources": item.get("retrieval_sources", []),
                "matched_entities": item.get("matched_entities", []),
                "mentions": item.get("mentions", []),
                "graph_metadata": graph_metadata,
                "vector_metadata": vector_metadata,

                # Existing answer/citation logic can still use matched_terms.
                "matched_terms": vector_metadata.get("matched_terms", []),
            }
        )

    return normalized_results


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