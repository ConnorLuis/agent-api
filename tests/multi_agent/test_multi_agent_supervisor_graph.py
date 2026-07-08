from src.app.multi_agent.supervisor_graph import run_deterministic_supervisor_graph


def test_run_deterministic_supervisor_graph_completes_orchestration():
    state = run_deterministic_supervisor_graph(
        task="实现 Day59 Supervisor graph",
        thread_id="day59-test-thread",
        trace_id="day59-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day59 Supervisor graph"
    assert state["thread_id"] == "day59-test-thread"
    assert state["trace_id"] == "day59-test-trace"
    assert state["current_role"] == "supervisor"
    assert state["status"] == "completed"

    assert state["memory"]["planner"]["llm_used"] is False
    assert state["memory"]["researcher"]["llm_used"] is False
    assert state["memory"]["tool"]["llm_used"] is False
    assert state["memory"]["critic"]["llm_used"] is False
    assert state["memory"]["memory"]["llm_used"] is False
    assert state["memory"]["reflection"]["llm_used"] is False

    supervisor = state["memory"]["supervisor"]

    assert supervisor["supervisor_role"] == "supervisor"
    assert supervisor["planning_mode"] == "implementation"
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

    expected_preserved_endpoints = {
        "/multi-agent/plan-debug",
        "/multi-agent/research-debug",
        "/multi-agent/tool-debug",
        "/multi-agent/critic-debug",
        "/multi-agent/memory-debug",
        "/multi-agent/reflection-debug",
    }
    assert set(supervisor["preserved_debug_endpoints"]) == expected_preserved_endpoints

    supervisor_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "supervisor"
    ]
    assert len(supervisor_tasks) == 1
    assert supervisor_tasks[0]["status"] == "completed"
    assert supervisor_tasks[0]["metadata"]["supervisor_completed"] is True
    assert supervisor_tasks[0]["metadata"]["orchestration_pass"] is True
    assert supervisor_tasks[0]["metadata"]["llm_used"] is False

    assert len(state["artifacts"]) == 7
    assert state["artifacts"][-1]["created_by"] == "supervisor"
    assert state["artifacts"][-1]["name"] == "deterministic_supervisor_graph_report"


def test_run_deterministic_supervisor_graph_records_expected_roles_and_memory():
    state = run_deterministic_supervisor_graph(
        task="实现 Day59 Supervisor graph",
        thread_id="day59-memory-thread",
        trace_id="day59-memory-trace",
    )

    expected_memory_keys = {
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    }

    assert expected_memory_keys <= set(state["memory"].keys())

    supervisor = state["memory"]["supervisor"]
    readiness_by_role = {
        item["role"]: item for item in supervisor["role_readiness"]
    }

    for role in ["planner", "researcher", "tool", "critic", "memory", "reflection"]:
        assert readiness_by_role[role]["memory_present"] is True
        assert readiness_by_role[role]["artifact_count"] >= 1
        assert readiness_by_role[role]["completed_task_count"] >= 1
        assert readiness_by_role[role]["ready"] is True


def test_run_deterministic_supervisor_graph_keeps_graph_fusion_non_default_boundary():
    state = run_deterministic_supervisor_graph(
        task="实现 Day59 Supervisor graph",
        thread_id="day59-boundary-thread",
        trace_id="day59-boundary-trace",
    )

    supervisor = state["memory"]["supervisor"]

    assert "graph_fusion remains a non-default retrieval backend." in supervisor[
        "constraints_checked"
    ]
    assert supervisor["orchestration_pass"] is True

    assert not any(
        constraint == "graph_fusion is the default retrieval backend."
        for constraint in supervisor["constraints_checked"]
    )