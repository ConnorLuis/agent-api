from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass
from typing import Any

from src.app.rag.chunking import load_knowledge_chunks


@dataclass(frozen=True)
class EntityPattern:
    name: str
    normalized_name: str
    entity_type: str
    aliases: tuple[str, ...]


ENTITY_PATTERNS: tuple[EntityPattern, ...] = (
    EntityPattern(
        name="Agent",
        normalized_name="agent",
        entity_type="concept",
        aliases=("Agent", "agent", "智能体"),
    ),
    EntityPattern(
        name="RAG",
        normalized_name="rag",
        entity_type="concept",
        aliases=("RAG", "Retrieval-Augmented Generation", "检索增强生成"),
    ),
    EntityPattern(
        name="LangGraph",
        normalized_name="langgraph",
        entity_type="framework",
        aliases=("LangGraph", "langgraph"),
    ),
    EntityPattern(
        name="Tool",
        normalized_name="tool",
        entity_type="concept",
        aliases=("Tool", "tool", "工具", "工具调用"),
    ),
    EntityPattern(
        name="Memory",
        normalized_name="memory",
        entity_type="concept",
        aliases=("Memory", "memory", "记忆", "短期记忆"),
    ),
    EntityPattern(
        name="Router Agent",
        normalized_name="router_agent",
        entity_type="component",
        aliases=("Router Agent", "router", "路由", "路由器"),
    ),
    EntityPattern(
        name="Smart Chat",
        normalized_name="smart_chat",
        entity_type="component",
        aliases=("Smart Chat", "smart chat", "统一入口"),
    ),
    EntityPattern(
        name="Vector Store",
        normalized_name="vector_store",
        entity_type="component",
        aliases=("Vector Store", "vector store", "向量库", "向量数据库"),
    ),
    EntityPattern(
        name="Chroma",
        normalized_name="chroma",
        entity_type="database",
        aliases=("Chroma", "chromadb", "ChromaDB"),
    ),
    EntityPattern(
        name="GraphRAG",
        normalized_name="graphrag",
        entity_type="concept",
        aliases=("GraphRAG", "graph rag", "图谱增强检索"),
    ),
    EntityPattern(
        name="Neo4j",
        normalized_name="neo4j",
        entity_type="database",
        aliases=("Neo4j", "neo4j"),
    ),
)


def _stable_hash(text: str, length: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _document_id(source: str) -> str:
    return f"Document:{source}"


def _entity_id(pattern: EntityPattern) -> str:
    return f"Entity:{pattern.entity_type}:{pattern.normalized_name}"


def _relation_id(
    relation_type: str,
    source_id: str,
    target_id: str,
    scope: str | None = None,
) -> str:
    raw = f"{relation_type}:{source_id}->{target_id}:{scope or ''}"
    return f"Relation:{relation_type}:{_stable_hash(raw, length=16)}"


def _find_alias(content: str, aliases: tuple[str, ...]) -> str | None:
    lower_content = content.lower()

    for alias in sorted(aliases, key=len, reverse=True):
        if alias.lower() in lower_content:
            return alias

    return None


def _chunk_to_dict(raw_chunk: dict[str, Any]) -> dict[str, Any]:
    content = raw_chunk.get("content", "")
    preview = raw_chunk.get("preview") or content[:120]

    return {
        "chunk_id": raw_chunk["chunk_id"],
        "source": raw_chunk["source"],
        "index": raw_chunk["index"],
        "content": content,
        "preview": preview,
        "content_length": raw_chunk.get("content_length", len(content)),
    }


def _build_documents(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for chunk in chunks:
        grouped.setdefault(chunk["source"], []).append(chunk)

    documents = []

    for source in sorted(grouped):
        source_chunks = sorted(grouped[source], key=lambda item: item["index"])
        joined_content = "\n\n".join(chunk["content"] for chunk in source_chunks)

        documents.append(
            {
                "document_id": _document_id(source),
                "source": source,
                "title": source.rsplit("/", maxsplit=1)[-1],
                "content_hash": _stable_hash(joined_content),
                "chunk_count": len(source_chunks),
            }
        )

    return documents


def extract_entities_from_chunks(chunks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    entities_by_id: dict[str, dict[str, Any]] = {}
    mentions_by_chunk: dict[str, list[dict[str, Any]]] = {}

    for chunk in chunks:
        chunk_mentions: list[dict[str, Any]] = []
        content = chunk["content"]

        for pattern in ENTITY_PATTERNS:
            matched_alias = _find_alias(content=content, aliases=pattern.aliases)
            if matched_alias is None:
                continue

            entity_id = _entity_id(pattern)

            entities_by_id.setdefault(
                entity_id,
                {
                    "entity_id": entity_id,
                    "name": pattern.name,
                    "normalized_name": pattern.normalized_name,
                    "type": pattern.entity_type,
                    "aliases": list(pattern.aliases),
                },
            )

            chunk_mentions.append(
                {
                    "entity_id": entity_id,
                    "surface_text": matched_alias,
                    "confidence": 1.0,
                }
            )

        mentions_by_chunk[chunk["chunk_id"]] = sorted(
            chunk_mentions,
            key=lambda item: item["entity_id"],
        )

    entities = sorted(
        entities_by_id.values(),
        key=lambda item: (item["type"], item["normalized_name"]),
    )

    return entities, mentions_by_chunk


def extract_relations_from_chunks(
    documents: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    mentions_by_chunk: dict[str, list[dict[str, Any]]],
    include_related_entities: bool = True,
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []

    document_source_to_id = {
        document["source"]: document["document_id"]
        for document in documents
    }

    sorted_chunks = sorted(chunks, key=lambda item: (item["source"], item["index"]))

    for chunk in sorted_chunks:
        document_id = document_source_to_id[chunk["source"]]
        chunk_id = chunk["chunk_id"]

        relations.append(
            {
                "relation_id": _relation_id("HAS_CHUNK", document_id, chunk_id),
                "type": "HAS_CHUNK",
                "source_id": document_id,
                "target_id": chunk_id,
                "properties": {
                    "chunk_index": chunk["index"],
                },
            }
        )

    for _, source_chunks_iter in itertools.groupby(sorted_chunks, key=lambda item: item["source"]):
        source_chunks = list(source_chunks_iter)

        for previous, current in zip(source_chunks, source_chunks[1:]):
            relations.append(
                {
                    "relation_id": _relation_id(
                        "NEXT_CHUNK",
                        previous["chunk_id"],
                        current["chunk_id"],
                    ),
                    "type": "NEXT_CHUNK",
                    "source_id": previous["chunk_id"],
                    "target_id": current["chunk_id"],
                    "properties": {
                        "source": current["source"],
                    },
                }
            )

    for chunk in sorted_chunks:
        chunk_id = chunk["chunk_id"]

        for mention in mentions_by_chunk.get(chunk_id, []):
            relations.append(
                {
                    "relation_id": _relation_id(
                        "MENTIONS",
                        chunk_id,
                        mention["entity_id"],
                        scope=mention["surface_text"],
                    ),
                    "type": "MENTIONS",
                    "source_id": chunk_id,
                    "target_id": mention["entity_id"],
                    "properties": {
                        "surface_text": mention["surface_text"],
                        "confidence": mention["confidence"],
                    },
                }
            )

    if include_related_entities:
        for chunk in sorted_chunks:
            chunk_id = chunk["chunk_id"]
            entity_ids = sorted(
                {
                    mention["entity_id"]
                    for mention in mentions_by_chunk.get(chunk_id, [])
                }
            )

            for source_id, target_id in itertools.combinations(entity_ids, 2):
                relations.append(
                    {
                        "relation_id": _relation_id(
                            "RELATED_TO",
                            source_id,
                            target_id,
                            scope=chunk_id,
                        ),
                        "type": "RELATED_TO",
                        "source_id": source_id,
                        "target_id": target_id,
                        "properties": {
                            "relation_type": "co_occurs_in_chunk",
                            "confidence": 0.8,
                            "source": chunk_id,
                        },
                    }
                )

    return relations


def extract_graph_items(
    source_filter: str | None = "agent_basics",
    max_chars: int = 300,
    include_related_entities: bool = True,
) -> dict[str, Any]:
    raw_chunks = load_knowledge_chunks(
        source_filter=source_filter,
        max_chars=max_chars,
    )

    chunks = [_chunk_to_dict(chunk) for chunk in raw_chunks]
    documents = _build_documents(chunks)
    entities, mentions_by_chunk = extract_entities_from_chunks(chunks)

    relations = extract_relations_from_chunks(
        documents=documents,
        chunks=chunks,
        mentions_by_chunk=mentions_by_chunk,
        include_related_entities=include_related_entities,
    )

    relation_type_counts: dict[str, int] = {}

    for relation in relations:
        relation_type_counts[relation["type"]] = relation_type_counts.get(relation["type"], 0) + 1

    entity_type_counts: dict[str, int] = {}

    for entity in entities:
        entity_type_counts[entity["type"]] = entity_type_counts.get(entity["type"], 0) + 1

    return {
        "source_filter": source_filter,
        "max_chars": max_chars,
        "include_related_entities": include_related_entities,
        "documents": documents,
        "chunks": chunks,
        "entities": entities,
        "relations": relations,
        "counts": {
            "documents": len(documents),
            "chunks": len(chunks),
            "entities": len(entities),
            "relations": len(relations),
            "entity_types": entity_type_counts,
            "relation_types": relation_type_counts,
        },
    }
