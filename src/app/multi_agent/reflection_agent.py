from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.app.multi_agent.memory_agent import run_deterministic_memory_agent
from src.app.multi_agent.state import (
    MultiAgentArtifact,
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
)


ReflectionStatus = Literal["accepted", "follow_up"]


class ReflectionItem(TypedDict):
    category: str
    source_role: str
    status: ReflectionStatus
    summary: str
    evidence: list[str]


class ReflectionAgentOutput(TypedDict):
    reflection_role: str
    planning_mode: str
    objective: str
    source_task_id: str
    reviewed_roles: list[str]
    reflection_items: list[ReflectionItem]
    readiness_summary: dict[str, Any]
    constraints_checked: list[str]
    next_role: str | None
    execution_boundary: str
    llm_used: bool
    external_tools_used: bool
    note: str


def _find_pending_reflection_task(state: MultiAgentState) -> MultiAgentTask | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "reflection" and task.get("status") == "pending":
            return task
    return None


def _find_next_pending_role_after_reflection(state: MultiAgentState) -> str | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "reflection":
            continue
        if task.get("status") == "pending":
            return task.get("assigned_role")
    return None


def _ensure_reflection_task(
    state: MultiAgentState,
    *,
    objective: str,
    planning_mode: str,
) -> MultiAgentTask:
    reflection_task = _find_pending_reflection_task(state)
    if reflection_task is not None:
        return reflection_task

    reflection_task = create_multi_agent_task(
        title="Reflect on deterministic multi-agent workflow",
        description=f"Reflect on Planner / Researcher / Tool / Critic / Memory outputs for: {objective}",
        assigned_role="reflection",
        status="pending",
        metadata={
            "created_by": "reflection_fallback",
            "planning_mode": planning_mode,
            "reason": "Planner output did not contain a pending reflection task.",
        },
    )
    state["tasks"].append(reflection_task)
    state["events"].append(
        create_multi_agent_event(
            event_type="task_added",
            role="reflection",
            message="Reflection Agent added fallback reflection task.",
            metadata={
                "task_id": reflection_task["task_id"],
                "planning_mode": planning_mode,
            },
        )
    )
    return reflection_task


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


def _build_reflection_items(state: MultiAgentState) -> list[ReflectionItem]:
    memory = state.get("memory", {})

    planner = memory.get("planner", {})
    researcher = memory.get("researcher", {})
    tool = memory.get("tool", {})
    critic = memory.get("critic", {})
    memory_output = memory.get("memory", {})

    return [
        {
            "category": "planning_quality",
            "source_role": "planner",
            "status": "accepted",
            "summary": "Planner produced a deterministic task decomposition with explicit role assignments.",
            "evidence": [
                f"planning_mode={planner.get('planning_mode')}",
                f"execution_boundary={planner.get('execution_boundary')}",
                f"llm_used={planner.get('llm_used')}",
                f"planned_task_count={len(planner.get('task_ids', []))}",
            ],
        },
        {
            "category": "research_grounding",
            "source_role": "researcher",
            "status": "accepted",
            "summary": "Researcher converted planner context into deterministic findings without crossing into tool execution.",
            "evidence": [
                f"execution_boundary={researcher.get('execution_boundary')}",
                f"llm_used={researcher.get('llm_used')}",
                f"finding_count={len(researcher.get('findings', []))}",
            ],
        },
        {
            "category": "tool_execution_safety",
            "source_role": "tool",
            "status": "accepted",
            "summary": "Tool Agent produced CI-safe execution records without shell execution, filesystem mutation, or external tools.",
            "evidence": [
                f"execution_boundary={tool.get('execution_boundary')}",
                f"llm_used={tool.get('llm_used')}",
                f"external_tools_used={tool.get('external_tools_used')}",
                f"execution_record_count={len(tool.get('execution_records', []))}",
            ],
        },
        {
            "category": "critic_validation",
            "source_role": "critic",
            "status": "accepted",
            "summary": "Critic validated task transitions, memory outputs, artifacts, and graph_fusion non-default boundary.",
            "evidence": [
                f"validation_pass={critic.get('validation_pass')}",
                f"passed_check_count={critic.get('passed_check_count')}",
                f"warning_check_count={critic.get('warning_check_count')}",
                f"failed_check_count={critic.get('failed_check_count')}",
            ],
        },
        {
            "category": "memory_snapshot",
            "source_role": "memory",
            "status": "accepted",
            "summary": "Memory Agent persisted an approved CI-safe snapshot into MultiAgentState memory and artifacts only.",
            "evidence": [
                f"approved={memory_output.get('approved')}",
                f"storage_backend={memory_output.get('storage_backend')}",
                f"persistence_mode={memory_output.get('persistence_mode')}",
                f"external_storage_used={memory_output.get('external_storage_used')}",
                f"memory_item_count={len(memory_output.get('memory_items', []))}",
            ],
        },
        {
            "category": "supervisor_readiness",
            "source_role": "reflection",
            "status": "follow_up",
            "summary": "The deterministic role chain is ready for a future Supervisor graph, but Supervisor orchestration is intentionally deferred.",
            "evidence": [
                "Supervisor graph is not started in Day58.",
                "Planner-created pending planner subtasks may remain until Supervisor graph controls execution order.",
                "Day59 should introduce Supervisor graph after Reflection Agent is documented and validated.",
            ],
        },
    ]


def _build_readiness_summary(
    *,
    state: MultiAgentState,
    reflection_items: list[ReflectionItem],
) -> dict[str, Any]:
    accepted_count = sum(1 for item in reflection_items if item["status"] == "accepted")
    follow_up_count = sum(1 for item in reflection_items if item["status"] == "follow_up")

    return {
        "reviewed_roles": [
            "planner",
            "researcher",
            "tool",
            "critic",
            "memory",
        ],
        "accepted_reflection_count": accepted_count,
        "follow_up_reflection_count": follow_up_count,
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
            "memory": _artifact_count_by_creator(state, "memory"),
        },
        "supervisor_readiness": {
            "ready_for_supervisor_graph_next": True,
            "supervisor_graph_started": False,
            "recommended_next_milestone": "Day59 Supervisor graph",
        },
        "boundary_flags": {
            "llm_used": False,
            "external_tools_used": False,
            "external_storage_used": False,
            "supervisor_graph_executed": False,
            "graph_fusion_default_changed": False,
        },
    }


def _render_reflection_artifact(
    *,
    objective: str,
    planning_mode: str,
    reflection_task: MultiAgentTask,
    reflection_items: list[ReflectionItem],
    readiness_summary: dict[str, Any],
) -> str:
    lines = [
        "# Deterministic Reflection Report",
        "",
        f"Objective: {objective}",
        f"Planning mode: {planning_mode}",
        f"Reflection task: {reflection_task['title']}",
        f"Reflection task id: {reflection_task['task_id']}",
        "",
        "## Reflection items",
        "",
    ]

    for index, item in enumerate(reflection_items, start=1):
        lines.extend(
            [
                f"{index}. {item['category']}",
                f"   - source_role: {item['source_role']}",
                f"   - status: {item['status']}",
                f"   - summary: {item['summary']}",
                "",
            ]
        )

    supervisor_readiness = readiness_summary["supervisor_readiness"]

    lines.extend(
        [
            "## Readiness summary",
            "",
            f"- accepted_reflection_count: {readiness_summary['accepted_reflection_count']}",
            f"- follow_up_reflection_count: {readiness_summary['follow_up_reflection_count']}",
            f"- ready_for_supervisor_graph_next: {supervisor_readiness['ready_for_supervisor_graph_next']}",
            f"- supervisor_graph_started: {supervisor_readiness['supervisor_graph_started']}",
            f"- recommended_next_milestone: {supervisor_readiness['recommended_next_milestone']}",
            "",
            "## Boundary",
            "",
            "- Reflection Agent is deterministic and LLM-free.",
            "- Reflection Agent only reviews prior Planner / Researcher / Tool / Critic / Memory outputs.",
            "- Supervisor graph is not executed in Day58.",
            "- No external tools, storage, database, or filesystem write is used in Day58.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def run_deterministic_reflection_agent(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = run_deterministic_memory_agent(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    planner_memory = state["memory"]["planner"]
    planning_mode = planner_memory["planning_mode"]

    reflection_task = _ensure_reflection_task(
        state=state,
        objective=task,
        planning_mode=planning_mode,
    )

    state["current_role"] = "reflection"
    state["status"] = "pending"

    reflection_task["status"] = "running"
    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="reflection",
            message="Reflection Agent started deterministic workflow reflection.",
            metadata={
                "task_id": reflection_task["task_id"],
                "planning_mode": planning_mode,
                "llm_used": False,
                "external_tools_used": False,
            },
        )
    )

    reflection_items = _build_reflection_items(state)
    readiness_summary = _build_readiness_summary(
        state=state,
        reflection_items=reflection_items,
    )

    reflection_task["status"] = "completed"
    reflection_task["result"] = "Deterministic Reflection Agent completed workflow reflection."
    reflection_task["metadata"] = {
        **reflection_task.get("metadata", {}),
        "reflection_completed": True,
        "reflection_item_count": len(reflection_items),
        "accepted_reflection_count": readiness_summary["accepted_reflection_count"],
        "follow_up_reflection_count": readiness_summary["follow_up_reflection_count"],
        "llm_used": False,
        "external_tools_used": False,
        "supervisor_graph_started": False,
    }

    next_role = _find_next_pending_role_after_reflection(state)

    reflection_output: ReflectionAgentOutput = {
        "reflection_role": "reflection",
        "planning_mode": planning_mode,
        "objective": task,
        "source_task_id": reflection_task["task_id"],
        "reviewed_roles": [
            "planner",
            "researcher",
            "tool",
            "critic",
            "memory",
        ],
        "reflection_items": reflection_items,
        "readiness_summary": readiness_summary,
        "constraints_checked": [
            "Reflection Agent is deterministic and LLM-free.",
            "Reflection Agent reviews Planner / Researcher / Tool / Critic / Memory outputs.",
            "Reflection Agent does not start Supervisor graph in Day58.",
            "Reflection Agent does not use external tools in Day58.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "next_role": next_role,
        "execution_boundary": "reflection_only",
        "llm_used": False,
        "external_tools_used": False,
        "note": "Day58 executes only deterministic reflection on top of Day57 Memory Agent state flow.",
    }

    state["memory"]["reflection"] = reflection_output

    reflection_artifact: MultiAgentArtifact = create_multi_agent_artifact(
        name="deterministic_reflection_report",
        artifact_type="markdown",
        content=_render_reflection_artifact(
            objective=task,
            planning_mode=planning_mode,
            reflection_task=reflection_task,
            reflection_items=reflection_items,
            readiness_summary=readiness_summary,
        ),
        created_by="reflection",
        metadata={
            "planning_mode": planning_mode,
            "source_task_id": reflection_task["task_id"],
            "reflection_item_count": len(reflection_items),
            "accepted_reflection_count": readiness_summary["accepted_reflection_count"],
            "follow_up_reflection_count": readiness_summary["follow_up_reflection_count"],
            "llm_used": False,
            "external_tools_used": False,
            "supervisor_graph_started": False,
        },
    )
    state["artifacts"].append(reflection_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="reflection",
            message="Reflection Agent added deterministic reflection artifact.",
            metadata={
                "artifact_id": reflection_artifact["artifact_id"],
                "artifact_type": reflection_artifact["artifact_type"],
                "source_task_id": reflection_task["task_id"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed",
            role="reflection",
            message="Reflection Agent completed deterministic workflow reflection.",
            metadata={
                "task_id": reflection_task["task_id"],
                "planning_mode": planning_mode,
                "reflection_item_count": len(reflection_items),
                "llm_used": False,
                "external_tools_used": False,
                "supervisor_graph_started": False,
            },
        )
    )

    return state