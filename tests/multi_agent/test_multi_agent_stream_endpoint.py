import json

from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def _parse_sse_events(response_text: str) -> list[dict]:
    parsed_events = []

    for block in response_text.strip().split("\n\n"):
        event_name = None
        data = None

        for line in block.splitlines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ").strip()
            elif line.startswith("data: "):
                data = json.loads(line.removeprefix("data: ").strip())

        if event_name is not None and data is not None:
            parsed_events.append({"event": event_name, "data": data})

    return parsed_events


def test_multi_agent_stream_returns_deterministic_sse_events():
    response = client.post(
        "/multi-agent/stream",
        json={
            "task": "实现 Day60 Multi-Agent streaming",
            "thread_id": "day60-stream-endpoint-thread",
            "metadata": {"source": "day60-test"},
        },
        headers={"x-trace-id": "day60-stream-endpoint-test-001"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    parsed_events = _parse_sse_events(response.text)
    event_names = [event["event"] for event in parsed_events]

    assert event_names[0] == "metadata"
    assert "graph" in event_names
    assert "node" in event_names
    assert "edge" in event_names
    assert "role" in event_names
    assert "artifact" in event_names
    assert event_names[-2] == "final"
    assert event_names[-1] == "done"

    metadata = parsed_events[0]["data"]
    assert metadata["task"] == "实现 Day60 Multi-Agent streaming"
    assert metadata["thread_id"] == "day60-stream-endpoint-thread"
    assert metadata["trace_id"] == "day60-stream-endpoint-test-001"
    assert metadata["streaming_mode"] == "deterministic_replay"
    assert metadata["llm_used"] is False

    role_events = [event for event in parsed_events if event["event"] == "role"]
    assert [event["data"]["role"] for event in role_events] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]

    final = parsed_events[-2]["data"]
    assert final["orchestration_pass"] is True
    assert final["completed_role_count"] == 6
    assert final["artifact_count"] == 7
    assert final["llm_used"] is False
    assert final["graph_fusion_default_changed"] is False

    done = parsed_events[-1]["data"]
    assert done["status"] == "done"
    assert done["trace_id"] == "day60-stream-endpoint-test-001"


def test_multi_agent_stream_preserves_debug_endpoint_contracts_in_final_event():
    response = client.post(
        "/multi-agent/stream",
        json={
            "task": "实现 Day60 Multi-Agent streaming",
            "thread_id": "day60-stream-contract-thread",
        },
        headers={"x-trace-id": "day60-stream-contract-test-001"},
    )

    assert response.status_code == 200

    parsed_events = _parse_sse_events(response.text)
    final = parsed_events[-2]["data"]

    assert set(final["preserved_debug_endpoints"]) == {
        "/multi-agent/plan-debug",
        "/multi-agent/research-debug",
        "/multi-agent/tool-debug",
        "/multi-agent/critic-debug",
        "/multi-agent/memory-debug",
        "/multi-agent/reflection-debug",
    }


def test_multi_agent_stream_rejects_empty_task():
    response = client.post(
        "/multi-agent/stream",
        json={
            "task": "",
            "thread_id": "day60-stream-endpoint-thread",
        },
    )

    assert response.status_code == 422