from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.rag.answer_verifier import verify_agentic_rag_answer
from src.app.observability.trace_store import record_trace_event
from src.app.schemas.rag import RagAnswerVerifyDebugResponse, RagAnswerVerifyDebugRequest

router = APIRouter()

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
        event_type="rag_answer_verify_debug",
        payload={
            "query": result["query"],
            "rewritten_query": result["rewritten_query"],
            "retrieval_needed": result["retrieval_needed"],
            "relevance_score": result["relevance_score"],
            "citations": result["citations"],
            "steps": result["steps"],
            "verification": result["verification"],
            "retrieval_backend": result.get("retrieval_backend"),
            "retrieval_metadata": result.get("retrieval_metadata", {}),
            "graph_vector_contribution": result.get("graph_vector_contribution", {}),
            "graph_fusion_verification": result.get("graph_fusion_verification", {}),
            "verification_pass": result.get("verification_pass"),
            "answer_supported": result.get("answer_supported"),
            "confidence": result.get("confidence"),
            "risk_flags": result.get("risk_flags", []),
        },
    )

    return RagAnswerVerifyDebugResponse(
        **result,
        trace_id=trace_id,
    )