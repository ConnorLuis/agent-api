from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.rag.retriever import search_knowledge
from src.app.rag.explain import explain_search_knowledge
from src.app.rag.chunking import debug_knowledge_chunks
from src.app.rag.vector_index import vector_search_knowledge
from src.app.schemas.rag import RAGReaderRequest, RAGSearchResponse, RAGSearchResult, RagSearchDebugResponse, \
    RagSearchDebugRequest, RagChunksDebugResponse, RagChunksDebugRequest, RagVectorSearchDebugResponse, \
    RagVectorSearchDebugRequest

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


