from src.app.graph.schema import (
    GRAPH_CONSTRAINTS,
    GRAPH_INDEXES,
    get_graph_schema,
    get_graph_schema_summary,
)


def test_graph_schema_contains_core_labels_and_relationships():
    schema = get_graph_schema()

    assert schema["schema_version"] == "day42_graph_schema_v1"

    assert "Document" in schema["node_labels"]
    assert "Chunk" in schema["node_labels"]
    assert "Entity" in schema["node_labels"]

    assert "HAS_CHUNK" in schema["relation_types"]
    assert "NEXT_CHUNK" in schema["relation_types"]
    assert "MENTIONS" in schema["relation_types"]
    assert "RELATED_TO" in schema["relation_types"]


def test_graph_schema_contains_required_properties():
    schema = get_graph_schema()

    assert "source" in schema["node_properties"]["Document"]
    assert "chunk_id" in schema["node_properties"]["Chunk"]
    assert "content" in schema["node_properties"]["Chunk"]
    assert "normalized_name" in schema["node_properties"]["Entity"]
    assert "type" in schema["node_properties"]["Entity"]


def test_graph_schema_contains_constraints_and_indexes():
    assert any("Document" in item and "source" in item for item in GRAPH_CONSTRAINTS)
    assert any("Chunk" in item and "chunk_id" in item for item in GRAPH_CONSTRAINTS)
    assert any("Entity" in item and "normalized_name" in item for item in GRAPH_CONSTRAINTS)

    assert any("Chunk" in item for item in GRAPH_INDEXES)
    assert any("Entity" in item for item in GRAPH_INDEXES)


def test_graph_schema_summary_is_stable():
    summary = get_graph_schema_summary()

    assert summary["schema_version"] == "day42_graph_schema_v1"
    assert summary["node_label_count"] == 3
    assert summary["relation_type_count"] == 4
    assert summary["constraint_count"] >= 3
    assert summary["index_count"] >= 3
