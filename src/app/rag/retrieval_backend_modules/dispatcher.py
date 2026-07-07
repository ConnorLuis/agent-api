from pathlib import Path
from typing import Any

from src.app.rag.chroma_store import (
    DEFAULT_CHROMA_PERSIST_DIR,
    debug_chroma_search,
)
from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.embedding_provider import DEFAULT_EMBEDDING_PROVIDER
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.retrieval_backend_modules.normalization import DEFAULT_RETRIEVAL_BACKEND, normalize_retrieval_backend
from src.app.rag.retrieval_backend_modules.result_normalizers import _normalize_graph_fusion_results, \
    _normalize_hybrid_results, _normalize_chroma_results
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM
from src.app.rag.reranker import rerank_retrieval_results
from src.app.graph.fusion import run_graph_vector_fusion_debug

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
    graph_dry_run: bool = True,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
) -> dict[str, Any]:
    backend = normalize_retrieval_backend(retrieval_backend)

    if backend == "graph_fusion":
        fusion_payload = run_graph_vector_fusion_debug(
            query=query,
            top_k=top_k,
            source_filter=source_filter,
            max_chars=max_chars,
            embedding_dim=embedding_dim,
            hybrid_keyword_weight=keyword_weight,
            hybrid_vector_weight=vector_weight,
            fusion_graph_weight=fusion_graph_weight,
            fusion_vector_weight=fusion_vector_weight,
            graph_chunk_limit=graph_chunk_limit,
            related_entity_limit=related_entity_limit,
            graph_dry_run=graph_dry_run,
        )

        normalized_results = _normalize_graph_fusion_results(
            fusion_payload.get("results", [])
        )

        return {
            "retrieval_backend": "graph_fusion",
            "results": normalized_results,
            "metadata": {
                "retrieval_backend": "graph_fusion",
                "graph_dry_run": graph_dry_run,
                "fusion_graph_weight": fusion_graph_weight,
                "fusion_vector_weight": fusion_vector_weight,
                "graph_chunk_limit": graph_chunk_limit,
                "related_entity_limit": related_entity_limit,
                "query_entity_matches": fusion_payload.get("query_entity_matches", []),
                "graph_retrieval": fusion_payload.get("graph_retrieval", {}),
                "vector_retrieval": fusion_payload.get("vector_retrieval", {}),
                "fusion": fusion_payload.get("fusion", {}),
            },
        }

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

    if backend == "chroma_rerank":
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

        normalized_results = _normalize_chroma_results(result["results"])
        reranked_results = rerank_retrieval_results(
            query=query,
            results=normalized_results,
        )

        for item in reranked_results:
            item["retrieval_backend"] = "chroma_rerank"

        return {
            "retrieval_backend": "chroma_rerank",
            "query": query,
            "results": reranked_results,
            "metadata": {
                "retrieval_backend": "chroma_rerank",
                "base_backend": "chroma",
                "rerank_enabled": True,
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