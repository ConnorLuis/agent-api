from src.app.multi_agent.evaluation import run_deterministic_multi_agent_eval_trace


def test_run_deterministic_multi_agent_eval_trace_passes_all_checks():
    result = run_deterministic_multi_agent_eval_trace(
        task="实现 Day61 Multi-Agent eval / trace",
        thread_id="day61-eval-test-thread",
        trace_id="day61-eval-test-trace",
        metadata={"source": "unit-test"},
    )

    state = result["state"]
    eval_report = result["eval_report"]
    trace_report = result["trace_report"]
    stream_events = result["stream_events"]

    assert state["task"] == "实现 Day61 Multi-Agent eval / trace"
    assert state["thread_id"] == "day61-eval-test-thread"
    assert state["trace_id"] == "day61-eval-test-trace"
    assert state["current_role"] == "supervisor"
    assert state["status"] == "completed"

    assert eval_report["eval_role"] == "multi_agent_eval_trace"
    assert eval_report["planning_mode"] == "implementation"
    assert eval_report["eval_pass"] is True
    assert eval_report["failed_check_count"] == 0
    assert eval_report["passed_check_count"] >= 10
    assert eval_report["execution_boundary"] == "multi_agent_eval_trace_only"
    assert eval_report["llm_used"] is False

    check_names = {check["check_name"] for check in eval_report["checks"]}
    assert {
        "supervisor_orchestration_pass",
        "stream_graph_matches_supervisor",
        "stream_event_sequence",
        "node_coverage",
        "edge_coverage",
        "role_stream_sequence",
        "role_readiness_consistency",
        "artifact_coverage",
        "terminal_stream_events",
        "trace_identity_consistency",
        "boundary_flags",
        "debug_endpoint_contracts",
        "state_event_completion_coverage",
        "trace_report_consistency",
    } <= check_names

    assert trace_report["trace_id"] == "day61-eval-test-trace"
    assert trace_report["thread_id"] == "day61-eval-test-thread"
    assert trace_report["graph_name"] == "deterministic_multi_agent_supervisor_graph"
    assert trace_report["graph_version"] == "day59_supervisor_graph_v1"
    assert trace_report["stream_event_count"] == len(stream_events)
    assert trace_report["streamed_roles"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]
    assert trace_report["artifact_creators"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]
    assert trace_report["boundary_flags"]["default_retrieval_backend"] == "hybrid"
    assert trace_report["boundary_flags"]["graph_fusion_default_changed"] is False


def test_run_deterministic_multi_agent_eval_trace_validates_stream_consistency():
    result = run_deterministic_multi_agent_eval_trace(
        task="实现 Day61 Multi-Agent eval / trace",
        thread_id="day61-stream-consistency-thread",
        trace_id="day61-stream-consistency-trace",
    )

    supervisor = result["state"]["memory"]["supervisor"]
    stream_events = result["stream_events"]

    metadata = stream_events[0]["data"]
    graph = next(event["data"] for event in stream_events if event["event"] == "graph")
    role_events = [event["data"] for event in stream_events if event["event"] == "role"]
    artifact_events = [
        event["data"] for event in stream_events if event["event"] == "artifact"
    ]
    final = stream_events[-2]["data"]
    done = stream_events[-1]["data"]

    assert metadata["streaming_mode"] == "deterministic_replay"
    assert metadata["llm_used"] is False
    assert metadata["graph_fusion_default_changed"] is False

    assert graph["graph_name"] == supervisor["graph_name"]
    assert graph["graph_version"] == supervisor["graph_version"]
    assert graph["execution_order"] == supervisor["execution_order"]
    assert graph["orchestration_pass"] is True

    assert [event["role"] for event in role_events] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]
    assert all(event["status"] == "completed" for event in role_events)
    assert all(event["llm_used"] is False for event in role_events)

    assert [event["created_by"] for event in artifact_events] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]

    assert final["orchestration_pass"] is True
    assert final["llm_used"] is False
    assert final["graph_fusion_default_changed"] is False
    assert done["status"] == "done"


def test_run_deterministic_multi_agent_eval_trace_preserves_endpoint_contracts():
    result = run_deterministic_multi_agent_eval_trace(
        task="实现 Day61 Multi-Agent eval / trace",
        thread_id="day61-endpoint-contract-thread",
        trace_id="day61-endpoint-contract-trace",
    )

    assert set(result["eval_report"]["preserved_endpoints"]) == {
        "/multi-agent/stream",
        "/multi-agent/supervisor-debug",
        "/multi-agent/plan-debug",
        "/multi-agent/research-debug",
        "/multi-agent/tool-debug",
        "/multi-agent/critic-debug",
        "/multi-agent/memory-debug",
        "/multi-agent/reflection-debug",
    }

    assert result["eval_report"]["eval_pass"] is True
    assert "graph_fusion remains a non-default retrieval backend." in result[
        "eval_report"
    ]["constraints_checked"]