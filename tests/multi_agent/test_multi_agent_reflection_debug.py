from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_reflection_debug_returns_deterministic_reflection():
    response = client.post(
        "/multi-agent/reflection-debug",
        json={
            "task": "实现 Day58 Reflection Agent",
            "thread_id": "day58-reflection-debug-thread",
            "metadata": {"source": "day58-test"},
        },
        headers={"x-trace-id": "day58-reflection-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day58 Reflection Agent"
    assert data["thread_id"] == "day58-reflection-debug-thread"
    assert data["trace_id"] == "day58-reflection-debug-test-001"
    assert data["current_role"] == "reflection"
    assert data["status"] == "pending"
    assert data["planning_mode"] == "implementation"

    assert data["memory"]["planner"]["llm_used"] is False
    assert data["memory"]["researcher"]["llm_used"] is False
    assert data["memory"]["tool"]["llm_used"] is False
    assert data["memory"]["critic"]["llm_used"] is False
    assert data["memory"]["memory"]["llm_used"] is False

    reflection = data["reflection"]

    assert reflection["reflection_role"] == "reflection"
    assert reflection["execution_boundary"] == "reflection_only"
    assert reflection["llm_used"] is False
    assert reflection["external_tools_used"] is False
    assert reflection["reviewed_roles"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
    ]
    assert len(reflection["reflection_items"]) == 6

    readiness = reflection["readiness_summary"]
    assert readiness["accepted_reflection_count"] == 5
    assert readiness["follow_up_reflection_count"] == 1
    assert readiness["supervisor_readiness"]["ready_for_supervisor_graph_next"] is True
    assert readiness["supervisor_readiness"]["supervisor_graph_started"] is False
    assert readiness["boundary_flags"]["graph_fusion_default_changed"] is False

    reflection_tasks = [
        task for task in data["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(reflection_tasks) == 1
    assert reflection_tasks[0]["status"] == "completed"
    assert reflection_tasks[0]["metadata"]["reflection_completed"] is True
    assert reflection_tasks[0]["metadata"]["supervisor_graph_started"] is False

    event_roles = {event["role"] for event in data["events"]}
    assert event_roles <= {
        "supervisor",
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    }

    assert not any(
        event["role"] == "supervisor"
        and event["event_type"] in {"task_started", "task_completed"}
        for event in data["events"]
    )

    assert data["summary"]["artifact_count"] == 6
    assert data["artifacts"][5]["created_by"] == "reflection"


def test_multi_agent_reflection_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/reflection-debug",
        json={
            "task": "",
            "thread_id": "day58-reflection-debug-thread",
        },
    )

    assert response.status_code == 422