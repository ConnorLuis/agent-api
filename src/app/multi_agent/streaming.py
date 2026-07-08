from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any, Literal, TypedDict

from src.app.multi_agent.supervisor_graph import run_deterministic_supervisor_graph


MultiAgentStreamEventType = Literal[
    "metadata",
    "graph",
    "node",
    "edge",
    "role",
    "artifact",
    "final",
    "done",
]


class MultiAgentStreamEvent(TypedDict):
    event: MultiAgentStreamEventType
    data: dict[str, Any]


def _format_sse_event(event: str, data: dict[str, Any]) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False, sort_keys=True)}\n\n"
    )


def _artifact_count_by_creator(artifacts: list[dict[str, Any]], creator: str) -> int:
    return sum(1 for artifact in artifacts if artifact.get("created_by") == creator)


def _completed_task_count_by_role(tasks: list[dict[str, Any]], role: str) -> int:
    return sum(
        1
        for task in tasks
        if task.get("assigned_role") == role and task.get("status") == "completed"
    )


def _build_role_stream_payload(
    *,
    role: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    memory = state.get("memory", {})
    tasks = state.get("tasks", [])
    artifacts = state.get("artifacts", [])

    role_memory = memory.get(role, {})

    return {
        "role": role,
        "memory_present": role in memory,
        "artifact_count": _artifact_count_by_creator(artifacts, role),
        "completed_task_count": _completed_task_count_by_role(tasks, role),
        "llm_used": role_memory.get("llm_used", False),
        "execution_boundary": role_memory.get("execution_boundary"),
        "status": "completed" if role in memory else "skipped",
    }


def build_multi_agent_stream_events(
    *,
    task: str,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> list[MultiAgentStreamEvent]:
    state = run_deterministic_supervisor_graph(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    supervisor = state["memory"]["supervisor"]
    execution_order = supervisor["execution_order"]

    events: list[MultiAgentStreamEvent] = [
        {
            "event": "metadata",
            "data": {
                "task": state["task"],
                "thread_id": state["thread_id"],
                "trace_id": state["trace_id"],
                "current_role": state["current_role"],
                "status": state["status"],
                "streaming_mode": "deterministic_replay",
                "llm_used": False,
                "graph_fusion_default_changed": False,
            },
        },
        {
            "event": "graph",
            "data": {
                "graph_name": supervisor["graph_name"],
                "graph_version": supervisor["graph_version"],
                "planning_mode": supervisor["planning_mode"],
                "execution_order": execution_order,
                "orchestration_pass": supervisor["orchestration_pass"],
                "completed_role_count": supervisor["completed_role_count"],
                "execution_boundary": supervisor["execution_boundary"],
            },
        },
    ]

    for node in supervisor["nodes"]:
        events.append(
            {
                "event": "node",
                "data": {
                    "node_id": node["node_id"],
                    "role": node["role"],
                    "status": node["status"],
                    "memory_key": node["memory_key"],
                    "artifact_expected": node["artifact_expected"],
                    "summary": node["summary"],
                },
            }
        )

    for edge in supervisor["edges"]:
        events.append(
            {
                "event": "edge",
                "data": {
                    "source": edge["source"],
                    "target": edge["target"],
                    "condition": edge["condition"],
                },
            }
        )

    for index, role in enumerate(execution_order, start=1):
        events.append(
            {
                "event": "role",
                "data": {
                    "sequence": index,
                    **_build_role_stream_payload(role=role, state=state),
                },
            }
        )

    events.append(
        {
            "event": "role",
            "data": {
                "sequence": len(execution_order) + 1,
                **_build_role_stream_payload(role="supervisor", state=state),
                "orchestration_pass": supervisor["orchestration_pass"],
            },
        }
    )

    for artifact in state.get("artifacts", []):
        events.append(
            {
                "event": "artifact",
                "data": {
                    "artifact_id": artifact["artifact_id"],
                    "name": artifact["name"],
                    "artifact_type": artifact["artifact_type"],
                    "created_by": artifact["created_by"],
                },
            }
        )

    events.append(
        {
            "event": "final",
            "data": {
                "task": state["task"],
                "thread_id": state["thread_id"],
                "trace_id": state["trace_id"],
                "current_role": state["current_role"],
                "status": state["status"],
                "orchestration_pass": supervisor["orchestration_pass"],
                "completed_role_count": supervisor["completed_role_count"],
                "artifact_count": len(state.get("artifacts", [])),
                "event_count": len(state.get("events", [])),
                "preserved_debug_endpoints": supervisor["preserved_debug_endpoints"],
                "llm_used": False,
                "graph_fusion_default_changed": False,
            },
        }
    )

    events.append(
        {
            "event": "done",
            "data": {
                "trace_id": state["trace_id"],
                "status": "done",
            },
        }
    )

    return events


def stream_deterministic_multi_agent_events(
    *,
    task: str,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> Iterator[str]:
    events = build_multi_agent_stream_events(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    for event in events:
        yield _format_sse_event(event=event["event"], data=event["data"])