from src.app.multi_agent.planner import (
    build_deterministic_plan,
    infer_planning_mode,
)


def test_infer_planning_mode_detects_implementation():
    assert infer_planning_mode("实现 Day53 Planner Agent") == "implementation"
    assert infer_planning_mode("Build deterministic planner") == "implementation"


def test_infer_planning_mode_detects_debugging():
    assert infer_planning_mode("修复 pytest 失败的问题") == "debugging"
    assert infer_planning_mode("debug traceback error") == "debugging"


def test_infer_planning_mode_detects_documentation():
    assert infer_planning_mode("更新 README 和 HANDOFF 文档") == "documentation"


def test_build_deterministic_plan_creates_pending_tasks_without_executing_other_agents():
    state = build_deterministic_plan(
        task="实现 Day53 Planner Agent",
        thread_id="day53-test-thread",
        trace_id="day53-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day53 Planner Agent"
    assert state["thread_id"] == "day53-test-thread"
    assert state["trace_id"] == "day53-test-trace"
    assert state["current_role"] == "planner"
    assert state["status"] == "pending"

    assert state["tasks"][0]["assigned_role"] == "planner"
    assert state["tasks"][0]["status"] == "completed"

    planned_tasks = state["tasks"][1:]
    assert len(planned_tasks) >= 4
    assert all(task["status"] == "pending" for task in planned_tasks)

    assigned_roles = {task["assigned_role"] for task in planned_tasks}
    assert "researcher" in assigned_roles
    assert "tool" in assigned_roles
    assert "critic" in assigned_roles
    assert "reflection" in assigned_roles

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {"supervisor", "planner"}

    planner_memory = state["memory"]["planner"]
    assert planner_memory["planning_mode"] == "implementation"
    assert planner_memory["execution_boundary"] == "planning_only"
    assert planner_memory["llm_used"] is False
    assert planner_memory["next_role"] in assigned_roles

    assert len(state["artifacts"]) == 1
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][0]["artifact_type"] == "markdown"