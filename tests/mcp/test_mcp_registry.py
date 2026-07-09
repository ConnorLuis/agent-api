from src.app.mcp_integration.registry import (
    get_mcp_tool_spec,
    list_mcp_tool_names,
    list_mcp_tool_specs,
    summarize_mcp_tool_registry,
)


EXPECTED_DAY68_TOOL_NAMES = [
    "agentic_rag_query",
    "graph_fusion_retrieve",
    "multi_agent_eval_trace",
    "answer_verify",
    "rag_backend_eval",
    "mcp_registry_summary",
]


def test_mcp_registry_contains_day68_core_tools():
    tool_names = list_mcp_tool_names()

    assert tool_names == EXPECTED_DAY68_TOOL_NAMES


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


def test_mcp_registry_records_day68_verification_and_eval_tools():
    answer_verify = get_mcp_tool_spec("answer_verify")
    rag_backend_eval = get_mcp_tool_spec("rag_backend_eval")
    registry_summary = get_mcp_tool_spec("mcp_registry_summary")

    assert answer_verify.category == "verification"
    assert answer_verify.required_scopes == ("mcp:verification:read",)
    assert answer_verify.requires_neo4j is True

    assert rag_backend_eval.category == "evaluation"
    assert rag_backend_eval.required_scopes == ("mcp:evaluation:read",)
    assert rag_backend_eval.requires_neo4j is True

    assert registry_summary.category == "system"
    assert registry_summary.required_scopes == ("mcp:system:read",)
    assert registry_summary.requires_neo4j is False


def test_mcp_registry_summary_is_stable():
    summary = summarize_mcp_tool_registry()

    assert summary["tool_count"] == 6
    assert summary["tool_names"] == EXPECTED_DAY68_TOOL_NAMES
    assert summary["categories"] == [
        "evaluation",
        "graphrag",
        "multi_agent",
        "rag",
        "system",
        "verification",
    ]
    assert summary["requires_neo4j_tool_names"] == [
        "graph_fusion_retrieve",
        "answer_verify",
        "rag_backend_eval",
    ]
