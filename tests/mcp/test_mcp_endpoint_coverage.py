import asyncio

from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
    extract_resource_json,
)
from src.app.mcp_integration.endpoint_coverage import (
    build_mcp_endpoint_coverage_report,
    list_mcp_endpoint_coverage_specs,
)
from src.app.mcp_integration.permissions import get_ci_safe_mcp_principal


def test_endpoint_coverage_report_contains_day71_target_domains_and_endpoints():
    report = build_mcp_endpoint_coverage_report()

    assert report["report_version"] == "day71_mcp_endpoint_coverage_report_v1"
    assert report["scope"]["milestone"] == "Day71"
    assert report["scope"]["rest_endpoints_preserved"] is True
    assert report["scope"]["mcp_is_additive_protocol_layer"] is True
    assert report["scope"]["main_agent_default_path_changed"] is False
    assert report["scope"]["graph_fusion_default_changed"] is False

    summary = report["summary"]
    assert summary["endpoint_count"] == 14
    assert summary["ci_safe_endpoint_count"] == 14
    assert summary["dry_run_default_endpoint_count"] == 14
    assert summary["domain_counts"] == {
        "rag": 5,
        "graph": 4,
        "multi_agent": 3,
        "observability": 2,
    }

    endpoint_ids = {item["endpoint_id"] for item in report["coverage"]}
    assert {
        "rag_agentic_debug",
        "rag_agentic_stream",
        "rag_eval_debug",
        "rag_backend_eval_debug",
        "rag_answer_verify_debug",
        "graph_schema_debug",
        "graph_extract_debug",
        "graph_retrieval_debug",
        "graph_fusion_debug",
        "multi_agent_supervisor_debug",
        "multi_agent_stream",
        "multi_agent_eval_debug",
        "observability_traces",
        "observability_trace_detail",
    } == endpoint_ids


def test_endpoint_coverage_report_records_existing_and_planned_mcp_mappings():
    report = build_mcp_endpoint_coverage_report()

    by_id = {item["endpoint_id"]: item for item in report["coverage"]}

    assert by_id["rag_agentic_debug"]["mapped_mcp_tools"] == ["agentic_rag_query"]
    assert by_id["rag_backend_eval_debug"]["mapped_mcp_tools"] == ["rag_backend_eval"]
    assert by_id["rag_answer_verify_debug"]["mapped_mcp_tools"] == ["answer_verify"]
    assert by_id["graph_schema_debug"]["mapped_mcp_resources"] == [
        "agent-api://graph/schema"
    ]
    assert by_id["graph_fusion_debug"]["mapped_mcp_tools"] == [
        "graph_fusion_retrieve"
    ]
    assert by_id["multi_agent_eval_debug"]["mapped_mcp_tools"] == [
        "multi_agent_eval_trace"
    ]

    assert by_id["observability_traces"]["mapped_mcp_tools"] == [
        "mcp_endpoint_probe"
    ]
    assert by_id["observability_trace_detail"]["mapped_mcp_tools"] == [
        "mcp_endpoint_probe"
    ]

    planned_ids = set(report["summary"]["planned_endpoint_ids"])
    assert {
        "rag_agentic_stream",
        "graph_extract_debug",
        "graph_retrieval_debug",
        "multi_agent_supervisor_debug",
        "multi_agent_stream",
    }.issubset(planned_ids)


def test_endpoint_coverage_specs_are_read_only_and_ci_safe():
    specs = list_mcp_endpoint_coverage_specs()

    assert len(specs) == 14
    assert all(spec.ci_safe for spec in specs)
    assert all(spec.dry_run_default for spec in specs)

    for spec in specs:
        assert "read_only" in spec.risk_flags
        assert spec.method in {"GET", "POST"}
        assert spec.path.startswith("/")


def test_mcp_endpoint_coverage_tool_returns_security_wrapped_report():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.call_tool(
            tool_name="mcp_endpoint_coverage_report",
            arguments={
                "trace_id": "test-day71-endpoint-coverage-tool",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_endpoint_coverage_report"
    assert payload["trace_id"] == "test-day71-endpoint-coverage-tool"
    assert payload["summary"]["endpoint_count"] == 14
    assert payload["summary"]["ci_safe"] is True
    assert payload["summary"]["rest_endpoint_behavior_changed"] is False
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False
    assert payload["security_decision"]["tool_name"] == "mcp_endpoint_coverage_report"
    assert payload["security_decision"]["allowed"] is True
    assert payload["security_audit_trace"]["event_type"] == "mcp_security_decision"


def test_mcp_endpoint_coverage_resource_returns_report():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    result = asyncio.run(
        wrapper.read_resource(uri="agent-api://mcp/endpoint-coverage")
    )

    payload = extract_resource_json(result)

    assert payload["resource"] == "agent-api://mcp/endpoint-coverage"
    report = payload["endpoint_coverage_report"]
    assert report["summary"]["endpoint_count"] == 14
    assert report["summary"]["domain_counts"]["rag"] == 5
    assert report["summary"]["domain_counts"]["graph"] == 4
    assert report["summary"]["domain_counts"]["multi_agent"] == 3
    assert report["summary"]["domain_counts"]["observability"] == 2
    assert report["safety"]["rest_endpoint_behavior_changed"] is False
