from __future__ import annotations

from typing import Any

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - defensive fallback
    GraphDatabase = None  # type: ignore[assignment]

from src.app.graph.extraction import ENTITY_PATTERNS, EntityPattern
from src.app.graph.neo4j_client import Neo4jSettings, get_neo4j_settings


MATCHED_ENTITIES_QUERY = """
MATCH (e:Entity)
WHERE e.entity_id IN $entity_ids
RETURN e
ORDER BY e.type ASC, e.normalized_name ASC
"""


MENTIONED_CHUNKS_QUERY = """
MATCH (chunk:Chunk)-[m:MENTIONS]->(e:Entity)
WHERE e.entity_id IN $entity_ids
OPTIONAL MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
WITH chunk,
     doc,
     collect(DISTINCT e {
       .entity_id,
       .name,
       .normalized_name,
       .type
     }) AS matched_entities,
     collect(DISTINCT {
       entity_id: e.entity_id,
       surface_text: m.surface_text,
       confidence: m.confidence
     }) AS mentions
RETURN chunk, doc, matched_entities, mentions
ORDER BY chunk.source ASC, chunk.index ASC
LIMIT $chunk_limit
"""


RELATED_ENTITIES_QUERY = """
MATCH (e:Entity)-[r:RELATED_TO]-(related:Entity)
WHERE e.entity_id IN $entity_ids
WITH e, r, related
RETURN DISTINCT
  e {
    .entity_id,
    .name,
    .normalized_name,
    .type
  } AS source_entity,
  related {
    .entity_id,
    .name,
    .normalized_name,
    .type
  } AS related_entity,
  type(r) AS relationship_type,
  r.relation_type AS relation_type,
  r.confidence AS confidence,
  r.source AS source
ORDER BY related_entity.type ASC, related_entity.normalized_name ASC
LIMIT $related_entity_limit
"""


def _find_query_alias(query: str, pattern: EntityPattern) -> str | None:
    lower_query = query.lower()

    for alias in sorted(pattern.aliases, key=len, reverse=True):
        if alias.lower() in lower_query:
            return alias

    return None


def _entity_id(pattern: EntityPattern) -> str:
    return f"Entity:{pattern.entity_type}:{pattern.normalized_name}"


def extract_query_entity_matches(query: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    for pattern in ENTITY_PATTERNS:
        matched_alias = _find_query_alias(query=query, pattern=pattern)

        if matched_alias is None:
            continue

        matches.append(
            {
                "entity_id": _entity_id(pattern),
                "name": pattern.name,
                "normalized_name": pattern.normalized_name,
                "type": pattern.entity_type,
                "matched_alias": matched_alias,
                "aliases": list(pattern.aliases),
            }
        )

    return sorted(
        matches,
        key=lambda item: (item["type"], item["normalized_name"]),
    )


def get_graph_retrieval_cypher_templates() -> dict[str, str]:
    return {
        "matched_entities": MATCHED_ENTITIES_QUERY,
        "mentioned_chunks": MENTIONED_CHUNKS_QUERY,
        "related_entities": RELATED_ENTITIES_QUERY,
    }


def build_graph_retrieval_plan(
    query: str,
    chunk_limit: int = 5,
    related_entity_limit: int = 10,
) -> dict[str, Any]:
    query_entity_matches = extract_query_entity_matches(query)
    entity_ids = [entity["entity_id"] for entity in query_entity_matches]

    return {
        "query": query,
        "chunk_limit": chunk_limit,
        "related_entity_limit": related_entity_limit,
        "query_entity_matches": query_entity_matches,
        "matched_entity_ids": entity_ids,
        "cypher_query_keys": list(get_graph_retrieval_cypher_templates().keys()),
        "dry_run_safe": True,
    }


def _node_to_dict(node: Any | None) -> dict[str, Any] | None:
    if node is None:
        return None

    return dict(node)


def _serialize_matched_entity_record(record: Any) -> dict[str, Any]:
    entity = _node_to_dict(record["e"]) or {}

    return {
        "entity_id": entity.get("entity_id"),
        "name": entity.get("name"),
        "normalized_name": entity.get("normalized_name"),
        "type": entity.get("type"),
        "aliases": entity.get("aliases", []),
    }


def _serialize_chunk_record(record: Any) -> dict[str, Any]:
    chunk = _node_to_dict(record["chunk"]) or {}
    document = _node_to_dict(record["doc"])

    return {
        "chunk_id": chunk.get("chunk_id"),
        "source": chunk.get("source"),
        "index": chunk.get("index"),
        "content": chunk.get("content"),
        "preview": chunk.get("preview"),
        "content_length": chunk.get("content_length"),
        "document": document,
        "matched_entities": record.get("matched_entities", []),
        "mentions": record.get("mentions", []),
    }


def _serialize_related_entity_record(record: Any) -> dict[str, Any]:
    return {
        "source_entity": record.get("source_entity"),
        "related_entity": record.get("related_entity"),
        "relationship_type": record.get("relationship_type"),
        "relation_type": record.get("relation_type"),
        "confidence": record.get("confidence"),
        "source": record.get("source"),
    }


def execute_graph_retrieval(
    query: str,
    query_entity_matches: list[dict[str, Any]],
    chunk_limit: int = 5,
    related_entity_limit: int = 10,
    settings: Neo4jSettings | None = None,
) -> dict[str, Any]:
    current_settings = settings or get_neo4j_settings()
    entity_ids = [entity["entity_id"] for entity in query_entity_matches]

    if not entity_ids:
        return {
            "ok": True,
            "status": "no_query_entity_match",
            "reason": "No known query entity matched the configured graph entity patterns.",
            "matched_entities": [],
            "chunks": [],
            "related_entities": [],
            "settings": current_settings.safe_public_dict(),
        }

    if GraphDatabase is None:
        return {
            "ok": False,
            "status": "driver_missing",
            "reason": "neo4j Python driver is not installed.",
            "matched_entities": [],
            "chunks": [],
            "related_entities": [],
            "settings": current_settings.safe_public_dict(),
        }

    try:
        driver = GraphDatabase.driver(
            current_settings.uri,
            auth=(current_settings.username, current_settings.password),
        )

        try:
            with driver.session(database=current_settings.database) as session:
                matched_entity_records = session.run(
                    MATCHED_ENTITIES_QUERY,
                    entity_ids=entity_ids,
                )
                matched_entities = [
                    _serialize_matched_entity_record(record)
                    for record in matched_entity_records
                ]

                chunk_records = session.run(
                    MENTIONED_CHUNKS_QUERY,
                    entity_ids=entity_ids,
                    chunk_limit=chunk_limit,
                )
                chunks = [
                    _serialize_chunk_record(record)
                    for record in chunk_records
                ]

                related_entity_records = session.run(
                    RELATED_ENTITIES_QUERY,
                    entity_ids=entity_ids,
                    related_entity_limit=related_entity_limit,
                )
                related_entities = [
                    _serialize_related_entity_record(record)
                    for record in related_entity_records
                ]

            return {
                "ok": True,
                "status": "retrieved",
                "reason": None,
                "matched_entities": matched_entities,
                "chunks": chunks,
                "related_entities": related_entities,
                "counts": {
                    "matched_entities": len(matched_entities),
                    "chunks": len(chunks),
                    "related_entities": len(related_entities),
                },
                "settings": current_settings.safe_public_dict(),
            }
        finally:
            driver.close()

    except Exception as exc:  # pragma: no cover - depends on live Neo4j runtime
        return {
            "ok": False,
            "status": "retrieval_failed",
            "reason": exc.__class__.__name__,
            "detail": str(exc),
            "matched_entities": [],
            "chunks": [],
            "related_entities": [],
            "settings": current_settings.safe_public_dict(),
        }


def run_graph_retrieval_debug(
    query: str,
    chunk_limit: int = 5,
    related_entity_limit: int = 10,
    dry_run: bool = True,
) -> dict[str, Any]:
    plan = build_graph_retrieval_plan(
        query=query,
        chunk_limit=chunk_limit,
        related_entity_limit=related_entity_limit,
    )

    query_entity_matches = plan["query_entity_matches"]

    if not query_entity_matches:
        execution = {
            "ok": True,
            "status": "no_query_entity_match",
            "reason": "No known query entity matched the configured graph entity patterns.",
            "matched_entities": [],
            "chunks": [],
            "related_entities": [],
            "counts": {
                "matched_entities": 0,
                "chunks": 0,
                "related_entities": 0,
            },
        }
    elif dry_run:
        execution = {
            "ok": None,
            "status": "dry_run",
            "reason": "Set dry_run=false to execute Neo4j graph retrieval.",
            "matched_entities": [],
            "chunks": [],
            "related_entities": [],
            "counts": {
                "matched_entities": 0,
                "chunks": 0,
                "related_entities": 0,
            },
        }
    else:
        execution = execute_graph_retrieval(
            query=query,
            query_entity_matches=query_entity_matches,
            chunk_limit=chunk_limit,
            related_entity_limit=related_entity_limit,
        )

    return {
        "query": query,
        "chunk_limit": chunk_limit,
        "related_entity_limit": related_entity_limit,
        "dry_run": dry_run,
        "query_entity_matches": query_entity_matches,
        "plan": plan,
        "execution": execution,
    }
