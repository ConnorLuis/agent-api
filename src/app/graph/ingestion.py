from __future__ import annotations

from typing import Any

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - defensive fallback
    GraphDatabase = None  # type: ignore[assignment]

from src.app.graph.extraction import extract_graph_items
from src.app.graph.neo4j_client import Neo4jSettings, get_neo4j_settings
from src.app.graph.schema import GRAPH_CONSTRAINTS, GRAPH_INDEXES


NODE_UPSERT_QUERIES = {
    "Document": """
UNWIND $documents AS doc
MERGE (d:Document {source: doc.source})
SET d.document_id = doc.document_id,
    d.title = doc.title,
    d.content_hash = doc.content_hash,
    d.chunk_count = doc.chunk_count
""",
    "Chunk": """
UNWIND $chunks AS chunk
MERGE (c:Chunk {chunk_id: chunk.chunk_id})
SET c.source = chunk.source,
    c.index = chunk.index,
    c.content = chunk.content,
    c.preview = chunk.preview,
    c.content_length = chunk.content_length
""",
    "Entity": """
UNWIND $entities AS entity
MERGE (e:Entity {normalized_name: entity.normalized_name, type: entity.type})
SET e.entity_id = entity.entity_id,
    e.name = entity.name,
    e.aliases = entity.aliases
""",
}


RELATION_UPSERT_QUERIES = {
    "HAS_CHUNK": """
UNWIND $relations AS rel
MATCH (d:Document {document_id: rel.source_id})
MATCH (c:Chunk {chunk_id: rel.target_id})
MERGE (d)-[r:HAS_CHUNK]->(c)
SET r.chunk_index = rel.properties.chunk_index
""",
    "NEXT_CHUNK": """
UNWIND $relations AS rel
MATCH (source:Chunk {chunk_id: rel.source_id})
MATCH (target:Chunk {chunk_id: rel.target_id})
MERGE (source)-[r:NEXT_CHUNK]->(target)
SET r.source = rel.properties.source
""",
    "MENTIONS": """
UNWIND $relations AS rel
MATCH (chunk:Chunk {chunk_id: rel.source_id})
MATCH (entity:Entity {entity_id: rel.target_id})
MERGE (chunk)-[r:MENTIONS]->(entity)
SET r.surface_text = rel.properties.surface_text,
    r.confidence = rel.properties.confidence
""",
    "RELATED_TO": """
UNWIND $relations AS rel
MATCH (source:Entity {entity_id: rel.source_id})
MATCH (target:Entity {entity_id: rel.target_id})
MERGE (source)-[r:RELATED_TO]->(target)
SET r.relation_type = rel.properties.relation_type,
    r.confidence = rel.properties.confidence,
    r.source = rel.properties.source
""",
}


def _count_relations_by_type(relations: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for relation in relations:
        relation_type = relation["type"]
        counts[relation_type] = counts.get(relation_type, 0) + 1

    return counts


def _group_relations_by_type(relations: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for relation in relations:
        grouped.setdefault(relation["type"], []).append(relation)

    return grouped


def get_graph_ingestion_cypher_templates() -> dict[str, Any]:
    return {
        "node_upsert_queries": dict(NODE_UPSERT_QUERIES),
        "relation_upsert_queries": dict(RELATION_UPSERT_QUERIES),
        "schema_statements": list(GRAPH_CONSTRAINTS) + list(GRAPH_INDEXES),
    }


def build_graph_ingestion_plan(
    extraction: dict[str, Any],
    apply_schema: bool = True,
) -> dict[str, Any]:
    documents = extraction["documents"]
    chunks = extraction["chunks"]
    entities = extraction["entities"]
    relations = extraction["relations"]

    schema_statements = list(GRAPH_CONSTRAINTS) + list(GRAPH_INDEXES) if apply_schema else []

    return {
        "apply_schema": apply_schema,
        "schema_statement_count": len(schema_statements),
        "schema_statements": schema_statements,
        "node_counts": {
            "Document": len(documents),
            "Chunk": len(chunks),
            "Entity": len(entities),
        },
        "relationship_counts": _count_relations_by_type(relations),
        "total_node_upserts": len(documents) + len(chunks) + len(entities),
        "total_relationship_upserts": len(relations),
        "node_upsert_query_keys": list(NODE_UPSERT_QUERIES.keys()),
        "relation_upsert_query_keys": list(RELATION_UPSERT_QUERIES.keys()),
        "dry_run_safe": True,
    }


def apply_graph_schema_constraints_and_indexes(session: Any) -> dict[str, Any]:
    statements = list(GRAPH_CONSTRAINTS) + list(GRAPH_INDEXES)

    for statement in statements:
        session.run(statement).consume()

    return {
        "applied_statement_count": len(statements),
        "statements": statements,
    }


def execute_graph_ingestion(
    extraction: dict[str, Any],
    settings: Neo4jSettings | None = None,
    apply_schema: bool = True,
) -> dict[str, Any]:
    current_settings = settings or get_neo4j_settings()

    if GraphDatabase is None:
        return {
            "ok": False,
            "status": "driver_missing",
            "reason": "neo4j Python driver is not installed.",
            "settings": current_settings.safe_public_dict(),
        }

    plan = build_graph_ingestion_plan(
        extraction=extraction,
        apply_schema=apply_schema,
    )

    grouped_relations = _group_relations_by_type(extraction["relations"])

    try:
        driver = GraphDatabase.driver(
            current_settings.uri,
            auth=(current_settings.username, current_settings.password),
        )

        try:
            with driver.session(database=current_settings.database) as session:
                schema_result = {
                    "applied_statement_count": 0,
                    "statements": [],
                }

                if apply_schema:
                    schema_result = apply_graph_schema_constraints_and_indexes(session)

                session.run(
                    NODE_UPSERT_QUERIES["Document"],
                    documents=extraction["documents"],
                ).consume()
                session.run(
                    NODE_UPSERT_QUERIES["Chunk"],
                    chunks=extraction["chunks"],
                ).consume()
                session.run(
                    NODE_UPSERT_QUERIES["Entity"],
                    entities=extraction["entities"],
                ).consume()

                for relation_type, query in RELATION_UPSERT_QUERIES.items():
                    session.run(
                        query,
                        relations=grouped_relations.get(relation_type, []),
                    ).consume()

            return {
                "ok": True,
                "status": "ingested",
                "reason": None,
                "schema": schema_result,
                "node_upsert_attempts": plan["node_counts"],
                "relationship_upsert_attempts": plan["relationship_counts"],
                "total_node_upsert_attempts": plan["total_node_upserts"],
                "total_relationship_upsert_attempts": plan["total_relationship_upserts"],
                "settings": current_settings.safe_public_dict(),
            }
        finally:
            driver.close()

    except Exception as exc:  # pragma: no cover - depends on live Neo4j runtime
        return {
            "ok": False,
            "status": "ingestion_failed",
            "reason": exc.__class__.__name__,
            "detail": str(exc),
            "settings": current_settings.safe_public_dict(),
        }


def run_graph_ingestion_debug(
    source_filter: str | None = "agent_basics",
    max_chars: int = 300,
    include_related_entities: bool = True,
    dry_run: bool = True,
    apply_schema: bool = True,
) -> dict[str, Any]:
    extraction = extract_graph_items(
        source_filter=source_filter,
        max_chars=max_chars,
        include_related_entities=include_related_entities,
    )

    plan = build_graph_ingestion_plan(
        extraction=extraction,
        apply_schema=apply_schema,
    )

    if dry_run:
        execution = {
            "ok": None,
            "status": "dry_run",
            "reason": "Set dry_run=false to execute Neo4j ingestion.",
            "schema": {
                "applied_statement_count": 0,
                "statements": [],
            },
            "node_upsert_attempts": plan["node_counts"],
            "relationship_upsert_attempts": plan["relationship_counts"],
            "total_node_upsert_attempts": plan["total_node_upserts"],
            "total_relationship_upsert_attempts": plan["total_relationship_upserts"],
        }
    else:
        execution = execute_graph_ingestion(
            extraction=extraction,
            apply_schema=apply_schema,
        )

    return {
        "source_filter": source_filter,
        "max_chars": max_chars,
        "include_related_entities": include_related_entities,
        "dry_run": dry_run,
        "apply_schema": apply_schema,
        "extraction_counts": extraction["counts"],
        "documents": extraction["documents"],
        "entities": extraction["entities"],
        "relation_preview": extraction["relations"][:10],
        "plan": plan,
        "execution": execution,
    }
