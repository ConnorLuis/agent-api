from src.app.graph.extraction import extract_graph_items
from src.app.graph.ingestion import (
    RELATION_UPSERT_QUERIES,
    build_graph_ingestion_plan,
    get_graph_ingestion_cypher_templates,
    run_graph_ingestion_debug,
)


def test_build_graph_ingestion_plan_counts_nodes_and_relationships():
    extraction = extract_graph_items(source_filter="agent_basics", max_chars=300)

    plan = build_graph_ingestion_plan(extraction=extraction)

    assert plan["apply_schema"] is True
    assert plan["schema_statement_count"] >= 6

    assert plan["node_counts"]["Document"] == 1
    assert plan["node_counts"]["Chunk"] == extraction["counts"]["chunks"]
    assert plan["node_counts"]["Entity"] == extraction["counts"]["entities"]

    assert plan["relationship_counts"]["HAS_CHUNK"] == extraction["counts"]["chunks"]
    assert plan["relationship_counts"]["MENTIONS"] >= 1
    assert plan["total_node_upserts"] == (
        plan["node_counts"]["Document"]
        + plan["node_counts"]["Chunk"]
        + plan["node_counts"]["Entity"]
    )
    assert plan["total_relationship_upserts"] == extraction["counts"]["relations"]


def test_build_graph_ingestion_plan_can_skip_schema_application():
    extraction = extract_graph_items(source_filter="agent_basics", max_chars=300)

    plan = build_graph_ingestion_plan(
        extraction=extraction,
        apply_schema=False,
    )

    assert plan["apply_schema"] is False
    assert plan["schema_statement_count"] == 0
    assert plan["schema_statements"] == []


def test_graph_ingestion_cypher_templates_cover_schema_relation_types():
    templates = get_graph_ingestion_cypher_templates()

    assert "Document" in templates["node_upsert_queries"]
    assert "Chunk" in templates["node_upsert_queries"]
    assert "Entity" in templates["node_upsert_queries"]

    assert set(RELATION_UPSERT_QUERIES) == {
        "HAS_CHUNK",
        "NEXT_CHUNK",
        "MENTIONS",
        "RELATED_TO",
    }

    for relation_type in RELATION_UPSERT_QUERIES:
        assert relation_type in templates["relation_upsert_queries"]


def test_run_graph_ingestion_debug_defaults_to_dry_run():
    result = run_graph_ingestion_debug(
        source_filter="agent_basics",
        max_chars=300,
        include_related_entities=True,
    )

    assert result["dry_run"] is True
    assert result["apply_schema"] is True
    assert result["execution"]["ok"] is None
    assert result["execution"]["status"] == "dry_run"

    assert result["extraction_counts"]["documents"] == 1
    assert result["extraction_counts"]["chunks"] >= 1
    assert result["extraction_counts"]["entities"] >= 1
    assert result["plan"]["total_node_upserts"] >= 1
    assert result["plan"]["total_relationship_upserts"] >= 1
