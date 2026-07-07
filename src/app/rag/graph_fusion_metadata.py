from __future__ import annotations

from typing import Any


def build_graph_vector_contribution(
    retrieval_backend: str | None,
    retrieval_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a compact graph/vector contribution summary for GraphRAG fusion.

    This helper is intentionally pure and CI-safe. It does not call Neo4j.
    It only summarizes metadata already produced by graph_fusion retrieval.
    """

    if retrieval_backend != "graph_fusion":
        return {}

    if not retrieval_metadata:
        return {}

    graph_retrieval = retrieval_metadata.get("graph_retrieval", {}) or {}
    vector_retrieval = retrieval_metadata.get("vector_retrieval", {}) or {}
    fusion = retrieval_metadata.get("fusion", {}) or {}
    source_counts = fusion.get("source_counts", {}) or {}

    return {
        "retrieval_backend": "graph_fusion",
        "graph_dry_run": retrieval_metadata.get("graph_dry_run", True),
        "graph_status": graph_retrieval.get("status"),
        "graph_ok": graph_retrieval.get("ok"),
        "graph_chunk_count": graph_retrieval.get("chunk_count", 0),
        "graph_related_entity_count": graph_retrieval.get("related_entity_count", 0),
        "vector_result_count": vector_retrieval.get("result_count", 0),
        "fusion_result_count": fusion.get("result_count", 0),
        "graph_only_count": source_counts.get("graph_only", 0),
        "vector_only_count": source_counts.get("vector_only", 0),
        "graph_and_vector_count": source_counts.get("graph_and_vector", 0),
        "query_entity_match_count": len(
            retrieval_metadata.get("query_entity_matches", []) or []
        ),
    }


def build_graph_fusion_trace_payload(
    retrieval_backend: str | None,
    retrieval_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a GraphRAG-aware trace payload extension.

    This keeps trace payloads stable and concise while preserving the important
    graph/vector contribution details.
    """

    contribution = build_graph_vector_contribution(
        retrieval_backend=retrieval_backend,
        retrieval_metadata=retrieval_metadata,
    )

    if not contribution:
        return {}

    return {
        "retrieval_backend": "graph_fusion",
        "graph_vector_contribution": contribution,
        "graph_retrieval": (retrieval_metadata or {}).get("graph_retrieval", {}),
        "vector_retrieval": (retrieval_metadata or {}).get("vector_retrieval", {}),
        "fusion": (retrieval_metadata or {}).get("fusion", {}),
        "query_entity_matches": (retrieval_metadata or {}).get(
            "query_entity_matches",
            [],
        ),
    }
