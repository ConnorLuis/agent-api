from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.rag.retriever import search_knowledge
from src.app.schemas.rag import RAGReaderRequest, RAGSearchResponse, RAGSearchResult


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