from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_supervisor_debug_returns_deterministic_supervisor_graph():
    response = client.post(
        "/multi-agent/supervisor-debug",
        json={
            "task": "实现 Day59 Supervisor graph",
            "thread_id": "day59-supervisor-debug-thread",
            "metadata": {"source": "day59-test"},
        },
        headers={"x-trace-id": "day59-supervisor-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day59 Supervisor graph"
    assert data["thread_id"] == "day59-supervisor-debug-thread"
    assert data["trace_id"] == "day59-supervisor-debug-test-001"
    assert data["current_role"] == "supervisor"
    assert data["status"] == "completed"
    assert data["planning_mode"] == "implementation"

    supervisor = data["supervisor"]

    assert supervisor["supervisor_role"] == "supervisor"
    assert supervisor["graph_name"] == "deterministic_multi_agent_supervisor_graph"
    assert supervisor["graph_version"] == "day59_supervisor_graph_v1"
    assert supervisor["execution_boundary"] == "supervisor_orchestration_only"
    assert supervisor["llm_used"] is False
    assert supervisor["orchestration_pass"] is True
    assert supervisor["completed_role_count"] == 6

    assert supervisor["execution_order"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    ]

    assert [node["node_id"] for node in supervisor["nodes"]] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    ]
    assert all(node["status"] == "completed" for node in supervisor["nodes"])

    assert [(edge["source"], edge["target"]) for edge in supervisor["edges"]] == [
        ("planner", "researcher"),
        ("researcher", "tool"),
        ("tool", "critic"),
        ("critic", "memory"),
        ("memory", "reflection"),
    ]

    assert all(item["ready"] is True for item in supervisor["role_readiness"])

    assert data["memory"]["supervisor"]["orchestration_pass"] is True
    assert data["summary"]["artifact_count"] == 7
    assert data["artifacts"][-1]["created_by"] == "supervisor"


def test_multi_agent_supervisor_debug_preserves_role_specific_debug_endpoints():
    response = client.post(
        "/multi-agent/supervisor-debug",
        json={
            "task": "实现 Day59 Supervisor graph",
            "thread_id": "day59-supervisor-preserve-thread",
        },
        headers={"x-trace-id": "day59-supervisor-preserve-test-001"},
    )

    assert response.status_code == 200

    supervisor = response.json()["supervisor"]

    assert set(supervisor["preserved_debug_endpoints"]) == {
        "/multi-agent/plan-debug",
        "/multi-agent/research-debug",
        "/multi-agent/tool-debug",
        "/multi-agent/critic-debug",
        "/multi-agent/memory-debug",
        "/multi-agent/reflection-debug",
    }


def test_multi_agent_supervisor_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/supervisor-debug",
        json={
            "task": "",
            "thread_id": "day59-supervisor-debug-thread",
        },
    )

    assert response.status_code == 422