from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_agent_chat_preserves_internal_tool_behavior_when_mcp_disabled(monkeypatch):
    monkeypatch.delenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", raising=False)

    response = client.post(
        "/agent/chat",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-agent-mcp-disabled",
        },
        headers={"x-trace-id": "test-day72-agent-mcp-disabled"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["thread_id"] == "test-day72-agent-mcp-disabled"
    assert payload["trace_id"] == "test-day72-agent-mcp-disabled"
    assert payload["answer"]


def test_agent_debug_preserves_tool_path_when_mcp_disabled(monkeypatch):
    monkeypatch.delenv("AGENT_API_MAIN_AGENT_MCP_ENABLED", raising=False)

    response = client.post(
        "/agent/debug",
        json={
            "message": "请在知识库里搜索 RAG 是什么？",
            "thread_id": "test-day72-agent-debug-mcp-disabled",
        },
        headers={"x-trace-id": "test-day72-agent-debug-mcp-disabled"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["trace_id"] == "test-day72-agent-debug-mcp-disabled"
    assert payload["steps"]
    assert payload["final_answer"]
