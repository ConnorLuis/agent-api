from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src.app.core.request_context import get_trace_id
from src.app.rag.agentic_streaming import stream_agentic_rag_events
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.observability.trace_store import record_trace_event
from src.app.schemas.rag import RagAgenticDebugResponse, RagAgenticDebugRequest

router = APIRouter()


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
        graph_dry_run=request.graph_dry_run,
        fusion_graph_weight=request.fusion_graph_weight,
        fusion_vector_weight=request.fusion_vector_weight,
        graph_chunk_limit=request.graph_chunk_limit,
        related_entity_limit=request.related_entity_limit,
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
            "graph_vector_contribution": result.get("graph_vector_contribution", {}),
        },
    )

    return RagAgenticDebugResponse(
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