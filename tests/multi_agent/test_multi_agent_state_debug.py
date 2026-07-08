from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_state_debug_initializes_state():
    response = client.post(
        "/multi-agent/state-debug",
        json={
            "task": "分析 GraphRAG 项目并规划下一步 Multi-Agent 工作",
            "thread_id": "day52-test-thread",
            "metadata": {"source": "day52-test"},
        },
        headers={"x-trace-id": "day52-state-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "分析 GraphRAG 项目并规划下一步 Multi-Agent 工作"
    assert data["thread_id"] == "day52-test-thread"
    assert data["trace_id"] == "day52-state-debug-test-001"
    assert data["current_role"] == "supervisor"
    assert data["status"] == "pending"

    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["assigned_role"] == "planner"
    assert data["tasks"][0]["status"] == "pending"
    assert data["tasks"][0]["metadata"] == {"source": "day52-test"}

    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "state_initialized"
    assert data["events"][0]["role"] == "supervisor"

    assert data["artifacts"] == []
    assert data["memory"] == {}

    assert data["summary"]["task_count"] == 1
    assert data["summary"]["event_count"] == 1
    assert data["summary"]["artifact_count"] == 0
    assert data["summary"]["status_counts"]["pending"] == 1
    assert data["summary"]["role_counts"]["planner"] == 1


def test_multi_agent_state_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/state-debug",
        json={
            "task": "",
            "thread_id": "day52-test-thread",
        },
    )

    assert response.status_code == 422