from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_tool_debug_returns_deterministic_tool_execution():
    response = client.post(
        "/multi-agent/tool-debug",
        json={
            "task": "实现 Day55 Tool Agent",
            "thread_id": "day55-tool-debug-thread",
            "metadata": {"source": "day55-test"},
        },
        headers={"x-trace-id": "day55-tool-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day55 Tool Agent"
    assert data["thread_id"] == "day55-tool-debug-thread"
    assert data["trace_id"] == "day55-tool-debug-test-001"
    assert data["current_role"] == "tool"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["memory"]["planner"]["llm_used"] is False
    assert data["memory"]["researcher"]["llm_used"] is False

    assert data["tool"]["tool_role"] == "tool"
    assert data["tool"]["execution_boundary"] == "tool_simulation_only"
    assert data["tool"]["llm_used"] is False
    assert data["tool"]["external_tools_used"] is False
    assert len(data["tool"]["execution_records"]) >= 4

    researcher_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "researcher"
    ]
    tool_tasks = [task for task in data["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in data["tasks"] if task["assigned_role"] == "critic"]

    assert len(researcher_tasks) == 1
    assert len(tool_tasks) == 1
    assert researcher_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["metadata"]["tool_completed"] is True

    assert critic_tasks
    assert all(task["status"] == "pending" for task in critic_tasks)

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher", "tool"}

    assert data["summary"]["artifact_count"] == 3
    assert data["artifacts"][2]["created_by"] == "tool"


def test_multi_agent_tool_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/tool-debug",
        json={
            "task": "",
            "thread_id": "day55-tool-debug-thread",
        },
    )

    assert response.status_code == 422