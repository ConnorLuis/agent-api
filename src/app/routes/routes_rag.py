from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src.app.core.request_context import get_trace_id
from src.app.rag.agentic_streaming import stream_agentic_rag_events
from src.app.rag.answer_verifier import verify_agentic_rag_answer
from src.app.rag.retriever import search_knowledge
from src.app.rag.explain import explain_search_knowledge
from src.app.rag.chunking import debug_knowledge_chunks
from src.app.rag.vector_index import vector_search_knowledge
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.observability.trace_store import record_trace_event
from src.app.evaluation.rag_eval import evaluate_rag_cases, compare_rag_retrieval_backends
from src.app.rag.vector_store import debug_vector_store_search
from src.app.rag.embedding_provider import debug_embeddings
from src.app.rag.chroma_store import debug_chroma_search
from src.app.schemas.rag import RAGReaderRequest, RAGSearchResponse, RAGSearchResult, RagSearchDebugResponse, \
    RagSearchDebugRequest, RagChunksDebugResponse, RagChunksDebugRequest, RagVectorSearchDebugResponse, \
    RagVectorSearchDebugRequest, RagHybridSearchDebugResponse, RagHybridSearchDebugRequest, RagAgenticDebugResponse, \
    RagAgenticDebugRequest, RagEvalDebugResponse, RagEvalDebugRequest, RagAnswerVerifyDebugResponse, \
    RagAnswerVerifyDebugRequest, RagVectorStoreDebugResponse, RagVectorStoreDebugRequest, RagEmbeddingDebugResponse, \
    RagEmbeddingDebugRequest, RagChromaSearchDebugResponse, RagChromaSearchDebugRequest, RagBackendEvalDebugResponse, \
    RagBackendEvalDebugRequest

router = APIRouter()


@router.post("/search", response_model=RAGSearchResponse)
def rag_search(request: RAGReaderRequest) -> RAGSearchResponse:
    results = search_knowledge(query=request.query, k=request.k)
    return RAGSearchResponse(
        query=request.query,
        results=[
            RAGSearchResult(
                source=item.source,
                content=item.content,
                score=item.score,
            )
            for item in results
        ],
        trace_id=get_trace_id(),
    )


@router.post("/search-debug", response_model=RagSearchDebugResponse)
def rag_search_debug(request: RagSearchDebugRequest) -> RagSearchDebugResponse:
    result = explain_search_knowledge(
        query=request.query,
        k=request.k,
    )

    return RagSearchDebugResponse(
        **result,
        trace_id=get_trace_id(),
    )


@router.post("/chunks-debug", response_model=RagChunksDebugResponse)
def rag_chunks_debug(request: RagChunksDebugRequest) -> RagChunksDebugResponse:
    result = debug_knowledge_chunks(
        source_filter=request.source_filter,
        max_chars=request.max_chars,
    )

    return RagChunksDebugResponse(
        **result,
        trace_id=get_trace_id(),
    )


@router.post("/vector-search-debug", response_model=RagVectorSearchDebugResponse)
def rag_vector_search_debug(
    request: RagVectorSearchDebugRequest,
) -> RagVectorSearchDebugResponse:
    result = vector_search_knowledge(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
    )

    return RagVectorSearchDebugResponse(
        **result,
        trace_id=get_trace_id(),
    )


@router.post("/hybrid-search-debug", response_model=RagHybridSearchDebugResponse)
def rag_hybrid_search_debug(
    request: RagHybridSearchDebugRequest,
) -> RagHybridSearchDebugResponse:
    result = hybrid_search_knowledge(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
    )

    return RagHybridSearchDebugResponse(
        **result,
        trace_id=get_trace_id(),
    )

@router.post("/agentic-debug", response_model=RagAgenticDebugResponse)
def rag_agentic_debug(
    request: RagAgenticDebugRequest,
) -> RagAgenticDebugResponse:
    result = invoke_agentic_rag(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
        retrieval_backend=request.retrieval_backend,
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        rebuild_index=request.rebuild_index,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_agentic_debug",
        payload={
            "query": result["query"],
            "rewritten_query": result["rewritten_query"],
            "retrieval_needed": result["retrieval_needed"],
            "relevance_score": result["relevance_score"],
            "citations": result["citations"],
            "steps": result["steps"],
            "retrieval_results_count": len(result["retrieval_results"]),
            "retrieval_backend": result.get("retrieval_backend"),
            "retrieval_metadata": result.get("retrieval_metadata", {}),
        },
    )

    return RagAgenticDebugResponse(
        **result,
        trace_id=trace_id,
    )


@router.post("/eval-debug", response_model=RagEvalDebugResponse)
def rag_eval_debug(
    request: RagEvalDebugRequest,
) -> RagEvalDebugResponse:
    result = evaluate_rag_cases(
        eval_file=request.eval_file,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
        retrieval_backend=request.retrieval_backend,
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        rebuild_index=request.rebuild_index,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_eval_debug",
        payload={
            "eval_file": result["eval_file"],
            "source_filter": result["source_filter"],
            "metrics": result["metrics"],
            "case_count": len(result["cases"]),
            "retrieval_backend": result["retrieval_backend"],
            "embedding_provider": result["embedding_provider"],
            "embedding_model": result["embedding_model"],
            "rebuild_index": result["rebuild_index"],
        },
    )

    return RagEvalDebugResponse(
        **result,
        trace_id=trace_id,
    )


@router.post("/backend-eval-debug", response_model=RagBackendEvalDebugResponse)
def rag_backend_eval_debug(
    request: RagBackendEvalDebugRequest,
) -> RagBackendEvalDebugResponse:
    result = compare_rag_retrieval_backends(
        eval_file=request.eval_file,
        backends=request.backends,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        rebuild_index=request.rebuild_index,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_backend_eval_debug",
        payload={
            "eval_file": result["eval_file"],
            "backends": result["backends"],
            "source_filter": result["source_filter"],
            "embedding_dim": result["embedding_dim"],
            "best_backend_by_pass_rate": result["best_backend_by_pass_rate"],
            "best_backend_by_average_relevance": result[
                "best_backend_by_average_relevance"
            ],
            "pairwise_metric_deltas": result["pairwise_metric_deltas"],
            "metric_deltas": result["metric_deltas"],
            "comparison_summary": result["comparison_summary"],
            "case_comparisons": result["case_comparisons"],
            "backend_metrics": [
                {
                    "retrieval_backend": item["retrieval_backend"],
                    "metrics": item["metrics"],
                }
                for item in result["results"]
            ],
        },
    )

    return RagBackendEvalDebugResponse(
        **result,
        trace_id=trace_id,
    )


@router.post("/agentic-stream")
def rag_agentic_stream(
    request: RagAgenticDebugRequest,
) -> StreamingResponse:
    trace_id = get_trace_id()

    return StreamingResponse(
        stream_agentic_rag_events(
            query=request.query,
            trace_id=trace_id,
            top_k=request.top_k,
            source_filter=request.source_filter,
            max_chars=request.max_chars,
            embedding_dim=request.embedding_dim,
            keyword_weight=request.keyword_weight,
            vector_weight=request.vector_weight,
            retrieval_backend=request.retrieval_backend,
            embedding_provider=request.embedding_provider,
            embedding_model=request.embedding_model,
            rebuild_index=request.rebuild_index,
        ),
        media_type="text/event-stream",
    )


@router.post("/answer-verify-debug", response_model=RagAnswerVerifyDebugResponse)
def rag_answer_verify_debug(
    request: RagAnswerVerifyDebugRequest,
) -> RagAnswerVerifyDebugResponse:
    result = verify_agentic_rag_answer(
        query=request.query,
        top_k=request.top_k,
        source_filter=request.source_filter,
        max_chars=request.max_chars,
        embedding_dim=request.embedding_dim,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
    )

    trace_id = get_trace_id()

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_answer_verify_debug",
        payload={
            "query": result["query"],
            "rewritten_query": result["rewritten_query"],
            "retrieval_needed": result["retrieval_needed"],
            "relevance_score": result["relevance_score"],
            "citations": result["citations"],
            "steps": result["steps"],
            "verification": result["verification"],
        },
    )

    return RagAnswerVerifyDebugResponse(
        **result,
        trace_id=trace_id,
    )


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