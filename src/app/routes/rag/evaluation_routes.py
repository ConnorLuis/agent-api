from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.observability.trace_store import record_trace_event
from src.app.evaluation.rag_eval import evaluate_rag_cases, compare_rag_retrieval_backends
from src.app.schemas.rag import RagEvalDebugResponse, RagEvalDebugRequest, RagBackendEvalDebugResponse, \
    RagBackendEvalDebugRequest

router = APIRouter()

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
        graph_dry_run=request.graph_dry_run,
        fusion_graph_weight=request.fusion_graph_weight,
        fusion_vector_weight=request.fusion_vector_weight,
        graph_chunk_limit=request.graph_chunk_limit,
        related_entity_limit=request.related_entity_limit,
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
            "graph_dry_run": result.get("graph_dry_run"),
            "fusion_graph_weight": result.get("fusion_graph_weight"),
            "fusion_vector_weight": result.get("fusion_vector_weight"),
            "graph_chunk_limit": result.get("graph_chunk_limit"),
            "related_entity_limit": result.get("related_entity_limit"),
            "graph_evaluation_metadata": result.get("graph_evaluation_metadata", {}),
            "cases": result.get("cases", []),
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
        graph_dry_run=request.graph_dry_run,
        fusion_graph_weight=request.fusion_graph_weight,
        fusion_vector_weight=request.fusion_vector_weight,
        graph_chunk_limit=request.graph_chunk_limit,
        related_entity_limit=request.related_entity_limit,
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
            "evaluation_report": result.get("evaluation_report", {}),
            "case_comparisons": result["case_comparisons"],
            "backend_metrics": [
                {
                    "retrieval_backend": item["retrieval_backend"],
                    "metrics": item["metrics"],
                }
                for item in result["results"]
            ],
            "graph_dry_run": result.get("graph_dry_run"),
            "fusion_graph_weight": result.get("fusion_graph_weight"),
            "fusion_vector_weight": result.get("fusion_vector_weight"),
            "graph_chunk_limit": result.get("graph_chunk_limit"),
            "related_entity_limit": result.get("related_entity_limit"),
            "graph_evaluation_metadata": result.get("graph_evaluation_metadata", {}),
            "results": result.get("results", []),
        },
    )

    return RagBackendEvalDebugResponse(
        **result,
        trace_id=trace_id,
    )