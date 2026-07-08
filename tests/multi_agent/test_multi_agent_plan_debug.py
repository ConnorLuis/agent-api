from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_plan_debug_returns_deterministic_plan():
    response = client.post(
        "/multi-agent/plan-debug",
        json={
            "task": "实现 Day53 Planner Agent",
            "thread_id": "day53-plan-debug-thread",
            "metadata": {"source": "day53-test"},
        },
        headers={"x-trace-id": "day53-plan-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day53 Planner Agent"
    assert data["thread_id"] == "day53-plan-debug-thread"
    assert data["trace_id"] == "day53-plan-debug-test-001"
    assert data["current_role"] == "planner"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["plan"]["planner_role"] == "planner"
    assert data["plan"]["execution_boundary"] == "planning_only"
    assert data["plan"]["llm_used"] is False

    assert data["tasks"][0]["assigned_role"] == "planner"
    assert data["tasks"][0]["status"] == "completed"

    planned_tasks = data["tasks"][1:]
    assert len(planned_tasks) >= 4
    assert all(task["status"] == "pending" for task in planned_tasks)

    assigned_roles = {task["assigned_role"] for task in planned_tasks}
    assert "researcher" in assigned_roles
    assert "tool" in assigned_roles
    assert "critic" in assigned_roles

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {"supervisor", "planner"}

    assert data["summary"]["task_count"] == len(data["tasks"])
    assert data["summary"]["artifact_count"] == 1
    assert data["memory"]["planner"]["llm_used"] is False


def test_multi_agent_plan_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/plan-debug",
        json={
            "task": "",
            "thread_id": "day53-plan-debug-thread",
        },
    )

    assert response.status_code == 422