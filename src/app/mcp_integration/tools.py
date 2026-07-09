from __future__ import annotations

from typing import Any

from src.app.graph.fusion import run_graph_vector_fusion_debug
from src.app.mcp_integration.permissions import (
    MCPPrincipal,
    get_ci_safe_mcp_principal,
    authorize_mcp_tool,
    serialize_authorization_decision,
)
from src.app.mcp_integration.registry import get_mcp_tool_spec
from src.app.multi_agent.evaluation import run_deterministic_multi_agent_eval_trace
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.retrieval_backend_modules.normalization import DEFAULT_RETRIEVAL_BACKEND


MCP_SERVER_NAME = "agent-api-mcp"
MCP_SERVER_VERSION = "day67_mcp_foundation_v1"


def _build_mcp_boundary(
    *,
    tool_name: str,
    ci_safe: bool = True,
    llm_used: bool = False,
    graph_fusion_default_changed: bool = False,
) -> dict[str, Any]:
    return {
        "server": MCP_SERVER_NAME,
        "server_version": MCP_SERVER_VERSION,
        "tool_name": tool_name,
        "ci_safe": ci_safe,
        "llm_used": llm_used,
        "default_retrieval_backend": DEFAULT_RETRIEVAL_BACKEND,
        "graph_fusion_default_changed": graph_fusion_default_changed,
        "protocol_boundary": "mcp_tool_adapter",
    }


def _build_denied_response(
    *,
    tool_name: str,
    trace_id: str,
    authorization: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": False,
        "authorization": authorization,
        "result": None,
        "summary": {
            "status": "denied",
            "reason": authorization.get("reason"),
        },
        "mcp_boundary": _build_mcp_boundary(tool_name=tool_name),
    }


def run_agentic_rag_query_mcp_tool(
    *,
    query: str,
    top_k: int = 3,
    source_filter: str | None = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = DEFAULT_RETRIEVAL_BACKEND,
    embedding_provider: str = "deterministic",
    embedding_model: str | None = None,
    rebuild_index: bool = True,
    graph_dry_run: bool = True,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
    trace_id: str = "mcp-agentic-rag-trace",
    principal: MCPPrincipal | None = None,
) -> dict[str, Any]:
    tool_name = "agentic_rag_query"
    tool_spec = get_mcp_tool_spec(tool_name)
    principal = principal or get_ci_safe_mcp_principal()

    requested_live_neo4j = retrieval_backend == "graph_fusion" and not graph_dry_run

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=tool_spec,
        requested_live_neo4j=requested_live_neo4j,
        requested_network=False,
        requested_write=False,
    )
    authorization = serialize_authorization_decision(decision)

    if not decision.allowed:
        return _build_denied_response(
            tool_name=tool_name,
            trace_id=trace_id,
            authorization=authorization,
        )

    effective_graph_dry_run = graph_dry_run or decision.enforced_dry_run

    result = invoke_agentic_rag(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        retrieval_backend=retrieval_backend,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        rebuild_index=rebuild_index,
        graph_dry_run=effective_graph_dry_run,
        fusion_graph_weight=fusion_graph_weight,
        fusion_vector_weight=fusion_vector_weight,
        graph_chunk_limit=graph_chunk_limit,
        related_entity_limit=related_entity_limit,
    )

    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": True,
        "authorization": authorization,
        "result": result,
        "summary": {
            "status": "completed",
            "query": query,
            "retrieval_backend": result.get("retrieval_backend"),
            "retrieval_needed": result.get("retrieval_needed"),
            "citation_count": len(result.get("citations", [])),
            "retrieval_result_count": len(result.get("retrieval_results", [])),
            "graph_dry_run": effective_graph_dry_run,
        },
        "mcp_boundary": _build_mcp_boundary(
            tool_name=tool_name,
            ci_safe=True,
            llm_used=False,
            graph_fusion_default_changed=DEFAULT_RETRIEVAL_BACKEND != "hybrid",
        ),
    }


def run_graph_fusion_retrieve_mcp_tool(
    *,
    query: str,
    top_k: int = 3,
    source_filter: str | None = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    hybrid_keyword_weight: float = 0.6,
    hybrid_vector_weight: float = 0.4,
    fusion_graph_weight: float = 0.5,
    fusion_vector_weight: float = 0.5,
    graph_chunk_limit: int = 5,
    related_entity_limit: int = 10,
    graph_dry_run: bool = True,
    trace_id: str = "mcp-graph-fusion-trace",
    principal: MCPPrincipal | None = None,
) -> dict[str, Any]:
    tool_name = "graph_fusion_retrieve"
    tool_spec = get_mcp_tool_spec(tool_name)
    principal = principal or get_ci_safe_mcp_principal()

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=tool_spec,
        requested_live_neo4j=not graph_dry_run,
        requested_network=False,
        requested_write=False,
    )
    authorization = serialize_authorization_decision(decision)

    if not decision.allowed:
        return _build_denied_response(
            tool_name=tool_name,
            trace_id=trace_id,
            authorization=authorization,
        )

    effective_graph_dry_run = graph_dry_run or decision.enforced_dry_run

    result = run_graph_vector_fusion_debug(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        hybrid_keyword_weight=hybrid_keyword_weight,
        hybrid_vector_weight=hybrid_vector_weight,
        fusion_graph_weight=fusion_graph_weight,
        fusion_vector_weight=fusion_vector_weight,
        graph_chunk_limit=graph_chunk_limit,
        related_entity_limit=related_entity_limit,
        graph_dry_run=effective_graph_dry_run,
    )

    fusion = result.get("fusion", {}) or {}
    source_counts = fusion.get("source_counts", {}) or {}
    graph_retrieval = result.get("graph_retrieval", {}) or {}
    graph_execution = graph_retrieval.get("execution", {}) or {}
    graph_status = (
            graph_execution.get("status")
            or graph_retrieval.get("status")
            or graph_retrieval.get("execution_status")
    )

    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": True,
        "authorization": authorization,
        "result": result,
        "summary": {
            "status": "completed",
            "graph_status": graph_status,
            "query": query,
            "graph_dry_run": effective_graph_dry_run,
            "fusion_result_count": fusion.get("result_count"),
            "graph_only_count": source_counts.get("graph_only"),
            "vector_only_count": source_counts.get("vector_only"),
            "graph_and_vector_count": source_counts.get("graph_and_vector"),
        },
        "mcp_boundary": _build_mcp_boundary(
            tool_name=tool_name,
            ci_safe=True,
            llm_used=False,
            graph_fusion_default_changed=DEFAULT_RETRIEVAL_BACKEND != "hybrid",
        ),
    }


def run_multi_agent_eval_trace_mcp_tool(
    *,
    task: str,
    thread_id: str = "mcp-multi-agent-thread",
    trace_id: str = "mcp-multi-agent-trace",
    metadata: dict[str, Any] | None = None,
    principal: MCPPrincipal | None = None,
) -> dict[str, Any]:
    tool_name = "multi_agent_eval_trace"
    tool_spec = get_mcp_tool_spec(tool_name)
    principal = principal or get_ci_safe_mcp_principal()

    decision = authorize_mcp_tool(
        principal=principal,
        tool_spec=tool_spec,
        requested_live_neo4j=False,
        requested_network=False,
        requested_write=False,
    )
    authorization = serialize_authorization_decision(decision)

    if not decision.allowed:
        return _build_denied_response(
            tool_name=tool_name,
            trace_id=trace_id,
            authorization=authorization,
        )

    result = run_deterministic_multi_agent_eval_trace(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata or {
            "source": "mcp",
            "mcp_server": MCP_SERVER_NAME,
            "mcp_server_version": MCP_SERVER_VERSION,
        },
    )

    eval_report = result.get("eval_report", {}) or {}
    trace_report = result.get("trace_report", {}) or {}

    return {
        "tool_name": tool_name,
        "trace_id": trace_id,
        "allowed": True,
        "authorization": authorization,
        "result": result,
        "summary": {
            "status": "completed",
            "task": task,
            "eval_pass": eval_report.get("eval_pass"),
            "passed_check_count": eval_report.get("passed_check_count"),
            "failed_check_count": eval_report.get("failed_check_count"),
            "stream_event_count": trace_report.get("stream_event_count"),
        },
        "mcp_boundary": _build_mcp_boundary(
            tool_name=tool_name,
            ci_safe=True,
            llm_used=False,
            graph_fusion_default_changed=DEFAULT_RETRIEVAL_BACKEND != "hybrid",
        ),
    }
