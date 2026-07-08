from src.app.multi_agent.memory_agent import run_deterministic_memory_agent


def test_run_deterministic_memory_agent_persists_approved_memory_snapshot():
    state = run_deterministic_memory_agent(
        task="实现 Day57 Memory Agent",
        thread_id="day57-test-thread",
        trace_id="day57-test-trace",
        metadata={"source": "unit-test"},
    )

    assert state["task"] == "实现 Day57 Memory Agent"
    assert state["thread_id"] == "day57-test-thread"
    assert state["trace_id"] == "day57-test-trace"
    assert state["current_role"] == "memory"
    assert state["status"] == "pending"

    assert state["memory"]["planner"]["llm_used"] is False
    assert state["memory"]["researcher"]["llm_used"] is False
    assert state["memory"]["tool"]["llm_used"] is False
    assert state["memory"]["critic"]["llm_used"] is False
    assert state["memory"]["critic"]["validation_pass"] is True

    memory_output = state["memory"]["memory"]

    assert memory_output["memory_role"] == "memory"
    assert memory_output["planning_mode"] == "implementation"
    assert memory_output["execution_boundary"] == "memory_snapshot_only"
    assert memory_output["llm_used"] is False
    assert memory_output["external_storage_used"] is False
    assert memory_output["approved"] is True
    assert memory_output["approval_source"] == "critic"
    assert memory_output["storage_backend"] == "multi_agent_state_memory"
    assert memory_output["persistence_mode"] == "ci_safe_state_snapshot_only"
    assert len(memory_output["memory_items"]) == 4

    persisted_summary = memory_output["persisted_summary"]
    assert persisted_summary["approved_memory_item_count"] == 4
    assert persisted_summary["roles_summarized"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
    ]
    assert persisted_summary["boundary_flags"]["llm_used"] is False
    assert persisted_summary["boundary_flags"]["external_storage_used"] is False
    assert persisted_summary["boundary_flags"]["reflection_executed"] is False
    assert persisted_summary["boundary_flags"]["supervisor_graph_executed"] is False
    assert persisted_summary["boundary_flags"]["graph_fusion_default_changed"] is False

    memory_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "memory"
    ]
    reflection_tasks = [
        task for task in state["tasks"] if task["assigned_role"] == "reflection"
    ]

    assert len(memory_tasks) == 1
    assert memory_tasks[0]["status"] == "completed"
    assert memory_tasks[0]["metadata"]["memory_completed"] is True
    assert memory_tasks[0]["metadata"]["approved"] is True
    assert memory_tasks[0]["metadata"]["llm_used"] is False
    assert memory_tasks[0]["metadata"]["external_storage_used"] is False

    assert reflection_tasks
    assert all(task["status"] == "pending" for task in reflection_tasks)

    event_roles = {event["role"] for event in state["events"]}
    assert event_roles <= {
        "supervisor",
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
    }

    assert len(state["artifacts"]) == 5
    assert state["artifacts"][0]["created_by"] == "planner"
    assert state["artifacts"][1]["created_by"] == "researcher"
    assert state["artifacts"][2]["created_by"] == "tool"
    assert state["artifacts"][3]["created_by"] == "critic"
    assert state["artifacts"][4]["created_by"] == "memory"
    assert state["artifacts"][4]["artifact_type"] == "markdown"


def test_run_deterministic_memory_agent_keeps_reflection_and_supervisor_unexecuted():
    state = run_deterministic_memory_agent(
        task="实现 Day57 Memory Agent",
        thread_id="day57-boundary-thread",
        trace_id="day57-boundary-trace",
    )

    for event in state["events"]:
        assert not (
            event["role"] == "reflection"
            and event["event_type"] in {"task_started", "task_completed"}
        )

    assert not any(
        event["role"] == "supervisor"
        and event["event_type"] in {"task_started", "task_completed"}
        for event in state["events"]
    )

    assert state["memory"]["memory"]["approved"] is True
    assert state["memory"]["memory"]["next_role"] in {
        "planner",
        "reflection",
        None,
    }


def test_run_deterministic_memory_agent_records_expected_memory_item_keys():
    state = run_deterministic_memory_agent(
        task="实现 Day57 Memory Agent",
        thread_id="day57-memory-items-thread",
        trace_id="day57-memory-items-trace",
    )

    memory_item_keys = {
        item["key"] for item in state["memory"]["memory"]["memory_items"]
    }

    assert memory_item_keys == {
        "planner_summary",
        "researcher_summary",
        "tool_summary",
        "critic_summary",
    }