import json

from src.app.multi_agent.streaming import build_multi_agent_stream_events


def test_build_multi_agent_stream_events_replays_supervisor_graph_roles():
    events = build_multi_agent_stream_events(
        task="实现 Day60 Multi-Agent streaming",
        thread_id="day60-stream-test-thread",
        trace_id="day60-stream-test-trace",
        metadata={"source": "unit-test"},
    )

    event_names = [event["event"] for event in events]

    assert event_names[0] == "metadata"
    assert "graph" in event_names
    assert "node" in event_names
    assert "edge" in event_names
    assert "role" in event_names
    assert "artifact" in event_names
    assert event_names[-2] == "final"
    assert event_names[-1] == "done"

    metadata_event = events[0]
    assert metadata_event["data"]["task"] == "实现 Day60 Multi-Agent streaming"
    assert metadata_event["data"]["thread_id"] == "day60-stream-test-thread"
    assert metadata_event["data"]["trace_id"] == "day60-stream-test-trace"
    assert metadata_event["data"]["streaming_mode"] == "deterministic_replay"
    assert metadata_event["data"]["llm_used"] is False
    assert metadata_event["data"]["graph_fusion_default_changed"] is False

    graph_event = next(event for event in events if event["event"] == "graph")
    assert graph_event["data"]["graph_name"] == "deterministic_multi_agent_supervisor_graph"
    assert graph_event["data"]["graph_version"] == "day59_supervisor_graph_v1"
    assert graph_event["data"]["execution_order"] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    ]
    assert graph_event["data"]["orchestration_pass"] is True

    role_events = [event for event in events if event["event"] == "role"]
    streamed_roles = [event["data"]["role"] for event in role_events]

    assert streamed_roles == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]

    assert all(event["data"]["llm_used"] is False for event in role_events)
    assert all(event["data"]["status"] == "completed" for event in role_events)

    final_event = events[-2]
    assert final_event["event"] == "final"
    assert final_event["data"]["orchestration_pass"] is True
    assert final_event["data"]["completed_role_count"] == 6
    assert final_event["data"]["artifact_count"] == 7
    assert final_event["data"]["llm_used"] is False

    done_event = events[-1]
    assert done_event["event"] == "done"
    assert done_event["data"]["status"] == "done"


def test_build_multi_agent_stream_events_contains_nodes_edges_and_artifacts():
    events = build_multi_agent_stream_events(
        task="实现 Day60 Multi-Agent streaming",
        thread_id="day60-stream-structure-thread",
        trace_id="day60-stream-structure-trace",
    )

    node_events = [event for event in events if event["event"] == "node"]
    edge_events = [event for event in events if event["event"] == "edge"]
    artifact_events = [event for event in events if event["event"] == "artifact"]

    assert [event["data"]["node_id"] for event in node_events] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
    ]

    assert [(event["data"]["source"], event["data"]["target"]) for event in edge_events] == [
        ("planner", "researcher"),
        ("researcher", "tool"),
        ("tool", "critic"),
        ("critic", "memory"),
        ("memory", "reflection"),
    ]

    assert [event["data"]["created_by"] for event in artifact_events] == [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]


def test_stream_events_are_json_serializable():
    events = build_multi_agent_stream_events(
        task="实现 Day60 Multi-Agent streaming",
        thread_id="day60-json-thread",
        trace_id="day60-json-trace",
    )

    for event in events:
        json.dumps(event["data"], ensure_ascii=False, sort_keys=True)