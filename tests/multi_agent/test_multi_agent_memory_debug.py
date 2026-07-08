from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_memory_debug_returns_deterministic_memory_snapshot():
    response = client.post(
        "/multi-agent/memory-debug",
        json={
            "task": "实现 Day57 Memory Agent",
            "thread_id": "day57-memory-debug-thread",
            "metadata": {"source": "day57-test"},
        },
        headers={"x-trace-id": "day57-memory-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day57 Memory Agent"
    assert data["thread_id"] == "day57-memory-debug-thread"
    assert data["trace_id"] == "day57-memory-debug-test-001"
    assert data["current_role"] == "memory"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["memory"]["planner"]["llm_used"] is False
    assert data["memory"]["researcher"]["llm_used"] is False
    assert data["memory"]["tool"]["llm_used"] is False
    assert data["memory"]["critic"]["llm_used"] is False
    assert data["memory"]["critic"]["validation_pass"] is True

    memory_output = data["memory_output"]

    assert memory_output["memory_role"] == "memory"
    assert memory_output["execution_boundary"] == "memory_snapshot_only"
    assert memory_output["llm_used"] is False
    assert memory_output["external_storage_used"] is False
    assert memory_output["approved"] is True
    assert memory_output["approval_source"] == "critic"
    assert len(memory_output["memory_items"]) == 4

    assert data["memory"]["memory"]["approved"] is True
    assert data["memory"]["memory"]["persisted_summary"]["approved_memory_item_count"] == 4

    memory_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "memory"
    ]
    reflection_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(memory_tasks) == 1
    assert memory_tasks[0]["status"] == "completed"
    assert memory_tasks[0]["metadata"]["approved"] is True

    assert reflection_tasks
    assert all(task["status"] == "pending" for task in reflection_tasks)

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {
        "supervisor",
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
    }

    assert data["summary"]["artifact_count"] == 5
    assert data["artifacts"][4]["created_by"] == "memory"


def test_multi_agent_memory_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/memory-debug",
        json={
            "task": "",
            "thread_id": "day57-memory-debug-thread",
        },
    )

    assert response.status_code == 422