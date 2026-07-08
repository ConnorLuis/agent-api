from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.app.multi_agent.critic import run_deterministic_critic_agent
from src.app.multi_agent.state import (
    MultiAgentArtifact,
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
)


MemoryItemStatus = Literal["approved", "skipped"]


class MemoryItem(TypedDict):
    key: str
    source_role: str
    status: MemoryItemStatus
    summary: str
    evidence: list[str]


class MemoryAgentOutput(TypedDict):
    memory_role: str
    planning_mode: str
    objective: str
    source_task_id: str
    approved: bool
    approval_source: str
    memory_items: list[MemoryItem]
    persisted_summary: dict[str, Any]
    storage_backend: str
    persistence_mode: str
    constraints_checked: list[str]
    next_role: str | None
    execution_boundary: str
    llm_used: bool
    external_storage_used: bool
    note: str


def _find_pending_memory_task(state: MultiAgentState) -> MultiAgentTask | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "memory" and task.get("status") == "pending":
            return task
    return None


def _find_next_pending_role_after_memory(state: MultiAgentState) -> str | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "memory":
            continue
        if task.get("status") == "pending":
            return task.get("assigned_role")
    return None


def _ensure_memory_task(
    state: MultiAgentState,
    *,
    objective: str,
    planning_mode: str,
) -> MultiAgentTask:
    memory_task = _find_pending_memory_task(state)
    if memory_task is not None:
        return memory_task

    memory_task = create_multi_agent_task(
        title="Persist approved multi-agent memory",
        description=f"Summarize approved Planner / Researcher / Tool / Critic memory for: {objective}",
        assigned_role="memory",
        status="pending",
        metadata={
            "created_by": "memory_fallback",
            "planning_mode": planning_mode,
            "reason": "Planner output did not contain a pending memory task.",
        },
    )
    state["tasks"].append(memory_task)
    state["events"].append(
        create_multi_agent_event(
            event_type="task_added",
            role="memory",
            message="Memory Agent added fallback memory task.",
            metadata={
                "task_id": memory_task["task_id"],
                "planning_mode": planning_mode,
            },
        )
    )
    return memory_task


def _task_statuses_by_role(state: MultiAgentState, role: str) -> list[str]:
    return [
        task.get("status", "unknown")
        for task in state.get("tasks", [])
        if task.get("assigned_role") == role
    ]


def _artifact_count_by_creator(state: MultiAgentState, creator: str) -> int:
    return sum(
        1
        for artifact in state.get("artifacts", [])
        if artifact.get("created_by") == creator
    )


def _build_memory_items(state: MultiAgentState) -> list[MemoryItem]:
    memory = state.get("memory", {})

    planner = memory.get("planner", {})
    researcher = memory.get("researcher", {})
    tool = memory.get("tool", {})
    critic = memory.get("critic", {})

    return [
        {
            "key": "planner_summary",
            "source_role": "planner",
            "status": "approved",
            "summary": "Planner produced a deterministic execution plan and stayed within the planning-only boundary.",
            "evidence": [
                f"planning_mode={planner.get('planning_mode')}",
                f"execution_boundary={planner.get('execution_boundary')}",
                f"llm_used={planner.get('llm_used')}",
                f"task_id_count={len(planner.get('task_ids', []))}",
            ],
        },
        {
            "key": "researcher_summary",
            "source_role": "researcher",
            "status": "approved",
            "summary": "Researcher produced deterministic findings and stayed within the research-only boundary.",
            "evidence": [
                f"execution_boundary={researcher.get('execution_boundary')}",
                f"llm_used={researcher.get('llm_used')}",
                f"finding_count={len(researcher.get('findings', []))}",
                f"source_task_id={researcher.get('source_task_id')}",
            ],
        },
        {
            "key": "tool_summary",
            "source_role": "tool",
            "status": "approved",
            "summary": "Tool Agent produced CI-safe execution records without external tool execution or filesystem mutation.",
            "evidence": [
                f"execution_boundary={tool.get('execution_boundary')}",
                f"llm_used={tool.get('llm_used')}",
                f"external_tools_used={tool.get('external_tools_used')}",
                f"execution_record_count={len(tool.get('execution_records', []))}",
            ],
        },
        {
            "key": "critic_summary",
            "source_role": "critic",
            "status": "approved",
            "summary": "Critic validated task transitions, memory outputs, artifacts, and boundary flags.",
            "evidence": [
                f"execution_boundary={critic.get('execution_boundary')}",
                f"validation_pass={critic.get('validation_pass')}",
                f"passed_check_count={critic.get('passed_check_count')}",
                f"warning_check_count={critic.get('warning_check_count')}",
                f"failed_check_count={critic.get('failed_check_count')}",
            ],
        },
    ]


def _build_persisted_summary(
    *,
    state: MultiAgentState,
    memory_items: list[MemoryItem],
) -> dict[str, Any]:
    return {
        "task": state["task"],
        "thread_id": state["thread_id"],
        "trace_id": state["trace_id"],
        "approved_memory_item_count": len(
            [item for item in memory_items if item["status"] == "approved"]
        ),
        "roles_summarized": [
            item["source_role"]
            for item in memory_items
            if item["status"] == "approved"
        ],
        "task_statuses": {
            "planner": _task_statuses_by_role(state, "planner"),
            "researcher": _task_statuses_by_role(state, "researcher"),
            "tool": _task_statuses_by_role(state, "tool"),
            "critic": _task_statuses_by_role(state, "critic"),
            "memory": _task_statuses_by_role(state, "memory"),
            "reflection": _task_statuses_by_role(state, "reflection"),
        },
        "artifact_counts": {
            "planner": _artifact_count_by_creator(state, "planner"),
            "researcher": _artifact_count_by_creator(state, "researcher"),
            "tool": _artifact_count_by_creator(state, "tool"),
            "critic": _artifact_count_by_creator(state, "critic"),
        },
        "boundary_flags": {
            "llm_used": False,
            "external_storage_used": False,
            "reflection_executed": False,
            "supervisor_graph_executed": False,
            "graph_fusion_default_changed": False,
        },
    }


def _render_memory_artifact(
    *,
    objective: str,
    planning_mode: str,
    memory_task: MultiAgentTask,
    memory_items: list[MemoryItem],
    persisted_summary: dict[str, Any],
) -> str:
    lines = [
        "# Deterministic Memory Snapshot",
        "",
        f"Objective: {objective}",
        f"Planning mode: {planning_mode}",
        f"Memory task: {memory_task['title']}",
        f"Memory task id: {memory_task['task_id']}",
        "",
        "## Approved memory items",
        "",
    ]

    for index, item in enumerate(memory_items, start=1):
        lines.extend(
            [
                f"{index}. {item['key']}",
                f"   - source_role: {item['source_role']}",
                f"   - status: {item['status']}",
                f"   - summary: {item['summary']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Persisted summary",
            "",
            f"- approved_memory_item_count: {persisted_summary['approved_memory_item_count']}",
            f"- roles_summarized: {', '.join(persisted_summary['roles_summarized'])}",
            "",
            "## Boundary",
            "",
            "- Memory Agent is deterministic and LLM-free.",
            "- Memory Agent persists only into MultiAgentState memory and artifacts.",
            "- No external storage, database, or filesystem write is used in Day57.",
            "- Reflection Agent is not executed in Day57.",
            "- Supervisor graph is not executed in Day57.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def run_deterministic_memory_agent(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = run_deterministic_critic_agent(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    planner_memory = state["memory"]["planner"]
    critic_memory = state["memory"]["critic"]
    planning_mode = planner_memory["planning_mode"]

    memory_task = _ensure_memory_task(
        state=state,
        objective=task,
        planning_mode=planning_mode,
    )

    state["current_role"] = "memory"
    state["status"] = "pending"

    memory_task["status"] = "running"
    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="memory",
            message="Memory Agent started deterministic memory summarization.",
            metadata={
                "task_id": memory_task["task_id"],
                "planning_mode": planning_mode,
                "critic_validation_pass": critic_memory.get("validation_pass"),
                "llm_used": False,
                "external_storage_used": False,
            },
        )
    )

    approved = critic_memory.get("validation_pass") is True

    if approved:
        memory_items = _build_memory_items(state)
    else:
        memory_items = [
            {
                "key": "critic_rejected_memory",
                "source_role": "critic",
                "status": "skipped",
                "summary": "Critic validation did not pass, so Memory Agent skipped approved memory persistence.",
                "evidence": [
                    f"validation_pass={critic_memory.get('validation_pass')}",
                    f"failed_check_count={critic_memory.get('failed_check_count')}",
                ],
            }
        ]

    persisted_summary = _build_persisted_summary(
        state=state,
        memory_items=memory_items,
    )

    memory_task["status"] = "completed" if approved else "skipped"
    memory_task["result"] = (
        "Deterministic Memory Agent persisted approved memory snapshot."
        if approved
        else "Deterministic Memory Agent skipped persistence because Critic validation failed."
    )
    memory_task["metadata"] = {
        **memory_task.get("metadata", {}),
        "memory_completed": approved,
        "approved": approved,
        "memory_item_count": len(memory_items),
        "llm_used": False,
        "external_storage_used": False,
    }

    next_role = _find_next_pending_role_after_memory(state)

    memory_output: MemoryAgentOutput = {
        "memory_role": "memory",
        "planning_mode": planning_mode,
        "objective": task,
        "source_task_id": memory_task["task_id"],
        "approved": approved,
        "approval_source": "critic",
        "memory_items": memory_items,
        "persisted_summary": persisted_summary,
        "storage_backend": "multi_agent_state_memory",
        "persistence_mode": "ci_safe_state_snapshot_only",
        "constraints_checked": [
            "Memory Agent is deterministic and LLM-free.",
            "Memory Agent persists only approved Critic-validated memory.",
            "Memory Agent does not use external storage in Day57.",
            "Reflection Agent is not executed in Day57.",
            "Supervisor graph is not executed in Day57.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "next_role": next_role,
        "execution_boundary": "memory_snapshot_only",
        "llm_used": False,
        "external_storage_used": False,
        "note": "Day57 executes only deterministic memory summarization on top of Day56 Critic Agent state flow.",
    }

    state["memory"]["memory"] = memory_output

    memory_artifact: MultiAgentArtifact = create_multi_agent_artifact(
        name="deterministic_memory_snapshot",
        artifact_type="markdown",
        content=_render_memory_artifact(
            objective=task,
            planning_mode=planning_mode,
            memory_task=memory_task,
            memory_items=memory_items,
            persisted_summary=persisted_summary,
        ),
        created_by="memory",
        metadata={
            "planning_mode": planning_mode,
            "source_task_id": memory_task["task_id"],
            "approved": approved,
            "memory_item_count": len(memory_items),
            "llm_used": False,
            "external_storage_used": False,
        },
    )
    state["artifacts"].append(memory_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="memory",
            message="Memory Agent added deterministic memory snapshot artifact.",
            metadata={
                "artifact_id": memory_artifact["artifact_id"],
                "artifact_type": memory_artifact["artifact_type"],
                "source_task_id": memory_task["task_id"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed" if approved else "task_skipped",
            role="memory",
            message=(
                "Memory Agent completed deterministic memory summarization."
                if approved
                else "Memory Agent skipped memory persistence because Critic validation failed."
            ),
            metadata={
                "task_id": memory_task["task_id"],
                "planning_mode": planning_mode,
                "approved": approved,
                "memory_item_count": len(memory_items),
                "llm_used": False,
                "external_storage_used": False,
            },
        )
    )

    return state