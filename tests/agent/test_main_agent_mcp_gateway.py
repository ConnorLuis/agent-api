import pytest

from src.app.agent.mcp_tool_gateway import (
    MainAgentMCPGatewayConfig,
    run_search_knowledge_base_gateway,
)


def test_main_agent_mcp_gateway_uses_internal_search_when_disabled():
    result = run_search_knowledge_base_gateway(
        query="RAG 是什么？",
        k=2,
        config=MainAgentMCPGatewayConfig(
            enabled=False,
            fallback_enabled=True,
            server_id="agent-api-local",
            mode="local_wrapper",
        ),
    )

    assert result.source == "internal_search_knowledge"
    assert result.mcp_enabled is False
    assert result.fallback_used is False
    assert result.mcp_tool_name is None
    assert result.error is None
    assert "知识库检索结果" in result.output
    assert result.metadata["integration_mode"] == "internal"


def test_main_agent_mcp_gateway_uses_mcp_when_enabled(monkeypatch):
    def fake_mcp_call(*, query: str, k: int):
        assert query == "RAG 是什么？"
        assert k == 2
        return {
            "tool_name": "agentic_rag_query",
            "result": {
                "final_answer": "MCP Agentic RAG answer with citations.",
            },
            "security_decision": {
                "allowed": True,
                "tool_name": "agentic_rag_query",
            },
            "security_audit_trace": {
                "event_type": "mcp_security_decision",
            },
            "mcp_boundary": {
                "ci_safe": True,
            },
        }

    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        fake_mcp_call,
    )

    result = run_search_knowledge_base_gateway(
        query="RAG 是什么？",
        k=2,
        config=MainAgentMCPGatewayConfig(
            enabled=True,
            fallback_enabled=True,
            server_id="agent-api-local",
            mode="local_wrapper",
        ),
    )

    assert result.output == "MCP Agentic RAG answer with citations."
    assert result.source == "mcp_agentic_rag_query"
    assert result.mcp_enabled is True
    assert result.fallback_used is False
    assert result.mcp_tool_name == "agentic_rag_query"
    assert result.error is None
    assert result.metadata["security_decision"]["allowed"] is True
    assert result.metadata["security_audit_trace"]["event_type"] == "mcp_security_decision"


def test_main_agent_mcp_gateway_falls_back_to_internal_search_when_mcp_fails(
    monkeypatch,
):
    def failing_mcp_call(*, query: str, k: int):
        raise RuntimeError("simulated MCP failure")

    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        failing_mcp_call,
    )

    result = run_search_knowledge_base_gateway(
        query="RAG 是什么？",
        k=2,
        config=MainAgentMCPGatewayConfig(
            enabled=True,
            fallback_enabled=True,
            server_id="agent-api-local",
            mode="local_wrapper",
        ),
    )

    assert result.source == "internal_search_knowledge"
    assert result.mcp_enabled is True
    assert result.fallback_used is True
    assert result.mcp_tool_name == "agentic_rag_query"
    assert "RuntimeError: simulated MCP failure" == result.error
    assert "知识库检索结果" in result.output
    assert result.metadata["integration_mode"] == "mcp_fallback_to_internal"


def test_main_agent_mcp_gateway_raises_when_mcp_fails_and_fallback_disabled(
    monkeypatch,
):
    def failing_mcp_call(*, query: str, k: int):
        raise RuntimeError("simulated MCP failure")

    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        failing_mcp_call,
    )

    with pytest.raises(RuntimeError, match="simulated MCP failure"):
        run_search_knowledge_base_gateway(
            query="RAG 是什么？",
            k=2,
            config=MainAgentMCPGatewayConfig(
                enabled=True,
                fallback_enabled=False,
                server_id="agent-api-local",
                mode="local_wrapper",
            ),
        )
