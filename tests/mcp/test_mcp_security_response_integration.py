import asyncio

import src.app.mcp_integration.tools as mcp_tools
from src.app.mcp_integration.client import (
    MCPClientWrapper,
    build_mcp_client_config_from_marketplace,
    extract_json_content,
)
from src.app.mcp_integration.permissions import get_ci_safe_mcp_principal
from src.app.mcp_integration.registry import list_mcp_tool_names


def _run_tool_function_names() -> list[str]:
    return sorted(
        name
        for name, value in vars(mcp_tools).items()
        if name.startswith("run_")
        and name.endswith("_tool")
        and callable(value)
        and getattr(value, "__module__", None) == mcp_tools.__name__
    )


def test_all_mcp_tool_wrappers_are_security_wrapped():
    function_names = _run_tool_function_names()

    assert len(function_names) == 9

    for function_name in function_names:
        tool_func = getattr(mcp_tools, function_name)
        assert getattr(tool_func, "_mcp_security_wrapped", False) is True


def test_mcp_registry_summary_tool_includes_security_decision_and_audit_trace():
    payload = mcp_tools.run_mcp_registry_summary_tool(
        trace_id="test-day70-stage2-registry-summary-security",
    )

    assert payload["tool_name"] == "mcp_registry_summary"
    assert payload["security_decision"]["target_type"] == "tool"
    assert payload["security_decision"]["tool_name"] == "mcp_registry_summary"
    assert payload["security_decision"]["allowed"] is True
    assert payload["security_decision"]["reason"] == "allowed"
    assert payload["security_decision"]["blocked_reasons"] == []
    assert payload["security_audit_trace"]["event_type"] == "mcp_security_decision"
    assert payload["security_audit_trace"]["target_id"] == "mcp_registry_summary"
    assert payload["security_audit_trace"]["policy_version"] == "day70_mcp_security_policy_v1"
    assert payload["security_audit_trace"]["audit_enabled"] is True
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False


def test_mcp_security_report_tool_includes_nested_security_decision_without_recursion():
    payload = mcp_tools.run_mcp_security_report_tool(
        trace_id="test-day70-stage2-security-report-security",
    )

    assert payload["tool_name"] == "mcp_security_report"
    assert payload["summary"]["tool_count"] == 9
    assert payload["security_decision"]["tool_name"] == "mcp_security_report"
    assert payload["security_decision"]["allowed"] is True
    assert payload["security_audit_trace"]["target_id"] == "mcp_security_report"
    assert payload["result"]["summary"]["tool_count"] == 9
    assert payload["result"]["safety"]["audit_trace_enabled"] is True


def test_real_mcp_client_security_response_for_all_registered_tools():
    config = build_mcp_client_config_from_marketplace(
        server_id="agent-api-local",
        principal=get_ci_safe_mcp_principal(),
    )
    wrapper = MCPClientWrapper(config)

    tool_names = asyncio.run(wrapper.list_tools())
    listed_names = sorted(tool_names)

    assert listed_names == sorted(list_mcp_tool_names())

    # Keep this client test focused on lightweight system tools.
    # Core RAG / GraphRAG / Multi-Agent wrappers are covered by the wrapper installation test
    # and existing Day67-Day70 MCP contract tests.
    for tool_name in [
        "mcp_registry_summary",
        "mcp_marketplace_discovery",
        "mcp_security_report",
    ]:
        result = asyncio.run(
            wrapper.call_tool(
                tool_name=tool_name,
                arguments={
                    "trace_id": f"test-day70-stage2-client-{tool_name}",
                },
            )
        )
        payload = extract_json_content(result)

        assert payload["tool_name"] == tool_name
        assert payload["security_decision"]["tool_name"] == tool_name
        assert payload["security_decision"]["allowed"] is True
        assert payload["security_decision"]["reason"] == "allowed"
        assert payload["security_audit_trace"]["event_type"] == "mcp_security_decision"
        assert payload["security_audit_trace"]["target_id"] == tool_name
        assert payload["security_audit_trace"]["policy_version"] == "day70_mcp_security_policy_v1"
        assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False
