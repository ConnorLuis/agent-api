from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src.app.core.request_context import get_trace_id
from src.app.rag.agentic_streaming import stream_agentic_rag_events
from src.app.rag.retriever import search_knowledge
from src.app.rag.explain import explain_search_knowledge
from src.app.rag.chunking import debug_knowledge_chunks
from src.app.rag.vector_index import vector_search_knowledge
from src.app.rag.hybrid import hybrid_search_knowledge
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.observability.trace_store import record_trace_event
from src.app.evaluation.rag_eval import evaluate_rag_cases
from src.app.schemas.rag import RAGReaderRequest, RAGSearchResponse, RAGSearchResult, RagSearchDebugResponse, \
    RagSearchDebugRequest, RagChunksDebugResponse, RagChunksDebugRequest, RagVectorSearchDebugResponse, \
    RagVectorSearchDebugRequest, RagHybridSearchDebugResponse, RagHybridSearchDebugRequest, RagAgenticDebugResponse, \
    RagAgenticDebugRequest, RagEvalDebugResponse, RagEvalDebugRequest

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
        },
    )

    return RagEvalDebugResponse(
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
        ),
        media_type="text/event-stream",
    )