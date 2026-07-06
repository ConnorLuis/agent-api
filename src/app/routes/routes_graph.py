from __future__ import annotations

from fastapi import APIRouter, Request

from src.app.graph import fusion as graph_fusion
from src.app.graph import ingestion as graph_ingestion
from src.app.graph import retrieval as graph_retrieval
from src.app.graph.extraction import extract_graph_items
from src.app.graph.neo4j_client import (
    check_neo4j_connection,
    skipped_neo4j_connection_check,
)
from src.app.graph.schema import get_graph_schema
from src.app.schemas.graph import (
    GraphExtractDebugRequest,
    GraphExtractDebugResponse,
    GraphFusionDebugRequest,
    GraphFusionDebugResponse,
    GraphHealthDebugResponse,
    GraphIngestDebugRequest,
    GraphIngestDebugResponse,
    GraphRetrievalDebugRequest,
    GraphRetrievalDebugResponse,
    GraphSchemaDebugResponse,
)


router = APIRouter(prefix="/graph", tags=["graph"])


def _resolve_trace_id(request: Request) -> str:
    if request.headers.get("x-trace-id"):
        return request.headers["x-trace-id"]

    try:
        from src.app.core.request_context import get_trace_id

        return get_trace_id()
    except Exception:
        return "trace-unavailable"


@router.get("/schema-debug", response_model=GraphSchemaDebugResponse)
def graph_schema_debug(request: Request) -> dict:
    schema = get_graph_schema()

    return {
        "trace_id": _resolve_trace_id(request),
        **schema,
    }


@router.get("/health-debug", response_model=GraphHealthDebugResponse)
def graph_health_debug(
    request: Request,
    check_connection: bool = False,
) -> dict:
    if check_connection:
        connection = check_neo4j_connection()
    else:
        connection = skipped_neo4j_connection_check()

    return {
        "trace_id": _resolve_trace_id(request),
        "connection_check_requested": check_connection,
        "connection": connection,
    }


@router.post("/extract-debug", response_model=GraphExtractDebugResponse)
def graph_extract_debug(
    payload: GraphExtractDebugRequest,
    request: Request,
) -> dict:
    extraction = extract_graph_items(
        source_filter=payload.source_filter,
        max_chars=payload.max_chars,
        include_related_entities=payload.include_related_entities,
    )

    return {
        "trace_id": _resolve_trace_id(request),
        **extraction,
    }


@router.post("/ingest-debug", response_model=GraphIngestDebugResponse)
def graph_ingest_debug(
    payload: GraphIngestDebugRequest,
    request: Request,
) -> dict:
    ingestion = graph_ingestion.run_graph_ingestion_debug(
        source_filter=payload.source_filter,
        max_chars=payload.max_chars,
        include_related_entities=payload.include_related_entities,
        dry_run=payload.dry_run,
        apply_schema=payload.apply_schema,
    )

    return {
        "trace_id": _resolve_trace_id(request),
        **ingestion,
    }


@router.post("/retrieval-debug", response_model=GraphRetrievalDebugResponse)
def graph_retrieval_debug(
    payload: GraphRetrievalDebugRequest,
    request: Request,
) -> dict:
    retrieval = graph_retrieval.run_graph_retrieval_debug(
        query=payload.query,
        chunk_limit=payload.chunk_limit,
        related_entity_limit=payload.related_entity_limit,
        dry_run=payload.dry_run,
    )

    return {
        "trace_id": _resolve_trace_id(request),
        **retrieval,
    }


@router.post("/fusion-debug", response_model=GraphFusionDebugResponse)
def graph_fusion_debug(
    payload: GraphFusionDebugRequest,
    request: Request,
) -> dict:
    fusion = graph_fusion.run_graph_vector_fusion_debug(
        query=payload.query,
        top_k=payload.top_k,
        source_filter=payload.source_filter,
        max_chars=payload.max_chars,
        embedding_dim=payload.embedding_dim,
        hybrid_keyword_weight=payload.hybrid_keyword_weight,
        hybrid_vector_weight=payload.hybrid_vector_weight,
        fusion_graph_weight=payload.fusion_graph_weight,
        fusion_vector_weight=payload.fusion_vector_weight,
        graph_chunk_limit=payload.graph_chunk_limit,
        related_entity_limit=payload.related_entity_limit,
        graph_dry_run=payload.graph_dry_run,
    )

    return {
        "trace_id": _resolve_trace_id(request),
        **fusion,
    }
