from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_critic_debug_returns_deterministic_critic_validation():
    response = client.post(
        "/multi-agent/critic-debug",
        json={
            "task": "实现 Day56 Critic Agent",
            "thread_id": "day56-critic-debug-thread",
            "metadata": {"source": "day56-test"},
        },
        headers={"x-trace-id": "day56-critic-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day56 Critic Agent"
    assert data["thread_id"] == "day56-critic-debug-thread"
    assert data["trace_id"] == "day56-critic-debug-test-001"
    assert data["current_role"] == "critic"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["memory"]["planner"]["llm_used"] is False
    assert data["memory"]["researcher"]["llm_used"] is False
    assert data["memory"]["tool"]["llm_used"] is False

    assert data["critic"]["critic_role"] == "critic"
    assert data["critic"]["execution_boundary"] == "critic_validation_only"
    assert data["critic"]["llm_used"] is False
    assert data["critic"]["validation_pass"] is True
    assert data["critic"]["failed_check_count"] == 0
    assert data["critic"]["passed_check_count"] >= 8

    researcher_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "researcher"
    ]
    tool_tasks = [task for task in data["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in data["tasks"] if task["assigned_role"] == "critic"]
    reflection_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(researcher_tasks) == 1
    assert len(tool_tasks) == 1
    assert len(critic_tasks) == 1

    assert researcher_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["status"] == "completed"
    assert critic_tasks[0]["status"] == "completed"
    assert critic_tasks[0]["metadata"]["validation_pass"] is True

    assert reflection_tasks
    assert all(task["status"] == "pending" for task in reflection_tasks)

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher", "tool", "critic"}

    assert data["summary"]["artifact_count"] == 4
    assert data["artifacts"][3]["created_by"] == "critic"


def test_multi_agent_critic_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/critic-debug",
        json={
            "task": "",
            "thread_id": "day56-critic-debug-thread",
        },
    )

    assert response.status_code == 422