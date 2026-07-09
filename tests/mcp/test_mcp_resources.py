import json

from src.app.mcp_integration.resources import (
    get_graph_schema_resource,
    get_graphrag_docs_resource,
    get_mcp_marketplace_resource,
    get_mcp_plan_resource,
    get_mcp_tool_registry_resource,
    get_multi_agent_docs_resource,
)


def test_mcp_tool_registry_resource_is_json_text():
    payload = json.loads(get_mcp_tool_registry_resource())

    assert payload["resource"] == "agent-api://mcp/tool-registry"
    assert payload["registry"]["tool_count"] >= 3
    assert "agentic_rag_query" in payload["registry"]["tool_names"]
    assert "graph_fusion_retrieve" in payload["registry"]["tool_names"]
    assert "multi_agent_eval_trace" in payload["registry"]["tool_names"]


def test_mcp_marketplace_resource_is_json_text():
    payload = json.loads(get_mcp_marketplace_resource())

    assert payload["resource"] == "agent-api://mcp/marketplace"
    assert "agent-api-local" in payload["marketplace"]["server_ids"]
    assert "external-filesystem-stdio" in payload["marketplace"]["server_ids"]
    assert "external-memory-stdio" in payload["marketplace"]["server_ids"]
    assert payload["marketplace"]["external_servers_enabled_by_default"] == []


def test_graph_schema_resource_is_json_text():
    payload = json.loads(get_graph_schema_resource())

    assert payload["resource"] == "agent-api://graph/schema"
    assert "schema" in payload
    assert "node_labels" in payload["schema"]
    schema_text = json.dumps(payload["schema"], ensure_ascii=False)
    for relationship_type in ["HAS_CHUNK", "NEXT_CHUNK", "MENTIONS", "RELATED_TO"]:
        assert relationship_type in schema_text


def test_graphrag_docs_resource_reads_markdown():
    text = get_graphrag_docs_resource()

    assert "# GraphRAG" in text or "GraphRAG" in text
    assert "graph_fusion" in text


def test_multi_agent_docs_resource_reads_markdown():
    text = get_multi_agent_docs_resource()

    assert "# Multi-Agent Architecture" in text
    assert "/multi-agent/eval-debug" in text
    assert "graph_fusion remains a non-default retrieval backend." in text


def test_mcp_plan_resource_documents_day68_to_day72():
    text = get_mcp_plan_resource()

    assert "Day67 completed MCP Foundation" in text
    assert "Day68 expands MCP core tools and resources" in text
    assert "Day72" in text
    assert "graph_fusion non-default" in text
