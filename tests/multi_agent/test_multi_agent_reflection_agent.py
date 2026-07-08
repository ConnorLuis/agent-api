from src.app.multi_agent.reflection_agent import run_deterministic_reflection_agent


def test_run_deterministic_reflection_agent_completes_reflection_task():
    state = run_deterministic_reflection_agent(
        task="实现 Day58 Reflection Agent",
        thread_id="day58-test-thread",
        trace_id="day58-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day58 Reflection Agent"
    assert state["thread_id"] == "day58-test-thread"
    assert state["trace_id"] == "day58-test-trace"
    assert state["current_role"] == "reflection"
    assert state["status"] == "pending"

    assert state["memory"]["planner"]["llm_used"] is False
    assert state["memory"]["researcher"]["llm_used"] is False
    assert state["memory"]["tool"]["llm_used"] is False
    assert state["memory"]["critic"]["llm_used"] is False
    assert state["memory"]["memory"]["llm_used"] is False

    reflection = state["memory"]["reflection"]

    assert reflection["reflection_role"] == "reflection"
    assert reflection["planning_mode"] == "implementation"
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
    assert readiness["supervisor_readiness"]["recommended_next_milestone"] == "Day59 Supervisor graph"

    assert readiness["boundary_flags"]["llm_used"] is False
    assert readiness["boundary_flags"]["external_tools_used"] is False
    assert readiness["boundary_flags"]["external_storage_used"] is False
    assert readiness["boundary_flags"]["supervisor_graph_executed"] is False
    assert readiness["boundary_flags"]["graph_fusion_default_changed"] is False

    reflection_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(reflection_tasks) == 1
    assert reflection_tasks[0]["status"] == "completed"
    assert reflection_tasks[0]["metadata"]["reflection_completed"] is True
    assert reflection_tasks[0]["metadata"]["llm_used"] is False
    assert reflection_tasks[0]["metadata"]["external_tools_used"] is False
    assert reflection_tasks[0]["metadata"]["supervisor_graph_started"] is False

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {
        "supervisor",
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    }

    assert len(state["artifacts"]) == 6
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][1]["created_by"] == "researcher"
    assert state["artifacts"][2]["created_by"] == "tool"
    assert state["artifacts"][3]["created_by"] == "critic"
    assert state["artifacts"][4]["created_by"] == "memory"
    assert state["artifacts"][5]["created_by"] == "reflection"
    assert state["artifacts"][5]["artifact_type"] == "markdown"


def test_run_deterministic_reflection_agent_reflects_expected_categories():
    state = run_deterministic_reflection_agent(
        task="实现 Day58 Reflection Agent",
        thread_id="day58-categories-thread",
        trace_id="day58-categories-trace",
    )

    categories = {
        item["category"] for item in state["memory"]["reflection"]["reflection_items"]
    }

    assert categories == {
        "planning_quality",
        "research_grounding",
        "tool_execution_safety",
        "critic_validation",
        "memory_snapshot",
        "supervisor_readiness",
    }


def test_run_deterministic_reflection_agent_does_not_start_supervisor_graph():
    state = run_deterministic_reflection_agent(
        task="实现 Day58 Reflection Agent",
        thread_id="day58-boundary-thread",
        trace_id="day58-boundary-trace",
    )

    assert not any(
        event["role"] == "supervisor"
        and event["event_type"] in {"task_started", "task_completed"}
        for event in state["events"]
    )

    assert state["memory"]["reflection"]["readiness_summary"]["supervisor_readiness"][
        "supervisor_graph_started"
    ] is False
    assert state["memory"]["reflection"]["next_role"] in {
        "planner",
        None,
    }