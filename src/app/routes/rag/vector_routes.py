from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.observability.trace_store import record_trace_event
from src.app.rag.vector_store import debug_vector_store_search
from src.app.rag.embedding_provider import debug_embeddings
from src.app.rag.chroma_store import debug_chroma_search
from src.app.schemas.rag import RagVectorStoreDebugResponse, RagVectorStoreDebugRequest, RagEmbeddingDebugResponse, \
    RagEmbeddingDebugRequest, RagChromaSearchDebugResponse, RagChromaSearchDebugRequest

router = APIRouter()


@router.post("/vector-store-debug", response_model=RagVectorStoreDebugResponse)
def rag_vector_store_debug(
    request: RagVectorStoreDebugRequest,
) -> RagVectorStoreDebugResponse:
    result = debug_vector_store_search(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        rebuild_index=request.rebuild_index,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_vector_store_debug",
        payload={
            "query": result["query"],
            "top_k": result["top_k"],
            "source_filter": result["source_filter"],
            "max_chars": result["max_chars"],
            "embedding_dim": result["embedding_dim"],
            "embedding_provider": result["embedding_provider"],
            "embedding_model": result["embedding_model"],
            "rebuild_index": result["rebuild_index"],
            "total_indexed_chunks": result["total_indexed_chunks"],
            "index_stats": result["index_stats"],
            "results_count": len(result["results"]),
        },
    )

    return RagVectorStoreDebugResponse(
        **result,
        trace_id=trace_id,
    )


@router.post("/embedding-debug", response_model=RagEmbeddingDebugResponse)
def rag_embedding_debug(
    request: RagEmbeddingDebugRequest,
) -> RagEmbeddingDebugResponse:
    result = debug_embeddings(
        query=request.query,
        documents=request.documents,
        provider=request.provider,
        model_name=request.model_name,
        embedding_dim=request.embedding_dim,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_embedding_debug",
        payload={
            "query": result["query"],
            "provider": result["provider"],
            "model": result["model"],
            "requested_embedding_dim": result["requested_embedding_dim"],
            "actual_embedding_dim": result["actual_embedding_dim"],
            "documents_count": result["documents_count"],
        },
    )

    return RagEmbeddingDebugResponse(
        **result,
        trace_id=trace_id,
    )


@router.post("/chroma-search-debug", response_model=RagChromaSearchDebugResponse)
def rag_chroma_search_debug(
    request: RagChromaSearchDebugRequest,
) -> RagChromaSearchDebugResponse:
    result = debug_chroma_search(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        rebuild_index=request.rebuild_index,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_chroma_search_debug",
        payload={
            "query": result["query"],
            "top_k": result["top_k"],
            "source_filter": result["source_filter"],
            "max_chars": result["max_chars"],
            "embedding_dim": result["embedding_dim"],
            "embedding_provider": result["embedding_provider"],
            "embedding_model": result["embedding_model"],
            "collection_name": result["collection_name"],
            "persist_dir": result["persist_dir"],
            "total_indexed_chunks": result["total_indexed_chunks"],
            "rebuild_index": result["rebuild_index"],
            "index_stats": result["index_stats"],
            "results_count": len(result["results"]),
        },
    )

    return RagChromaSearchDebugResponse(
        **result,
        trace_id=trace_id,
    )