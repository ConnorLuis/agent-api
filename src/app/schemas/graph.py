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
