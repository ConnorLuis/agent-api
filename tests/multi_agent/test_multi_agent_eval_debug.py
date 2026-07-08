from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_multi_agent_eval_debug_returns_eval_and_trace_report():
    response = client.post(
        "/multi-agent/eval-debug",
        json={
            "task": "实现 Day61 Multi-Agent eval / trace",
            "thread_id": "day61-eval-debug-thread",
            "metadata": {"source": "day61-test"},
        },
        headers={"x-trace-id": "day61-eval-debug-test-001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "实现 Day61 Multi-Agent eval / trace"
    assert data["thread_id"] == "day61-eval-debug-thread"
    assert data["trace_id"] == "day61-eval-debug-test-001"
    assert data["current_role"] == "supervisor"
    assert data["status"] == "completed"
    assert data["planning_mode"] == "implementation"

    eval_report = data["eval_report"]
    trace_report = data["trace_report"]

    assert eval_report["eval_role"] == "multi_agent_eval_trace"
    assert eval_report["eval_pass"] is True
    assert eval_report["failed_check_count"] == 0
    assert eval_report["llm_used"] is False
    assert eval_report["execution_boundary"] == "multi_agent_eval_trace_only"

    assert trace_report["trace_id"] == "day61-eval-debug-test-001"
    assert trace_report["thread_id"] == "day61-eval-debug-thread"
    assert trace_report["graph_name"] == "deterministic_multi_agent_supervisor_graph"
    assert trace_report["graph_version"] == "day59_supervisor_graph_v1"
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

    supervisor = data["supervisor"]
    assert supervisor["orchestration_pass"] is True
    assert supervisor["completed_role_count"] == 6
    assert supervisor["llm_used"] is False

    stream_events = data["stream_events"]
    assert stream_events[0]["event"] == "metadata"
    assert stream_events[1]["event"] == "graph"
    assert stream_events[-2]["event"] == "final"
    assert stream_events[-1]["event"] == "done"

    assert data["summary"]["artifact_count"] == 7


def test_multi_agent_eval_debug_preserves_stream_and_debug_routes():
    endpoints = [
        "/multi-agent/eval-debug",
        "/multi-agent/supervisor-debug",
        "/multi-agent/plan-debug",
        "/multi-agent/research-debug",
        "/multi-agent/tool-debug",
        "/multi-agent/critic-debug",
        "/multi-agent/memory-debug",
        "/multi-agent/reflection-debug",
    ]

    for endpoint in endpoints:
        response = client.post(
            endpoint,
            json={
                "task": "确认 Day61 后 Multi-Agent debug endpoint 仍可用",
                "thread_id": "day61-preserve-debug-endpoints-thread",
            },
            headers={"x-trace-id": "day61-preserve-debug-endpoints-test-001"},
        )
        assert response.status_code == 200, endpoint

    stream_response = client.post(
        "/multi-agent/stream",
        json={
            "task": "确认 Day61 后 stream 仍可用",
            "thread_id": "day61-preserve-stream-thread",
        },
        headers={"x-trace-id": "day61-preserve-stream-test-001"},
    )

    assert stream_response.status_code == 200
    assert stream_response.headers["content-type"].startswith("text/event-stream")
    assert "event: done" in stream_response.text


def test_multi_agent_eval_debug_rejects_empty_task():
    response = client.post(
        "/multi-agent/eval-debug",
        json={
            "task": "",
            "thread_id": "day61-eval-debug-thread",
        },
    )

    assert response.status_code == 422