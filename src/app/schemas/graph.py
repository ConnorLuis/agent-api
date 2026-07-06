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
