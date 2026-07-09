from src.app.mcp_integration.registry import (
    get_mcp_tool_spec,
    list_mcp_tool_names,
    list_mcp_tool_specs,
    summarize_mcp_tool_registry,
)


def test_mcp_registry_contains_day67_core_tools():
    tool_names = list_mcp_tool_names()

    assert tool_names == [
        "agentic_rag_query",
        "graph_fusion_retrieve",
        "multi_agent_eval_trace",
    ]


def test_mcp_registry_core_tools_are_read_only_and_ci_safe():
    specs = list_mcp_tool_specs()

    assert all(spec.read_only for spec in specs)
    assert all(spec.default_ci_safe for spec in specs)
    assert all(not spec.requires_network for spec in specs)


def test_mcp_registry_records_graph_tool_neo4j_boundary():
    graph_tool = get_mcp_tool_spec("graph_fusion_retrieve")

    assert graph_tool.category == "graphrag"
    assert graph_tool.requires_neo4j is True
    assert graph_tool.risk_level == "medium"
    assert graph_tool.required_scopes == ("mcp:graph:read",)


def test_mcp_registry_summary_is_stable():
    summary = summarize_mcp_tool_registry()

    assert summary["tool_count"] == 3
    assert summary["tool_names"] == [
        "agentic_rag_query",
        "graph_fusion_retrieve",
        "multi_agent_eval_trace",
    ]
    assert summary["categories"] == ["graphrag", "multi_agent", "rag"]
    assert summary["requires_neo4j_tool_names"] == ["graph_fusion_retrieve"]
