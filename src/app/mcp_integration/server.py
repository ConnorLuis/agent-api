from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.app.mcp_integration.resources import (
    get_graph_schema_resource,
    get_graphrag_docs_resource,
    get_mcp_marketplace_resource,
    get_mcp_marketplace_discovery_resource,
    get_mcp_plan_resource,
    get_mcp_tool_registry_resource,
    get_multi_agent_docs_resource,
)
from src.app.mcp_integration.tools import (
    MCP_SERVER_NAME,
    run_agentic_rag_query_mcp_tool,
    run_answer_verify_mcp_tool,
    run_graph_fusion_retrieve_mcp_tool,
    run_mcp_registry_summary_tool,
    run_mcp_marketplace_discovery_tool,
    run_multi_agent_eval_trace_mcp_tool,
    run_rag_backend_eval_mcp_tool,
)


mcp = FastMCP(MCP_SERVER_NAME)


def _to_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def _parse_backends_csv(backends_csv: str) -> list[str]:
    return [
        backend.strip()
        for backend in backends_csv.split(",")
        if backend.strip()
    ]


@mcp.tool()
def agentic_rag_query(
    query: str,
    top_k: int = 3,
    source_filter: str = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = "hybrid",
    embedding_provider: str = "deterministic",
    rebuild_index: bool = True,
    graph_dry_run: bool = True,
    trace_id: str = "mcp-agentic-rag-trace",
) -> str:
    """Run the existing Agentic RAG workflow through the agent-api MCP server."""
    payload = run_agentic_rag_query_mcp_tool(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        retrieval_backend=retrieval_backend,
        embedding_provider=embedding_provider,
        rebuild_index=rebuild_index,
        graph_dry_run=graph_dry_run,
        trace_id=trace_id,
    )
    return _to_json_text(payload)


@mcp.tool()
def graph_fusion_retrieve(
    query: str,
    top_k: int = 3,
    source_filter: str = "agent_basics",
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
) -> str:
    """Run GraphRAG + VectorRAG fusion through the agent-api MCP server."""
    payload = run_graph_fusion_retrieve_mcp_tool(
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
        graph_dry_run=graph_dry_run,
        trace_id=trace_id,
    )
    return _to_json_text(payload)


@mcp.tool()
def multi_agent_eval_trace(
    task: str,
    thread_id: str = "mcp-multi-agent-thread",
    trace_id: str = "mcp-multi-agent-trace",
) -> str:
    """Run deterministic Multi-Agent eval / trace through the agent-api MCP server."""
    payload = run_multi_agent_eval_trace_mcp_tool(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
    )
    return _to_json_text(payload)


@mcp.tool()
def answer_verify(
    query: str,
    top_k: int = 3,
    source_filter: str = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = "hybrid",
    embedding_provider: str = "deterministic",
    rebuild_index: bool = True,
    graph_dry_run: bool = True,
    trace_id: str = "mcp-answer-verify-trace",
) -> str:
    """Run Agentic RAG answer verification through the agent-api MCP server."""
    payload = run_answer_verify_mcp_tool(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        retrieval_backend=retrieval_backend,
        embedding_provider=embedding_provider,
        rebuild_index=rebuild_index,
        graph_dry_run=graph_dry_run,
        trace_id=trace_id,
    )
    return _to_json_text(payload)


@mcp.tool()
def rag_backend_eval(
    eval_file: str = "eval_cases/rag_agentic_eval.jsonl",
    backends_csv: str = "hybrid,graph_fusion",
    source_filter: str = "agent_basics",
    max_chars: int = 300,
    embedding_dim: int = 64,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    embedding_provider: str = "deterministic",
    rebuild_index: bool = True,
    graph_dry_run: bool = True,
    trace_id: str = "mcp-rag-backend-eval-trace",
) -> str:
    """Run RAG backend evaluation through the agent-api MCP server."""
    payload = run_rag_backend_eval_mcp_tool(
        eval_file=eval_file,
        backends=_parse_backends_csv(backends_csv),
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        embedding_provider=embedding_provider,
        rebuild_index=rebuild_index,
        graph_dry_run=graph_dry_run,
        trace_id=trace_id,
    )
    return _to_json_text(payload)


@mcp.tool()
def mcp_registry_summary(
    trace_id: str = "mcp-registry-summary-trace",
) -> str:
    """Return the current agent-api MCP registry, permission, and marketplace summary."""
    payload = run_mcp_registry_summary_tool(trace_id=trace_id)
    return _to_json_text(payload)


@mcp.tool()
def mcp_marketplace_discovery(
    trace_id: str = "mcp-marketplace-discovery-trace",
) -> str:
    """Return a CI-safe MCP marketplace discovery report."""
    payload = run_mcp_marketplace_discovery_tool(trace_id=trace_id)
    return _to_json_text(payload)


@mcp.resource(
    "agent-api://mcp/tool-registry",
    name="agent_api_mcp_tool_registry",
    description="Current agent-api MCP tool registry summary.",
    mime_type="application/json",
)
def mcp_tool_registry_resource() -> str:
    return get_mcp_tool_registry_resource()


@mcp.resource(
    "agent-api://mcp/marketplace",
    name="agent_api_mcp_marketplace",
    description="Current agent-api local MCP marketplace catalog summary.",
    mime_type="application/json",
)
def mcp_marketplace_resource() -> str:
    return get_mcp_marketplace_resource()


@mcp.resource(
    "agent-api://mcp/marketplace-discovery",
    name="agent_api_mcp_marketplace_discovery",
    description="CI-safe MCP marketplace discovery report.",
    mime_type="application/json",
)
def mcp_marketplace_discovery_resource() -> str:
    return get_mcp_marketplace_discovery_resource()


@mcp.resource(
    "agent-api://graph/schema",
    name="agent_api_graph_schema",
    description="Current GraphRAG schema exposed as an MCP resource.",
    mime_type="application/json",
)
def graph_schema_resource() -> str:
    return get_graph_schema_resource()


@mcp.resource(
    "agent-api://docs/graphrag",
    name="agent_api_graphrag_docs",
    description="GraphRAG architecture documentation exposed as an MCP resource.",
    mime_type="text/markdown",
)
def graphrag_docs_resource() -> str:
    return get_graphrag_docs_resource()


@mcp.resource(
    "agent-api://docs/multi-agent",
    name="agent_api_multi_agent_docs",
    description="Multi-Agent architecture documentation exposed as an MCP resource.",
    mime_type="text/markdown",
)
def multi_agent_docs_resource() -> str:
    return get_multi_agent_docs_resource()


@mcp.resource(
    "agent-api://docs/mcp-plan",
    name="agent_api_mcp_plan",
    description="MCP Day67-Day72 integration plan exposed as an MCP resource.",
    mime_type="text/markdown",
)
def mcp_plan_resource() -> str:
    return get_mcp_plan_resource()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
