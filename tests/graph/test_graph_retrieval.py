from src.app.graph.retrieval import (
    build_graph_retrieval_plan,
    extract_query_entity_matches,
    get_graph_retrieval_cypher_templates,
    run_graph_retrieval_debug,
)


def _names(matches):
    return {match["name"] for match in matches}


def test_extract_query_entity_matches_finds_known_entities():
    matches = extract_query_entity_matches("请解释 RAG 和 LangGraph 的关系")

    names = _names(matches)

    assert "RAG" in names
    assert "LangGraph" in names

    rag = next(match for match in matches if match["name"] == "RAG")
    langgraph = next(match for match in matches if match["name"] == "LangGraph")

    assert rag["entity_id"] == "Entity:concept:rag"
    assert langgraph["entity_id"] == "Entity:framework:langgraph"


def test_extract_query_entity_matches_supports_chinese_aliases():
    matches = extract_query_entity_matches("智能体如何使用工具和短期记忆？")

    names = _names(matches)

    assert "Agent" in names
    assert "Tool" in names
    assert "Memory" in names


def test_build_graph_retrieval_plan_is_ci_safe():
    plan = build_graph_retrieval_plan(
        query="RAG 是什么？",
        chunk_limit=3,
        related_entity_limit=8,
    )

    assert plan["query"] == "RAG 是什么？"
    assert plan["chunk_limit"] == 3
    assert plan["related_entity_limit"] == 8
    assert plan["dry_run_safe"] is True
    assert "Entity:concept:rag" in plan["matched_entity_ids"]
    assert plan["cypher_query_keys"] == [
        "matched_entities",
        "mentioned_chunks",
        "related_entities",
    ]


def test_graph_retrieval_cypher_templates_cover_required_queries():
    templates = get_graph_retrieval_cypher_templates()

    assert "matched_entities" in templates
    assert "mentioned_chunks" in templates
    assert "related_entities" in templates

    assert "MATCH (e:Entity)" in templates["matched_entities"]
    assert "MENTIONS" in templates["mentioned_chunks"]
    assert "RELATED_TO" in templates["related_entities"]


def test_run_graph_retrieval_debug_defaults_to_dry_run():
    result = run_graph_retrieval_debug(
        query="RAG 是什么？",
        chunk_limit=5,
        related_entity_limit=10,
    )

    assert result["dry_run"] is True
    assert result["query"] == "RAG 是什么？"
    assert result["execution"]["ok"] is None
    assert result["execution"]["status"] == "dry_run"

    assert "Entity:concept:rag" in result["plan"]["matched_entity_ids"]
    assert result["execution"]["chunks"] == []
    assert result["execution"]["related_entities"] == []


def test_run_graph_retrieval_debug_handles_no_query_entity_match():
    result = run_graph_retrieval_debug(
        query="今天天气怎么样？",
        dry_run=True,
    )

    assert result["query_entity_matches"] == []
    assert result["plan"]["matched_entity_ids"] == []
    assert result["execution"]["ok"] is True
    assert result["execution"]["status"] == "no_query_entity_match"
    assert result["execution"]["counts"]["matched_entities"] == 0
    assert result["execution"]["counts"]["chunks"] == 0
    assert result["execution"]["counts"]["related_entities"] == 0


def test_run_graph_retrieval_debug_can_call_mocked_live_execution(monkeypatch):
    def fake_execute_graph_retrieval(
        query,
        query_entity_matches,
        chunk_limit=5,
        related_entity_limit=10,
    ):
        return {
            "ok": True,
            "status": "retrieved",
            "reason": None,
            "matched_entities": query_entity_matches,
            "chunks": [{"chunk_id": "mock-chunk-1"}],
            "related_entities": [{"entity_id": "mock-related-entity-1"}],
            "counts": {
                "matched_entities": len(query_entity_matches),
                "chunks": 1,
                "related_entities": 1,
            },
        }

    monkeypatch.setattr(
        "src.app.graph.retrieval.execute_graph_retrieval",
        fake_execute_graph_retrieval,
    )

    result = run_graph_retrieval_debug(
        query="RAG 是什么？",
        chunk_limit=5,
        related_entity_limit=10,
        dry_run=False,
    )

    assert result["dry_run"] is False
    assert result["execution"]["ok"] is True
    assert result["execution"]["status"] == "retrieved"
    assert result["execution"]["counts"]["chunks"] == 1
    assert result["execution"]["counts"]["related_entities"] == 1
