import json

from src.app.mcp_integration.server import (
    agentic_rag_query,
    graph_fusion_retrieve,
    multi_agent_eval_trace,
)
from src.app.mcp_integration.tools import (
    run_agentic_rag_query_mcp_tool,
    run_graph_fusion_retrieve_mcp_tool,
    run_multi_agent_eval_trace_mcp_tool,
)


def test_agentic_rag_query_mcp_tool_contract():
    payload = run_agentic_rag_query_mcp_tool(
        query="RAG 是什么？",
        top_k=2,
        trace_id="test-mcp-agentic-rag-001",
    )

    assert payload["tool_name"] == "agentic_rag_query"
    assert payload["trace_id"] == "test-mcp-agentic-rag-001"
    assert payload["allowed"] is True
    assert payload["authorization"]["allowed"] is True
    assert payload["mcp_boundary"]["server"] == "agent-api-mcp"
    assert payload["mcp_boundary"]["protocol_boundary"] == "mcp_tool_adapter"
    assert payload["mcp_boundary"]["default_retrieval_backend"] == "hybrid"
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False

    result = payload["result"]
    assert result["query"] == "RAG 是什么？"
    assert result["retrieval_backend"] == "hybrid"
    assert "final_answer" in result
    assert isinstance(result["retrieval_results"], list)


def test_graph_fusion_mcp_tool_enforces_dry_run_when_live_neo4j_requested():
    payload = run_graph_fusion_retrieve_mcp_tool(
        query="RAG 和 LangGraph 有什么关系？",
        top_k=2,
        graph_dry_run=False,
        trace_id="test-mcp-graph-fusion-001",
    )

    assert payload["tool_name"] == "graph_fusion_retrieve"
    assert payload["allowed"] is True
    assert payload["authorization"]["reason"] == "allowed_with_dry_run_enforced_for_live_neo4j"
    assert payload["authorization"]["enforced_dry_run"] is True
    assert payload["summary"]["graph_dry_run"] is True
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False

    result = payload["result"]
    assert result["query"] == "RAG 和 LangGraph 有什么关系？"
    assert result["graph_dry_run"] is True
    assert payload["summary"]["graph_status"] == "dry_run"


def test_multi_agent_eval_trace_mcp_tool_contract():
    payload = run_multi_agent_eval_trace_mcp_tool(
        task="解释 Multi-Agent Supervisor graph 的执行过程",
        thread_id="test-mcp-multi-agent-thread",
        trace_id="test-mcp-multi-agent-001",
    )

    assert payload["tool_name"] == "multi_agent_eval_trace"
    assert payload["trace_id"] == "test-mcp-multi-agent-001"
    assert payload["allowed"] is True
    assert payload["summary"]["eval_pass"] is True
    assert payload["summary"]["failed_check_count"] == 0
    assert payload["mcp_boundary"]["graph_fusion_default_changed"] is False

    result = payload["result"]
    assert result["eval_report"]["eval_pass"] is True
    assert result["trace_report"]["stream_event_count"] == 29
    assert result["trace_report"]["boundary_flags"]["default_retrieval_backend"] == "hybrid"


def test_fastmcp_server_tool_functions_return_json_text():
    rag_payload = json.loads(
        agentic_rag_query(
            query="RAG 是什么？",
            top_k=1,
            trace_id="test-server-rag-json-001",
        )
    )
    assert rag_payload["tool_name"] == "agentic_rag_query"
    assert rag_payload["allowed"] is True

    graph_payload = json.loads(
        graph_fusion_retrieve(
            query="RAG 和 LangGraph 有什么关系？",
            top_k=1,
            graph_dry_run=True,
            trace_id="test-server-graph-json-001",
        )
    )
    assert graph_payload["tool_name"] == "graph_fusion_retrieve"
    assert graph_payload["allowed"] is True
    assert graph_payload["summary"]["graph_dry_run"] is True

    multi_agent_payload = json.loads(
        multi_agent_eval_trace(
            task="解释 Multi-Agent eval trace",
            trace_id="test-server-multi-agent-json-001",
        )
    )
    assert multi_agent_payload["tool_name"] == "multi_agent_eval_trace"
    assert multi_agent_payload["allowed"] is True
    assert multi_agent_payload["summary"]["eval_pass"] is True
