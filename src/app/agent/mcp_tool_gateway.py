from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from src.app.rag.retriever import search_knowledge


_TRUE_VALUES = {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class MainAgentMCPGatewayConfig:
    enabled: bool
    fallback_enabled: bool
    server_id: str
    mode: str


@dataclass(frozen=True)
class MainAgentToolGatewayResult:
    output: str
    source: str
    mcp_enabled: bool
    fallback_used: bool
    mcp_tool_name: str | None
    error: str | None
    metadata: dict[str, Any]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in _TRUE_VALUES


def get_main_agent_mcp_gateway_config() -> MainAgentMCPGatewayConfig:
    return MainAgentMCPGatewayConfig(
        enabled=_env_bool("AGENT_API_MAIN_AGENT_MCP_ENABLED", False),
        fallback_enabled=_env_bool("AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED", True),
        server_id=os.getenv("AGENT_API_MAIN_AGENT_MCP_SERVER_ID", "agent-api-local"),
        mode=os.getenv("AGENT_API_MAIN_AGENT_MCP_MODE", "local_wrapper"),
    )


def _format_internal_search_results(
    *,
    query: str,
    k: int,
    results: list[Any],
) -> str:
    if not results:
        return "No relevant documents found."

    lines = []

    for index, item in enumerate(results, start=1):
        source = getattr(item, "source", None)
        score = getattr(item, "score", None)
        content = getattr(item, "content", None)

        if isinstance(item, dict):
            source = item.get("source", source)
            score = item.get("score", score)
            content = item.get("content", content)

        source = source or "unknown"
        content = content or str(item)

        lines.append(
            f"[{index}] source={source}, score={score}\n{content}"
        )

    return "\n\n".join(lines)


def _run_internal_search_knowledge_base(
    *,
    query: str,
    k: int,
) -> MainAgentToolGatewayResult:
    results = search_knowledge(query=query, k=k)
    output = _format_internal_search_results(query=query, k=k, results=results)

    return MainAgentToolGatewayResult(
        output=output,
        source="internal_search_knowledge",
        mcp_enabled=False,
        fallback_used=False,
        mcp_tool_name=None,
        error=None,
        metadata={
            "query": query,
            "k": k,
            "result_count": len(results),
            "integration_mode": "internal",
        },
    )


def _extract_mcp_agentic_rag_answer(payload: dict[str, Any]) -> str:
    result = payload.get("result", payload)

    if isinstance(result, dict):
        for key in ("final_answer", "answer", "output"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value

        nested_result = result.get("result")
        if isinstance(nested_result, dict):
            for key in ("final_answer", "answer", "output"):
                value = nested_result.get(key)
                if isinstance(value, str) and value.strip():
                    return value

    summary = payload.get("summary")
    if isinstance(summary, dict):
        value = summary.get("final_answer") or summary.get("answer")
        if isinstance(value, str) and value.strip():
            return value

    return str(payload)


def _call_local_mcp_agentic_rag_query(
    *,
    query: str,
    k: int,
) -> dict[str, Any]:
    from src.app.mcp_integration.tools import run_agentic_rag_query_tool

    return run_agentic_rag_query_tool(
        query=query,
        top_k=k,
        trace_id="main-agent-mcp-search-knowledge-base",
        retrieval_backend="hybrid",
        graph_dry_run=True,
    )


def run_search_knowledge_base_gateway(
    *,
    query: str,
    k: int = 2,
    config: MainAgentMCPGatewayConfig | None = None,
) -> MainAgentToolGatewayResult:
    config = config or get_main_agent_mcp_gateway_config()

    if not config.enabled:
        return _run_internal_search_knowledge_base(query=query, k=k)

    try:
        payload = _call_local_mcp_agentic_rag_query(query=query, k=k)
        answer = _extract_mcp_agentic_rag_answer(payload)

        return MainAgentToolGatewayResult(
            output=answer,
            source="mcp_agentic_rag_query",
            mcp_enabled=True,
            fallback_used=False,
            mcp_tool_name="agentic_rag_query",
            error=None,
            metadata={
                "query": query,
                "k": k,
                "server_id": config.server_id,
                "mode": config.mode,
                "mcp_tool_name": "agentic_rag_query",
                "security_decision": payload.get("security_decision"),
                "security_audit_trace": payload.get("security_audit_trace"),
                "mcp_boundary": payload.get("mcp_boundary"),
            },
        )
    except Exception as exc:
        if not config.fallback_enabled:
            raise

        fallback = _run_internal_search_knowledge_base(query=query, k=k)

        return MainAgentToolGatewayResult(
            output=fallback.output,
            source=fallback.source,
            mcp_enabled=True,
            fallback_used=True,
            mcp_tool_name="agentic_rag_query",
            error=f"{type(exc).__name__}: {exc}",
            metadata={
                **fallback.metadata,
                "server_id": config.server_id,
                "mode": config.mode,
                "mcp_tool_name": "agentic_rag_query",
                "mcp_error": f"{type(exc).__name__}: {exc}",
                "integration_mode": "mcp_fallback_to_internal",
            },
        )


def search_knowledge_base_gateway_text(
    *,
    query: str,
    k: int = 2,
) -> str:
    result = run_search_knowledge_base_gateway(query=query, k=k)
    return result.output
