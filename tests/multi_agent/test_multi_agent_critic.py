from src.app.multi_agent.critic import run_deterministic_critic_agent


def test_run_deterministic_critic_agent_completes_critic_validation():
    state = run_deterministic_critic_agent(
        task="实现 Day56 Critic Agent",
        thread_id="day56-test-thread",
        trace_id="day56-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day56 Critic Agent"
    assert state["thread_id"] == "day56-test-thread"
    assert state["trace_id"] == "day56-test-trace"
    assert state["current_role"] == "critic"
    assert state["status"] == "pending"

    assert state["memory"]["planner"]["llm_used"] is False
    assert state["memory"]["researcher"]["llm_used"] is False
    assert state["memory"]["tool"]["llm_used"] is False

    critic_memory = state["memory"]["critic"]
    assert critic_memory["critic_role"] == "critic"
    assert critic_memory["planning_mode"] == "implementation"
    assert critic_memory["execution_boundary"] == "critic_validation_only"
    assert critic_memory["llm_used"] is False
    assert critic_memory["validation_pass"] is True
    assert critic_memory["failed_check_count"] == 0
    assert critic_memory["passed_check_count"] >= 8

    researcher_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "researcher"
    ]
    tool_tasks = [task for task in state["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in state["tasks"] if task["assigned_role"] == "critic"]
    reflection_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(researcher_tasks) == 1
    assert len(tool_tasks) == 1
    assert len(critic_tasks) == 1

    assert researcher_tasks[0]["status"] == "completed"
    assert tool_tasks[0]["status"] == "completed"
    assert critic_tasks[0]["status"] == "completed"
    assert critic_tasks[0]["metadata"]["critic_completed"] is True
    assert critic_tasks[0]["metadata"]["validation_pass"] is True
    assert critic_tasks[0]["metadata"]["llm_used"] is False

    assert reflection_tasks
    assert all(task["status"] == "pending" for task in reflection_tasks)

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher", "tool", "critic"}

    assert len(state["artifacts"]) == 4
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][1]["created_by"] == "researcher"
    assert state["artifacts"][2]["created_by"] == "tool"
    assert state["artifacts"][3]["created_by"] == "critic"
    assert state["artifacts"][3]["artifact_type"] == "markdown"


def test_run_deterministic_critic_agent_validates_expected_check_names():
    state = run_deterministic_critic_agent(
        task="实现 Day56 Critic Agent",
        thread_id="day56-check-thread",
        trace_id="day56-check-trace",
    )

    check_names = {
        check["check_name"] for check in state["memory"]["critic"]["checks"]
    }

    assert "planner_initial_task_completed" in check_names
    assert "researcher_task_completed" in check_names
    assert "tool_task_completed" in check_names
    assert "planner_memory_boundary" in check_names
    assert "researcher_memory_boundary" in check_names
    assert "tool_memory_boundary" in check_names
    assert "artifact_chain_exists" in check_names
    assert "future_agents_not_executed" in check_names
    assert "supervisor_graph_not_started" in check_names
    assert "graph_fusion_non_default_boundary" in check_names


def test_run_deterministic_critic_agent_keeps_supervisor_memory_reflection_unexecuted():
    state = run_deterministic_critic_agent(
        task="实现 Day56 Critic Agent",
        thread_id="day56-boundary-thread",
        trace_id="day56-boundary-trace",
    )

    forbidden_executed_roles = {"memory", "reflection"}

    for event in state["events"]:
        assert not (
            event["role"] in forbidden_executed_roles
            and event["event_type"] in {"task_started", "task_completed"}
        )

    assert not any(
        event["role"] == "supervisor"
        and event["event_type"] in {"task_started", "task_completed"}
        for event in state["events"]
    )

    assert state["memory"]["critic"]["validation_pass"] is True
    assert state["memory"]["critic"]["next_role"] in {
        "planner",
        "reflection",
        None,
    }