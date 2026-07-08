from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.app.multi_agent.tool_agent import run_deterministic_tool_agent
from src.app.multi_agent.state import (
    MultiAgentArtifact,
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
)


CriticCheckStatus = Literal["passed", "failed", "warning"]


class CriticCheck(TypedDict):
    check_name: str
    status: CriticCheckStatus
    summary: str
    evidence: list[str]


class CriticAgentOutput(TypedDict):
    critic_role: str
    planning_mode: str
    objective: str
    source_task_id: str
    checks: list[CriticCheck]
    passed_check_count: int
    warning_check_count: int
    failed_check_count: int
    validation_pass: bool
    constraints_checked: list[str]
    next_role: str | None
    execution_boundary: str
    llm_used: bool
    note: str


def _find_pending_critic_task(state: MultiAgentState) -> MultiAgentTask | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "critic" and task.get("status") == "pending":
            return task
    return None


def _find_next_pending_role_after_critic(state: MultiAgentState) -> str | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "critic":
            continue
        if task.get("status") == "pending":
            return task.get("assigned_role")
    return None


def _ensure_critic_task(
    state: MultiAgentState,
    *,
    objective: str,
    planning_mode: str,
) -> MultiAgentTask:
    critic_task = _find_pending_critic_task(state)
    if critic_task is not None:
        return critic_task

    critic_task = create_multi_agent_task(
        title="Validate deterministic multi-agent execution",
        description=f"Validate deterministic Planner / Researcher / Tool outputs for: {objective}",
        assigned_role="critic",
        status="pending",
        metadata={
            "created_by": "critic_fallback",
            "planning_mode": planning_mode,
            "reason": "Planner output did not contain a pending critic task.",
        },
    )
    state["tasks"].append(critic_task)
    state["events"].append(
        create_multi_agent_event(
            event_type="task_added",
            role="critic",
            message="Critic Agent added fallback critic task.",
            metadata={
                "task_id": critic_task["task_id"],
                "planning_mode": planning_mode,
            },
        )
    )
    return critic_task


def _tasks_by_role(state: MultiAgentState, role: str) -> list[MultiAgentTask]:
    return [task for task in state.get("tasks", []) if task.get("assigned_role") == role]


def _artifacts_by_creator(state: MultiAgentState, creator: str) -> list[MultiAgentArtifact]:
    return [
        artifact
        for artifact in state.get("artifacts", [])
        if artifact.get("created_by") == creator
    ]


def _build_critic_checks(
    *,
    state: MultiAgentState,
    planning_mode: str,
) -> list[CriticCheck]:
    memory = state.get("memory", {})
    tasks = state.get("tasks", [])

    planner_tasks = _tasks_by_role(state, "planner")
    researcher_tasks = _tasks_by_role(state, "researcher")
    tool_tasks = _tasks_by_role(state, "tool")
    critic_tasks = _tasks_by_role(state, "critic")

    planner_artifacts = _artifacts_by_creator(state, "planner")
    researcher_artifacts = _artifacts_by_creator(state, "researcher")
    tool_artifacts = _artifacts_by_creator(state, "tool")

    checks: list[CriticCheck] = []

    initial_planner_completed = any(
        task.get("title") == "Initial user task"
        and task.get("assigned_role") == "planner"
        and task.get("status") == "completed"
        for task in tasks
    )

    checks.append(
        {
            "check_name": "planner_initial_task_completed",
            "status": "passed" if initial_planner_completed else "failed",
            "summary": "Initial planner task should be completed after Day53 planning.",
            "evidence": [
                f"planner_task_count={len(planner_tasks)}",
                f"initial_planner_completed={initial_planner_completed}",
            ],
        }
    )

    researcher_completed = (
        len(researcher_tasks) >= 1
        and all(task.get("status") == "completed" for task in researcher_tasks)
    )
    checks.append(
        {
            "check_name": "researcher_task_completed",
            "status": "passed" if researcher_completed else "failed",
            "summary": "Researcher task should be completed by Day54 flow.",
            "evidence": [
                f"researcher_task_count={len(researcher_tasks)}",
                f"researcher_statuses={[task.get('status') for task in researcher_tasks]}",
            ],
        }
    )

    tool_completed = (
        len(tool_tasks) >= 1
        and all(task.get("status") == "completed" for task in tool_tasks)
    )
    checks.append(
        {
            "check_name": "tool_task_completed",
            "status": "passed" if tool_completed else "failed",
            "summary": "Tool task should be completed by Day55 flow.",
            "evidence": [
                f"tool_task_count={len(tool_tasks)}",
                f"tool_statuses={[task.get('status') for task in tool_tasks]}",
            ],
        }
    )

    planner_memory_ok = (
        "planner" in memory
        and memory["planner"].get("llm_used") is False
        and memory["planner"].get("execution_boundary") == "planning_only"
    )
    checks.append(
        {
            "check_name": "planner_memory_boundary",
            "status": "passed" if planner_memory_ok else "failed",
            "summary": "Planner memory should exist and remain deterministic / planning-only.",
            "evidence": [
                f"planner_memory_exists={'planner' in memory}",
                f"planner_llm_used={memory.get('planner', {}).get('llm_used')}",
                f"planner_boundary={memory.get('planner', {}).get('execution_boundary')}",
            ],
        }
    )

    researcher_memory_ok = (
        "researcher" in memory
        and memory["researcher"].get("llm_used") is False
        and memory["researcher"].get("execution_boundary") == "research_only"
    )
    checks.append(
        {
            "check_name": "researcher_memory_boundary",
            "status": "passed" if researcher_memory_ok else "failed",
            "summary": "Researcher memory should exist and remain deterministic / research-only.",
            "evidence": [
                f"researcher_memory_exists={'researcher' in memory}",
                f"researcher_llm_used={memory.get('researcher', {}).get('llm_used')}",
                f"researcher_boundary={memory.get('researcher', {}).get('execution_boundary')}",
            ],
        }
    )

    tool_memory_ok = (
        "tool" in memory
        and memory["tool"].get("llm_used") is False
        and memory["tool"].get("external_tools_used") is False
        and memory["tool"].get("execution_boundary") == "tool_simulation_only"
    )
    checks.append(
        {
            "check_name": "tool_memory_boundary",
            "status": "passed" if tool_memory_ok else "failed",
            "summary": "Tool memory should exist and remain deterministic / simulation-only.",
            "evidence": [
                f"tool_memory_exists={'tool' in memory}",
                f"tool_llm_used={memory.get('tool', {}).get('llm_used')}",
                f"tool_external_tools_used={memory.get('tool', {}).get('external_tools_used')}",
                f"tool_boundary={memory.get('tool', {}).get('execution_boundary')}",
            ],
        }
    )

    artifact_chain_ok = (
        len(planner_artifacts) >= 1
        and len(researcher_artifacts) >= 1
        and len(tool_artifacts) >= 1
    )
    checks.append(
        {
            "check_name": "artifact_chain_exists",
            "status": "passed" if artifact_chain_ok else "failed",
            "summary": "Planner, Researcher, and Tool artifacts should all exist before Critic completes.",
            "evidence": [
                f"planner_artifact_count={len(planner_artifacts)}",
                f"researcher_artifact_count={len(researcher_artifacts)}",
                f"tool_artifact_count={len(tool_artifacts)}",
            ],
        }
    )

    forbidden_started_roles = {"memory", "reflection"}
    forbidden_events = [
        event
        for event in state.get("events", [])
        if event.get("role") in forbidden_started_roles
        and event.get("event_type") in {"task_started", "task_completed"}
    ]
    checks.append(
        {
            "check_name": "future_agents_not_executed",
            "status": "passed" if not forbidden_events else "failed",
            "summary": "Memory / Reflection agents should not be executed in Day56.",
            "evidence": [
                f"forbidden_event_count={len(forbidden_events)}",
                f"forbidden_roles={sorted(forbidden_started_roles)}",
            ],
        }
    )

    supervisor_graph_not_started = not any(
        event.get("role") == "supervisor"
        and event.get("event_type") in {"task_started", "task_completed"}
        for event in state.get("events", [])
    )
    checks.append(
        {
            "check_name": "supervisor_graph_not_started",
            "status": "passed" if supervisor_graph_not_started else "failed",
            "summary": "Supervisor graph should not start in Day56.",
            "evidence": [
                f"supervisor_graph_not_started={supervisor_graph_not_started}",
                "Only state_initialized from supervisor is allowed before Supervisor graph work.",
            ],
        }
    )

    def _has_graph_fusion_non_default_boundary(memory_item: dict[str, Any]) -> bool:
        constraints = [
            *memory_item.get("constraints", []),
            *memory_item.get("constraints_checked", []),
        ]
        normalized_constraints = [str(item).lower() for item in constraints]

        return any(
            "graph_fusion" in item
            and ("non-default" in item or "non default" in item)
            for item in normalized_constraints
        )

    planner_boundary_present = _has_graph_fusion_non_default_boundary(
        memory.get("planner", {})
    )
    researcher_boundary_present = _has_graph_fusion_non_default_boundary(
        memory.get("researcher", {})
    )
    tool_boundary_present = _has_graph_fusion_non_default_boundary(
        memory.get("tool", {})
    )

    graph_fusion_boundary_ok = (
        planner_boundary_present
        and researcher_boundary_present
        and tool_boundary_present
    )

    checks.append(
        {
            "check_name": "graph_fusion_non_default_boundary",
            "status": "passed" if graph_fusion_boundary_ok else "failed",
            "summary": "Planner / Researcher / Tool should preserve the graph_fusion non-default boundary.",
            "evidence": [
                f"planning_mode={planning_mode}",
                f"planner_boundary_present={planner_boundary_present}",
                f"researcher_boundary_present={researcher_boundary_present}",
                f"tool_boundary_present={tool_boundary_present}",
            ],
        }
    )

    pending_planner_tasks = [
        task for task in planner_tasks if task.get("status") == "pending"
    ]
    checks.append(
        {
            "check_name": "non_blocking_pending_planner_task",
            "status": "warning" if pending_planner_tasks else "passed",
            "summary": "Planner-created planner subtasks may remain pending until Supervisor graph decides execution order.",
            "evidence": [
                f"pending_planner_task_count={len(pending_planner_tasks)}",
                "This is acceptable before Supervisor graph orchestration.",
            ],
        }
    )

    checks.append(
        {
            "check_name": "critic_task_available",
            "status": "passed" if critic_tasks else "failed",
            "summary": "A critic task should exist before Day56 Critic validation completes.",
            "evidence": [
                f"critic_task_count={len(critic_tasks)}",
                f"critic_statuses={[task.get('status') for task in critic_tasks]}",
            ],
        }
    )

    return checks


def _count_checks(checks: list[CriticCheck], status: CriticCheckStatus) -> int:
    return sum(1 for check in checks if check["status"] == status)


def _render_critic_artifact(
    *,
    objective: str,
    planning_mode: str,
    critic_task: MultiAgentTask,
    checks: list[CriticCheck],
) -> str:
    passed_count = _count_checks(checks, "passed")
    warning_count = _count_checks(checks, "warning")
    failed_count = _count_checks(checks, "failed")

    lines = [
        "# Deterministic Critic Review",
        "",
        f"Objective: {objective}",
        f"Planning mode: {planning_mode}",
        f"Critic task: {critic_task['title']}",
        f"Critic task id: {critic_task['task_id']}",
        "",
        "## Summary",
        "",
        f"- passed: {passed_count}",
        f"- warning: {warning_count}",
        f"- failed: {failed_count}",
        "",
        "## Checks",
        "",
    ]

    for index, check in enumerate(checks, start=1):
        lines.extend(
            [
                f"{index}. {check['check_name']}",
                f"   - status: {check['status']}",
                f"   - summary: {check['summary']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Boundary",
            "",
            "- Critic Agent is deterministic and LLM-free.",
            "- Critic Agent only validates prior state flow.",
            "- Supervisor graph is not executed in Day56.",
            "- Memory / Reflection agents are not executed in Day56.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def run_deterministic_critic_agent(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = run_deterministic_tool_agent(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    planner_memory = state["memory"]["planner"]
    planning_mode = planner_memory["planning_mode"]

    critic_task = _ensure_critic_task(
        state=state,
        objective=task,
        planning_mode=planning_mode,
    )

    state["current_role"] = "critic"
    state["status"] = "pending"

    critic_task["status"] = "running"
    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="critic",
            message="Critic Agent started deterministic validation.",
            metadata={
                "task_id": critic_task["task_id"],
                "planning_mode": planning_mode,
                "llm_used": False,
            },
        )
    )

    checks = _build_critic_checks(
        state=state,
        planning_mode=planning_mode,
    )

    passed_count = _count_checks(checks, "passed")
    warning_count = _count_checks(checks, "warning")
    failed_count = _count_checks(checks, "failed")
    validation_pass = failed_count == 0

    critic_task["status"] = "completed" if validation_pass else "failed"
    critic_task["result"] = (
        "Deterministic Critic Agent completed validation."
        if validation_pass
        else "Deterministic Critic Agent found blocking validation failures."
    )
    critic_task["metadata"] = {
        **critic_task.get("metadata", {}),
        "critic_completed": validation_pass,
        "validation_pass": validation_pass,
        "passed_check_count": passed_count,
        "warning_check_count": warning_count,
        "failed_check_count": failed_count,
        "llm_used": False,
    }

    next_role = _find_next_pending_role_after_critic(state)

    critic_output: CriticAgentOutput = {
        "critic_role": "critic",
        "planning_mode": planning_mode,
        "objective": task,
        "source_task_id": critic_task["task_id"],
        "checks": checks,
        "passed_check_count": passed_count,
        "warning_check_count": warning_count,
        "failed_check_count": failed_count,
        "validation_pass": validation_pass,
        "constraints_checked": [
            "Critic Agent is deterministic and LLM-free.",
            "Critic Agent validates Planner / Researcher / Tool state transitions.",
            "Critic Agent validates memory outputs and artifacts.",
            "Supervisor graph is not executed in Day56.",
            "Memory / Reflection agents are not executed in Day56.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "next_role": next_role,
        "execution_boundary": "critic_validation_only",
        "llm_used": False,
        "note": "Day56 executes only deterministic Critic validation on top of Day55 Tool Agent state flow.",
    }

    state["memory"]["critic"] = critic_output

    critic_artifact: MultiAgentArtifact = create_multi_agent_artifact(
        name="deterministic_critic_review",
        artifact_type="markdown",
        content=_render_critic_artifact(
            objective=task,
            planning_mode=planning_mode,
            critic_task=critic_task,
            checks=checks,
        ),
        created_by="critic",
        metadata={
            "planning_mode": planning_mode,
            "source_task_id": critic_task["task_id"],
            "passed_check_count": passed_count,
            "warning_check_count": warning_count,
            "failed_check_count": failed_count,
            "validation_pass": validation_pass,
            "llm_used": False,
        },
    )
    state["artifacts"].append(critic_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="critic",
            message="Critic Agent added deterministic review artifact.",
            metadata={
                "artifact_id": critic_artifact["artifact_id"],
                "artifact_type": critic_artifact["artifact_type"],
                "source_task_id": critic_task["task_id"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed" if validation_pass else "task_failed",
            role="critic",
            message=(
                "Critic Agent completed deterministic validation."
                if validation_pass
                else "Critic Agent found deterministic validation failures."
            ),
            metadata={
                "task_id": critic_task["task_id"],
                "planning_mode": planning_mode,
                "passed_check_count": passed_count,
                "warning_check_count": warning_count,
                "failed_check_count": failed_count,
                "validation_pass": validation_pass,
                "llm_used": False,
            },
        )
    )

    return state