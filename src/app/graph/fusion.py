from __future__ import annotations

from typing import Any

from src.app.graph.retrieval import run_graph_retrieval_debug
from src.app.rag.hybrid import hybrid_search_knowledge


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_vector_results(vector_payload: Any) -> list[dict[str, Any]]:
    if isinstance(vector_payload, dict):
        results = vector_payload.get("results", [])
        if isinstance(results, list):
            return results
        return []

    if isinstance(vector_payload, list):
        return vector_payload

    return []


def _normalize_graph_chunk(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": chunk.get("chunk_id"),
        "source": chunk.get("source"),
        "index": chunk.get("index"),
        "content": chunk.get("content"),
        "preview": chunk.get("preview"),
        "content_length": chunk.get("content_length"),
        "document": chunk.get("document"),
        "graph_score": 1.0,
        "vector_score": 0.0,
        "matched_entities": chunk.get("matched_entities", []),
        "mentions": chunk.get("mentions", []),
        "retrieval_sources": ["graph"],
        "graph_metadata": {
            "matched_entities": chunk.get("matched_entities", []),
            "mentions": chunk.get("mentions", []),
            "document": chunk.get("document"),
        },
        "vector_metadata": {},
    }


def _normalize_vector_result(result: dict[str, Any]) -> dict[str, Any]:
    vector_score = _safe_float(
        result.get("hybrid_score", result.get("score", result.get("vector_score", 0.0)))
    )

    return {
        "chunk_id": result.get("chunk_id"),
        "source": result.get("source"),
        "index": result.get("index"),
        "content": result.get("content"),
        "preview": result.get("preview"),
        "content_length": result.get("content_length"),
        "document": None,
        "graph_score": 0.0,
        "vector_score": vector_score,
        "matched_entities": [],
        "mentions": [],
        "retrieval_sources": ["vector"],
        "graph_metadata": {},
        "vector_metadata": {
            "rank": result.get("rank"),
            "hybrid_score": result.get("hybrid_score"),
            "keyword_score": result.get("keyword_score"),
            "vector_score": result.get("vector_score"),
            "score": result.get("score"),
            "matched_terms": result.get("matched_terms", []),
        },
    }


def _merge_result(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    retrieval_sources = sorted(
        set(existing.get("retrieval_sources", [])) | set(incoming.get("retrieval_sources", []))
    )

    merged = dict(existing)
    merged["retrieval_sources"] = retrieval_sources
    merged["graph_score"] = max(
        _safe_float(existing.get("graph_score")),
        _safe_float(incoming.get("graph_score")),
    )
    merged["vector_score"] = max(
        _safe_float(existing.get("vector_score")),
        _safe_float(incoming.get("vector_score")),
    )

    for key in ["content", "preview", "source", "index", "content_length", "document"]:
        if merged.get(key) in (None, "", []):
            merged[key] = incoming.get(key)

    if incoming.get("matched_entities"):
        merged["matched_entities"] = incoming["matched_entities"]
    if incoming.get("mentions"):
        merged["mentions"] = incoming["mentions"]

    if incoming.get("graph_metadata"):
        merged["graph_metadata"] = incoming["graph_metadata"]
    if incoming.get("vector_metadata"):
        merged["vector_metadata"] = incoming["vector_metadata"]

    return merged


def fuse_graph_and_vector_results(
    graph_chunks: list[dict[str, Any]],
    vector_results: list[dict[str, Any]],
    top_k: int = 5,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
) -> list[dict[str, Any]]:
    combined_by_chunk_id: dict[str, dict[str, Any]] = {}

    for chunk in graph_chunks:
        normalized = _normalize_graph_chunk(chunk)
        chunk_id = normalized.get("chunk_id")
        if not chunk_id:
            continue
        combined_by_chunk_id[chunk_id] = normalized

    for result in vector_results:
        normalized = _normalize_vector_result(result)
        chunk_id = normalized.get("chunk_id")
        if not chunk_id:
            continue

        if chunk_id in combined_by_chunk_id:
            combined_by_chunk_id[chunk_id] = _merge_result(
                existing=combined_by_chunk_id[chunk_id],
                incoming=normalized,
            )
        else:
            combined_by_chunk_id[chunk_id] = normalized

    fused_results = []

    for result in combined_by_chunk_id.values():
        graph_score = _safe_float(result.get("graph_score"))
        vector_score = _safe_float(result.get("vector_score"))

        fusion_score = (
            fusion_graph_weight * graph_score
            + fusion_vector_weight * vector_score
        )

        fused_result = dict(result)
        fused_result["fusion_score"] = round(fusion_score, 6)
        fused_result["graph_score"] = round(graph_score, 6)
        fused_result["vector_score"] = round(vector_score, 6)
        fused_results.append(fused_result)

    fused_results.sort(
        key=lambda item: (
            item["fusion_score"],
            item["graph_score"],
            item["vector_score"],
            -int(item.get("index") or 0),
        ),
        reverse=True,
    )

    ranked_results = []

    for rank, item in enumerate(fused_results[:top_k], start=1):
        ranked = dict(item)
        ranked["rank"] = rank
        ranked_results.append(ranked)

    return ranked_results


def run_graph_vector_fusion_debug(
    query: str,
    top_k: int = 5,
    source_filter: str | None = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    hybrid_keyword_weight: float = 0.6,
    hybrid_vector_weight: float = 0.4,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
    graph_dry_run: bool = True,
) -> dict[str, Any]:
    graph_retrieval = run_graph_retrieval_debug(
        query=query,
        chunk_limit=graph_chunk_limit,
        related_entity_limit=related_entity_limit,
        dry_run=graph_dry_run,
    )

    vector_payload = hybrid_search_knowledge(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=hybrid_keyword_weight,
        vector_weight=hybrid_vector_weight,
    )

    vector_results = _extract_vector_results(vector_payload)
    graph_execution = graph_retrieval.get("execution", {})
    graph_chunks = graph_execution.get("chunks", [])

    fused_results = fuse_graph_and_vector_results(
        graph_chunks=graph_chunks,
        vector_results=vector_results,
        top_k=top_k,
        fusion_graph_weight=fusion_graph_weight,
        fusion_vector_weight=fusion_vector_weight,
    )

    fusion_source_counts = {
        "graph_only": 0,
        "vector_only": 0,
        "graph_and_vector": 0,
    }

    for result in fused_results:
        sources = set(result.get("retrieval_sources", []))

        if sources == {"graph"}:
            fusion_source_counts["graph_only"] += 1
        elif sources == {"vector"}:
            fusion_source_counts["vector_only"] += 1
        elif sources == {"graph", "vector"}:
            fusion_source_counts["graph_and_vector"] += 1

    return {
        "query": query,
        "top_k": top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "hybrid_keyword_weight": hybrid_keyword_weight,
        "hybrid_vector_weight": hybrid_vector_weight,
        "fusion_graph_weight": fusion_graph_weight,
        "fusion_vector_weight": fusion_vector_weight,
        "graph_chunk_limit": graph_chunk_limit,
        "related_entity_limit": related_entity_limit,
        "graph_dry_run": graph_dry_run,
        "query_entity_matches": graph_retrieval.get("query_entity_matches", []),
        "graph_retrieval": {
            "status": graph_execution.get("status"),
            "ok": graph_execution.get("ok"),
            "counts": graph_execution.get("counts", {}),
            "matched_entity_count": len(graph_execution.get("matched_entities", [])),
            "chunk_count": len(graph_chunks),
            "related_entity_count": len(graph_execution.get("related_entities", [])),
        },
        "vector_retrieval": {
            "result_count": len(vector_results),
        },
        "fusion": {
            "result_count": len(fused_results),
            "source_counts": fusion_source_counts,
            "strategy": "chunk_id_union_weighted_score",
        },
        "results": fused_results,
    }
