from src.app.multi_agent.state import (
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
    initialize_multi_agent_state,
    summarize_multi_agent_state,
)


def test_initialize_multi_agent_state_creates_initial_task_and_event():
    state = initialize_multi_agent_state(
        task="分析 GraphRAG 项目并给出改进建议",
        thread_id="test-thread",
        trace_id="test-trace",
    )

    assert state["task"] == "分析 GraphRAG 项目并给出改进建议"
    assert state["thread_id"] == "test-thread"
    assert state["trace_id"] == "test-trace"
    assert state["current_role"] == "supervisor"
    assert state["status"] == "pending"

    assert len(state["tasks"]) == 1
    assert state["tasks"][0]["assigned_role"] == "planner"
    assert state["tasks"][0]["status"] == "pending"

    assert len(state["events"]) == 1
    assert state["events"][0]["event_type"] == "state_initialized"
    assert state["events"][0]["role"] == "supervisor"


def test_create_multi_agent_task_uses_expected_defaults():
    task = create_multi_agent_task(
        title="Plan work",
        description="Break down the task.",
        assigned_role="planner",
    )

    assert task["task_id"].startswith("task-")
    assert task["title"] == "Plan work"
    assert task["assigned_role"] == "planner"
    assert task["status"] == "pending"
    assert task["depends_on"] == []
    assert task["result"] is None
    assert task["metadata"] == {}


def test_create_multi_agent_event_uses_expected_defaults():
    event = create_multi_agent_event(
        event_type="task_started",
        role="planner",
        message="Planner started.",
    )

    assert event["event_id"].startswith("event-")
    assert event["event_type"] == "task_started"
    assert event["role"] == "planner"
    assert event["message"] == "Planner started."
    assert event["metadata"] == {}


def test_create_multi_agent_artifact_uses_expected_defaults():
    artifact = create_multi_agent_artifact(
        name="plan",
        artifact_type="markdown",
        content="## Plan",
        created_by="planner",
    )

    assert artifact["artifact_id"].startswith("artifact-")
    assert artifact["name"] == "plan"
    assert artifact["artifact_type"] == "markdown"
    assert artifact["content"] == "## Plan"
    assert artifact["created_by"] == "planner"
    assert artifact["metadata"] == {}


def test_summarize_multi_agent_state_counts_tasks_events_and_artifacts():
    state = initialize_multi_agent_state(
        task="Test task",
        thread_id="test-thread",
        trace_id="test-trace",
    )
    state["tasks"].append(
        create_multi_agent_task(
            title="Research",
            description="Research task",
            assigned_role="researcher",
            status="completed",
        )
    )
    state["artifacts"].append(
        create_multi_agent_artifact(
            name="notes",
            artifact_type="text",
            content="notes",
            created_by="researcher",
        )
    )

    summary = summarize_multi_agent_state(state)

    assert summary["task_count"] == 2
    assert summary["event_count"] == 1
    assert summary["artifact_count"] == 1
    assert summary["status_counts"]["pending"] == 1
    assert summary["status_counts"]["completed"] == 1
    assert summary["role_counts"]["planner"] == 1
    assert summary["role_counts"]["researcher"] == 1