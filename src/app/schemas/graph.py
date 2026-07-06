from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GraphSchemaDebugResponse(BaseModel):
    trace_id: str
    schema_version: str
    node_labels: list[str]
    relation_types: list[str]
    node_properties: dict[str, list[str]]
    relation_properties: dict[str, list[str]]
    constraints: list[str]
    indexes: list[str]


class GraphHealthDebugResponse(BaseModel):
    trace_id: str
    connection_check_requested: bool
    connection: dict[str, Any]


class GraphExtractDebugRequest(BaseModel):
    source_filter: str | None = "agent_basics"
    max_chars: int = 300
    include_related_entities: bool = True


class GraphExtractDebugResponse(BaseModel):
    trace_id: str
    source_filter: str | None
    max_chars: int
    include_related_entities: bool
    documents: list[dict[str, Any]]
    chunks: list[dict[str, Any]]
    entities: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    counts: dict[str, Any]


class GraphIngestDebugRequest(BaseModel):
    source_filter: str | None = "agent_basics"
    max_chars: int = 300
    include_related_entities: bool = True
    dry_run: bool = True
    apply_schema: bool = True


class GraphIngestDebugResponse(BaseModel):
    trace_id: str
    source_filter: str | None
    max_chars: int
    include_related_entities: bool
    dry_run: bool
    apply_schema: bool
    extraction_counts: dict[str, Any]
    documents: list[dict[str, Any]]
    entities: list[dict[str, Any]]
    relation_preview: list[dict[str, Any]]
    plan: dict[str, Any]
    execution: dict[str, Any]


class GraphRetrievalDebugRequest(BaseModel):
    query: str
    chunk_limit: int = 5
    related_entity_limit: int = 10
    dry_run: bool = True


class GraphRetrievalDebugResponse(BaseModel):
    trace_id: str
    query: str
    chunk_limit: int
    related_entity_limit: int
    dry_run: bool
    query_entity_matches: list[dict[str, Any]]
    plan: dict[str, Any]
    execution: dict[str, Any]


class GraphFusionDebugRequest(BaseModel):
    query: str
    top_k: int = 5
    source_filter: str | None = "agent_basics"
    max_chars: int = 300
    embedding_dim: int = 64
    hybrid_keyword_weight: float = 0.6
    hybrid_vector_weight: float = 0.4
    fusion_graph_weight: float = 0.5
    fusion_vector_weight: float = 0.5
    graph_chunk_limit: int = 5
    related_entity_limit: int = 10
    graph_dry_run: bool = True


class GraphFusionDebugResponse(BaseModel):
    trace_id: str
    query: str
    top_k: int
    source_filter: str | None
    max_chars: int
    embedding_dim: int
    hybrid_keyword_weight: float
    hybrid_vector_weight: float
    fusion_graph_weight: float
    fusion_vector_weight: float
    graph_chunk_limit: int
    related_entity_limit: int
    graph_dry_run: bool
    query_entity_matches: list[dict[str, Any]]
    graph_retrieval: dict[str, Any]
    vector_retrieval: dict[str, Any]
    fusion: dict[str, Any]
    results: list[dict[str, Any]]
