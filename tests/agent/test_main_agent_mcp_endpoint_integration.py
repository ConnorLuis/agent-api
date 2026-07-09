from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def _extract_tool_message_content(payload: dict) -> str:
    for step in payload["steps"]:
        if step["node"] != "tools":
            continue

        for message in step["messages"]:
            if message.get("type") == "ToolMessage":
                return message.get("content", "")

    raise AssertionError("ToolMessage content not found in debug payload")


def test_agent_debug_uses_internal_search_when_main_agent_mcp_disabled(monkeypatch):
    monkeypatch.delenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", raising=False)
    monkeypatch.delenv("AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED", raising=False)

    response = client.post(
        "/agent/debug",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-stage2-mcp-disabled",
        },
        headers={"x-trace-id": "test-day72-stage2-mcp-disabled"},
    )

    assert response.status_code == 200
    payload = response.json()
    tool_content = _extract_tool_message_content(payload)

    assert payload["trace_id"] == "test-day72-stage2-mcp-disabled"
    assert "source=knowledge/agent_basics.md" in tool_content
    assert "MCP Agentic RAG endpoint answer" not in tool_content
    assert payload["final_answer"]


def test_agent_debug_uses_mcp_gateway_when_main_agent_mcp_enabled(monkeypatch):
    def fake_mcp_call(*, query: str, k: int):
        assert "RAG" in query
        assert k == 3
        return {
            "tool_name": "agentic_rag_query",
            "result": {
                "final_answer": "MCP Agentic RAG endpoint answer.",
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
                "graph_fusion_default_changed": False,
            },
        }

    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", "true")
    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        fake_mcp_call,
    )

    response = client.post(
        "/agent/debug",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-stage2-mcp-enabled",
        },
        headers={"x-trace-id": "test-day72-stage2-mcp-enabled"},
    )

    assert response.status_code == 200
    payload = response.json()
    tool_content = _extract_tool_message_content(payload)

    assert payload["trace_id"] == "test-day72-stage2-mcp-enabled"
    assert tool_content == "MCP Agentic RAG endpoint answer."
    assert "MCP Agentic RAG endpoint answer." in payload["final_answer"]


def test_agent_debug_falls_back_when_main_agent_mcp_enabled_but_call_fails(
    monkeypatch,
):
    def failing_mcp_call(*, query: str, k: int):
        raise RuntimeError("simulated endpoint MCP failure")

    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", "true")
    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        failing_mcp_call,
    )

    response = client.post(
        "/agent/debug",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-stage2-mcp-fallback",
        },
        headers={"x-trace-id": "test-day72-stage2-mcp-fallback"},
    )

    assert response.status_code == 200
    payload = response.json()
    tool_content = _extract_tool_message_content(payload)

    assert payload["trace_id"] == "test-day72-stage2-mcp-fallback"
    assert "source=knowledge/agent_basics.md" in tool_content
    assert "simulated endpoint MCP failure" not in tool_content
    assert payload["final_answer"]


def test_agent_chat_still_works_when_main_agent_mcp_enabled(monkeypatch):
    def fake_mcp_call(*, query: str, k: int):
        return {
            "tool_name": "agentic_rag_query",
            "result": {
                "final_answer": "MCP Agentic RAG chat answer.",
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
                "graph_fusion_default_changed": False,
            },
        }

    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", "true")
    monkeypatch.setenv("AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(
        "src.app.agent.mcp_tool_gateway._call_local_mcp_agentic_rag_query",
        fake_mcp_call,
    )

    response = client.post(
        "/agent/chat",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-stage2-agent-chat-mcp-enabled",
        },
        headers={"x-trace-id": "test-day72-stage2-agent-chat-mcp-enabled"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["thread_id"] == "test-day72-stage2-agent-chat-mcp-enabled"
    assert payload["trace_id"] == "test-day72-stage2-agent-chat-mcp-enabled"
    assert "MCP Agentic RAG chat answer." in payload["answer"]
