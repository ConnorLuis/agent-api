from __future__ import annotations

from typing import Any


GRAPH_SCHEMA_VERSION = "day42_graph_schema_v1"


GRAPH_NODE_LABELS = [
    "Document",
    "Chunk",
    "Entity",
]


GRAPH_RELATION_TYPES = [
    "HAS_CHUNK",
    "NEXT_CHUNK",
    "MENTIONS",
    "RELATED_TO",
]


GRAPH_NODE_PROPERTIES: dict[str, list[str]] = {
    "Document": [
        "source",
        "title",
        "content_hash",
        "created_at_ms",
    ],
    "Chunk": [
        "chunk_id",
        "source",
        "index",
        "content",
        "preview",
        "content_length",
    ],
    "Entity": [
        "name",
        "normalized_name",
        "type",
        "created_at_ms",
    ],
}


GRAPH_RELATION_PROPERTIES: dict[str, list[str]] = {
    "HAS_CHUNK": [
        "chunk_index",
    ],
    "NEXT_CHUNK": [
        "source",
    ],
    "MENTIONS": [
        "surface_text",
        "confidence",
    ],
    "RELATED_TO": [
        "relation_type",
        "confidence",
        "source",
    ],
}


GRAPH_CONSTRAINTS = [
    "CREATE CONSTRAINT document_source_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.source IS UNIQUE",
    "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE",
    "CREATE CONSTRAINT entity_identity_unique IF NOT EXISTS FOR (e:Entity) REQUIRE (e.normalized_name, e.type) IS UNIQUE",
]


GRAPH_INDEXES = [
    "CREATE INDEX chunk_source_index IF NOT EXISTS FOR (c:Chunk) ON (c.source)",
    "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
    "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
]


def get_graph_schema() -> dict[str, Any]:
    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "node_labels": list(GRAPH_NODE_LABELS),
        "relation_types": list(GRAPH_RELATION_TYPES),
        "node_properties": dict(GRAPH_NODE_PROPERTIES),
        "relation_properties": dict(GRAPH_RELATION_PROPERTIES),
        "constraints": list(GRAPH_CONSTRAINTS),
        "indexes": list(GRAPH_INDEXES),
    }


def get_graph_schema_summary() -> dict[str, Any]:
    schema = get_graph_schema()
    return {
        "schema_version": schema["schema_version"],
        "node_label_count": len(schema["node_labels"]),
        "relation_type_count": len(schema["relation_types"]),
        "constraint_count": len(schema["constraints"]),
        "index_count": len(schema["indexes"]),
        "node_labels": schema["node_labels"],
        "relation_types": schema["relation_types"],
    }
