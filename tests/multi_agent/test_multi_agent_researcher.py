from src.app.multi_agent.researcher import run_deterministic_research


def test_run_deterministic_research_completes_researcher_task_only():
    state = run_deterministic_research(
        task="实现 Day54 Research Agent",
        thread_id="day54-test-thread",
        trace_id="day54-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day54 Research Agent"
    assert state["thread_id"] == "day54-test-thread"
    assert state["trace_id"] == "day54-test-trace"
    assert state["current_role"] == "researcher"
    assert state["status"] == "pending"

    planner_memory = state["memory"]["planner"]
    researcher_memory = state["memory"]["researcher"]

    assert planner_memory["llm_used"] is False
    assert researcher_memory["researcher_role"] == "researcher"
    assert researcher_memory["planning_mode"] == "implementation"
    assert researcher_memory["execution_boundary"] == "research_only"
    assert researcher_memory["llm_used"] is False
    assert len(researcher_memory["findings"]) >= 3

    researcher_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "researcher"
    ]
    assert len(researcher_tasks) == 1
    assert researcher_tasks[0]["status"] == "completed"
    assert researcher_tasks[0]["metadata"]["research_completed"] is True

    tool_tasks = [task for task in state["tasks"] if task["assigned_role"] == "tool"]
    critic_tasks = [task for task in state["tasks"] if task["assigned_role"] == "critic"]

    assert tool_tasks
    assert critic_tasks
    assert all(task["status"] == "pending" for task in tool_tasks)
    assert all(task["status"] == "pending" for task in critic_tasks)

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {"supervisor", "planner", "researcher"}

    assert len(state["artifacts"]) == 2
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][1]["created_by"] == "researcher"
    assert state["artifacts"][1]["artifact_type"] == "markdown"


def test_run_deterministic_research_keeps_future_agents_unexecuted():
    state = run_deterministic_research(
        task="实现 Day54 Research Agent",
        thread_id="day54-boundary-thread",
        trace_id="day54-boundary-trace",
    )

    forbidden_executed_roles = {"tool", "critic", "memory", "reflection"}

    for event in state["events"]:
        assert not (
            event["role"] in forbidden_executed_roles
            and event["event_type"] in {"task_started", "task_completed"}
        )

    assert state["memory"]["researcher"]["next_role"] in {
        "planner",
        "tool",
        "critic",
        "reflection",
        None,
    }


def test_run_deterministic_research_adds_fallback_research_task_when_planner_has_none():
    state = run_deterministic_research(
        task="更新 README 和 HANDOFF 文档",
        thread_id="day54-doc-thread",
        trace_id="day54-doc-trace",
    )

    researcher_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "researcher"
    ]

    assert len(researcher_tasks) == 1
    assert researcher_tasks[0]["status"] == "completed"
    assert researcher_tasks[0]["metadata"]["research_completed"] is True
    assert state["memory"]["researcher"]["planning_mode"] == "documentation"