from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_research_debug_returns_deterministic_research():
    response = client.post(
        "/multi-agent/research-debug",
        json={
            "task": "实现 Day54 Research Agent",
            "thread_id": "day54-research-debug-thread",
            "metadata": {"source": "day54-test"},
        },
        headers={"x-trace-id": "day54-research-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day54 Research Agent"
    assert data["thread_id"] == "day54-research-debug-thread"
    assert data["trace_id"] == "day54-research-debug-test-001"
    assert data["current_role"] == "researcher"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["research"]["researcher_role"] == "researcher"
    assert data["research"]["execution_boundary"] == "research_only"
    assert data["research"]["llm_used"] is False
    assert len(data["research"]["findings"]) >= 3

    assert data["memory"]["planner"]["llm_used"] is False
    assert data["memory"]["researcher"]["llm_used"] is False

    researcher_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "researcher"
    ]
    assert len(researcher_tasks) == 1
    assert researcher_tasks[0]["status"] == "completed"

    tool_tasks = [task for task in data["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in data["tasks"] if task["assigned_role"] == "critic"]

    assert tool_tasks
    assert critic_tasks
    assert all(task["status"] == "pending" for task in tool_tasks)
    assert all(task["status"] == "pending" for task in critic_tasks)

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher"}

    assert data["summary"]["artifact_count"] == 2
    assert data["artifacts"][1]["created_by"] == "researcher"


def test_multi_agent_research_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/research-debug",
        json={
            "task": "",
            "thread_id": "day54-research-debug-thread",
        },
    )

    assert response.status_code == 422