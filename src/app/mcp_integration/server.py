from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.app.mcp_integration.tools import (
    MCP_SERVER_NAME,
    run_agentic_rag_query_mcp_tool,
    run_graph_fusion_retrieve_mcp_tool,
    run_multi_agent_eval_trace_mcp_tool,
)


mcp = FastMCP(MCP_SERVER_NAME)


def _to_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
