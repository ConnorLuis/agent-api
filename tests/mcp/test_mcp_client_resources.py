import asyncio

from src.app.mcp_integration.client import (
    extract_json_content,
    extract_resource_json,
    extract_resource_text,
    call_mcp_tool,
    list_mcp_resources,
    read_mcp_resource,
)


EXPECTED_DAY68_RESOURCES = {
    "agent-api://mcp/tool-registry",
    "agent-api://mcp/marketplace",
    "agent-api://graph/schema",
    "agent-api://docs/graphrag",
    "agent-api://docs/multi-agent",
    "agent-api://docs/mcp-plan",
    "agent-api://mcp/marketplace-discovery",
    "agent-api://mcp/security-report",
}


def test_real_mcp_stdio_client_can_list_agent_api_resources():
    resources = asyncio.run(list_mcp_resources())

    assert set(resources) == EXPECTED_DAY68_RESOURCES


def test_real_mcp_stdio_client_can_read_tool_registry_resource():
    result = asyncio.run(
        read_mcp_resource(uri="agent-api://mcp/tool-registry")
    )

    payload = extract_resource_json(result)

    assert payload["resource"] == "agent-api://mcp/tool-registry"
    assert payload["registry"]["tool_count"] == 8
    assert "answer_verify" in payload["registry"]["tool_names"]
    assert "rag_backend_eval" in payload["registry"]["tool_names"]
    assert "mcp_registry_summary" in payload["registry"]["tool_names"]


def test_real_mcp_stdio_client_can_read_graph_schema_resource():
    result = asyncio.run(
        read_mcp_resource(uri="agent-api://graph/schema")
    )

    payload = extract_resource_json(result)
    schema_text = extract_resource_text(result)

    assert payload["resource"] == "agent-api://graph/schema"
    assert "node_labels" in payload["schema"]
    assert "HAS_CHUNK" in schema_text
    assert "MENTIONS" in schema_text


def test_real_mcp_stdio_client_can_read_multi_agent_docs_resource():
    result = asyncio.run(
        read_mcp_resource(uri="agent-api://docs/multi-agent")
    )

    text = extract_resource_text(result)

    assert "# Multi-Agent Architecture" in text
    assert "/multi-agent/eval-debug" in text
    assert "graph_fusion remains a non-default retrieval backend." in text


def test_real_mcp_stdio_client_can_call_day68_registry_summary_tool():
    result = asyncio.run(
        call_mcp_tool(
            tool_name="mcp_registry_summary",
            arguments={
                "trace_id": "test-real-mcp-client-registry-summary",
            },
        )
    )

    payload = extract_json_content(result)

    assert payload["tool_name"] == "mcp_registry_summary"
    assert payload["trace_id"] == "test-real-mcp-client-registry-summary"
    assert payload["summary"]["tool_count"] == 8
    assert payload["summary"]["external_servers_enabled_by_default"] == []
