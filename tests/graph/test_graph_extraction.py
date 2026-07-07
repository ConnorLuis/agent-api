from src.app.graph.extraction import extract_graph_items


def _names(entities):
    return {entity["name"] for entity in entities}


def _relation_types(relations):
    return {relation["type"] for relation in relations}


def test_extract_graph_items_returns_documents_chunks_entities_and_relations():
    result = extract_graph_items(source_filter="agent_basics", max_chars=300)

    assert result["source_filter"] == "agent_basics"
    assert result["max_chars"] == 300
    assert result["include_related_entities"] is True

    assert result["counts"]["documents"] == len(result["documents"])
    assert result["counts"]["chunks"] == len(result["chunks"])
    assert result["counts"]["entities"] == len(result["entities"])
    assert result["counts"]["relations"] == len(result["relations"])

    assert result["counts"]["documents"] >= 1
    assert result["counts"]["chunks"] >= 1
    assert result["counts"]["entities"] >= 3
    assert result["counts"]["relations"] >= result["counts"]["chunks"]


def test_extract_graph_items_finds_core_agent_rag_entities():
    result = extract_graph_items(source_filter="agent_basics", max_chars=300)

    names = _names(result["entities"])

    assert "Agent" in names
    assert "RAG" in names
    assert "LangGraph" in names
    assert "Tool" in names


def test_extract_graph_items_builds_schema_aligned_relation_types():
    result = extract_graph_items(source_filter="agent_basics", max_chars=300)

    types = _relation_types(result["relations"])

    assert "HAS_CHUNK" in types
    assert "NEXT_CHUNK" in types
    assert "MENTIONS" in types
    assert "RELATED_TO" in types


def test_extract_graph_items_can_disable_related_entity_edges():
    result = extract_graph_items(
        source_filter="agent_basics",
        max_chars=300,
        include_related_entities=False,
    )

    types = _relation_types(result["relations"])

    assert "HAS_CHUNK" in types
    assert "NEXT_CHUNK" in types
    assert "MENTIONS" in types
    assert "RELATED_TO" not in types


def test_extract_graph_items_uses_stable_ids():
    result = extract_graph_items(source_filter="agent_basics", max_chars=300)

    document = result["documents"][0]
    entity = next(item for item in result["entities"] if item["name"] == "RAG")
    relation = result["relations"][0]

    assert document["document_id"].startswith("Document:")
    assert entity["entity_id"] == "Entity:concept:rag"
    assert relation["relation_id"].startswith("Relation:")
    assert relation["source_id"]
    assert relation["target_id"]
