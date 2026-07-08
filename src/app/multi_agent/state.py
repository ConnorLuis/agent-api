from __future__ import annotations

from typing import Any, Literal, TypedDict
from uuid import uuid4


MultiAgentRole = Literal[
    "supervisor",
    "planner",
    "researcher",
    "tool",
    "critic",
    "memory",
    "reflection",
]

MultiAgentTaskStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
]

MultiAgentEventType = Literal[
    "state_initialized",
    "task_added",
    "task_started",
    "task_completed",
    "task_failed",
    "artifact_added",
    "note_added",
]


class MultiAgentTask(TypedDict, total=False):
    task_id: str
    title: str
    description: str
    assigned_role: MultiAgentRole
    status: MultiAgentTaskStatus
    depends_on: list[str]
    result: str | None
    metadata: dict[str, Any]


class MultiAgentEvent(TypedDict, total=False):
    event_id: str
    event_type: MultiAgentEventType
    role: MultiAgentRole
    message: str
    metadata: dict[str, Any]


class MultiAgentArtifact(TypedDict, total=False):
    artifact_id: str
    name: str
    artifact_type: str
    content: str
    created_by: MultiAgentRole
    metadata: dict[str, Any]


class MultiAgentState(TypedDict, total=False):
    task: str
    thread_id: str
    trace_id: str
    current_role: MultiAgentRole
    tasks: list[MultiAgentTask]
    events: list[MultiAgentEvent]
    artifacts: list[MultiAgentArtifact]
    memory: dict[str, Any]
    final_answer: str | None
    status: MultiAgentTaskStatus


def create_multi_agent_task(
    title: str,
    description: str,
    assigned_role: MultiAgentRole,
    *,
    depends_on: list[str] | None = None,
    status: MultiAgentTaskStatus = "pending",
    metadata: dict[str, Any] | None = None,
) -> MultiAgentTask:
    return {
        "task_id": f"task-{uuid4().hex[:12]}",
        "title": title,
        "description": description,
        "assigned_role": assigned_role,
        "status": status,
        "depends_on": depends_on or [],
        "result": None,
        "metadata": metadata or {},
    }


def create_multi_agent_event(
    event_type: MultiAgentEventType,
    role: MultiAgentRole,
    message: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentEvent:
    return {
        "event_id": f"event-{uuid4().hex[:12]}",
        "event_type": event_type,
        "role": role,
        "message": message,
        "metadata": metadata or {},
    }


def create_multi_agent_artifact(
    name: str,
    artifact_type: str,
    content: str,
    created_by: MultiAgentRole,
    *,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentArtifact:
    return {
        "artifact_id": f"artifact-{uuid4().hex[:12]}",
        "name": name,
        "artifact_type": artifact_type,
        "content": content,
        "created_by": created_by,
        "metadata": metadata or {},
    }


def initialize_multi_agent_state(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    initial_task = create_multi_agent_task(
        title="Initial user task",
        description=task,
        assigned_role="planner",
        metadata=metadata,
    )

    initial_event = create_multi_agent_event(
        event_type="state_initialized",
        role="supervisor",
        message="Multi-Agent state initialized.",
        metadata={
            "initial_task_id": initial_task["task_id"],
            "thread_id": thread_id,
        },
    )

    return {
        "task": task,
        "thread_id": thread_id,
        "trace_id": trace_id,
        "current_role": "supervisor",
        "tasks": [initial_task],
        "events": [initial_event],
        "artifacts": [],
        "memory": {},
        "final_answer": None,
        "status": "pending",
    }


def summarize_multi_agent_state(state: MultiAgentState) -> dict[str, Any]:
    tasks = state.get("tasks", [])
    events = state.get("events", [])
    artifacts = state.get("artifacts", [])

    status_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}

    for task in tasks:
        status = task.get("status", "pending")
        role = task.get("assigned_role", "planner")
        status_counts[status] = status_counts.get(status, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "task_count": len(tasks),
        "event_count": len(events),
        "artifact_count": len(artifacts),
        "status_counts": status_counts,
        "role_counts": role_counts,
        "current_role": state.get("current_role"),
        "status": state.get("status"),
    }