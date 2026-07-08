from src.app.multi_agent.tool_agent import run_deterministic_tool_agent


def test_run_deterministic_tool_agent_completes_tool_task_only():
    state = run_deterministic_tool_agent(
        task="实现 Day55 Tool Agent",
        thread_id="day55-test-thread",
        trace_id="day55-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day55 Tool Agent"
    assert state["thread_id"] == "day55-test-thread"
    assert state["trace_id"] == "day55-test-trace"
    assert state["current_role"] == "tool"
    assert state["status"] == "pending"

    assert state["memory"]["planner"]["llm_used"] is False
    assert state["memory"]["researcher"]["llm_used"] is False

    tool_memory = state["memory"]["tool"]
    assert tool_memory["tool_role"] == "tool"
    assert tool_memory["planning_mode"] == "implementation"
    assert tool_memory["execution_boundary"] == "tool_simulation_only"
    assert tool_memory["llm_used"] is False
    assert tool_memory["external_tools_used"] is False
    assert len(tool_memory["execution_records"]) >= 4

    researcher_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "researcher"
    ]
    tool_tasks = [task for task in state["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in state["tasks"] if task["assigned_role"] == "critic"]

    assert len(researcher_tasks) == 1
    assert len(tool_tasks) == 1
    assert researcher_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["metadata"]["tool_completed"] is True
    assert tool_tasks[0]["metadata"]["llm_used"] is False
    assert tool_tasks[0]["metadata"]["external_tools_used"] is False
    assert tool_tasks[0]["metadata"]["filesystem_modified"] is False
    assert tool_tasks[0]["metadata"]["shell_commands_executed"] is False

    assert critic_tasks
    assert all(task["status"] == "pending" for task in critic_tasks)

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher", "tool"}

    assert len(state["artifacts"]) == 3
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][1]["created_by"] == "researcher"
    assert state["artifacts"][2]["created_by"] == "tool"
    assert state["artifacts"][2]["artifact_type"] == "markdown"


def test_run_deterministic_tool_agent_keeps_critic_and_supervisor_unexecuted():
    state = run_deterministic_tool_agent(
        task="实现 Day55 Tool Agent",
        thread_id="day55-boundary-thread",
        trace_id="day55-boundary-trace",
    )

    forbidden_executed_roles = {"critic", "memory", "reflection"}

    for event in state["events"]:
        assert not (
            event["role"] in forbidden_executed_roles
            and event["event_type"] in {"task_started", "task_completed"}
        )

    assert "critic" not in {
        event["role"]
        for event in state["events"]
        if event["event_type"] in {"task_started", "task_completed"}
    }

    assert state["memory"]["tool"]["next_role"] in {
        "planner",
        "critic",
        "reflection",
        None,
    }


def test_run_deterministic_tool_agent_adds_fallback_tool_task_when_planner_has_none():
    state = run_deterministic_tool_agent(
        task="调研 Multi-Agent 任务分解方案",
        thread_id="day55-research-mode-thread",
        trace_id="day55-research-mode-trace",
    )

    tool_tasks = [task for task in state["tasks"] if task["assigned_role"] == "tool"]

    assert len(tool_tasks) == 1
    assert tool_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["metadata"]["tool_completed"] is True
    assert state["memory"]["tool"]["execution_boundary"] == "tool_simulation_only"
    assert state["memory"]["tool"]["llm_used"] is False