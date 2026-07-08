from __future__ import annotations

from typing import Any, TypedDict

from src.app.multi_agent.planner import build_deterministic_plan
from src.app.multi_agent.state import (
    MultiAgentArtifact,
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
)


class ResearchFinding(TypedDict):
    title: str
    summary: str
    evidence: list[str]
    confidence: str
    tags: list[str]


class ResearcherOutput(TypedDict):
    researcher_role: str
    planning_mode: str
    objective: str
    source_task_id: str
    findings: list[ResearchFinding]
    constraints_checked: list[str]
    next_role: str | None
    execution_boundary: str
    llm_used: bool
    note: str


def _find_pending_researcher_task(state: MultiAgentState) -> MultiAgentTask | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "researcher" and task.get("status") == "pending":
            return task
    return None


def _find_next_pending_role_after_researcher(state: MultiAgentState) -> str | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "researcher":
            continue
        if task.get("status") == "pending":
            return task.get("assigned_role")
    return None


def _ensure_researcher_task(state: MultiAgentState, objective: str, planning_mode: str) -> MultiAgentTask:
    researcher_task = _find_pending_researcher_task(state)
    if researcher_task is not None:
        return researcher_task

    researcher_task = create_multi_agent_task(
        title="Collect deterministic research context",
        description=f"Collect deterministic project context for: {objective}",
        assigned_role="researcher",
        status="pending",
        metadata={
            "created_by": "researcher_fallback",
            "planning_mode": planning_mode,
            "reason": "Planner output did not contain a pending researcher task.",
        },
    )
    state["tasks"].append(researcher_task)
    state["events"].append(
        create_multi_agent_event(
            event_type="task_added",
            role="researcher",
            message="Researcher added fallback research task.",
            metadata={
                "task_id": researcher_task["task_id"],
                "planning_mode": planning_mode,
            },
        )
    )
    return researcher_task


def _build_findings(
    *,
    objective: str,
    planning_mode: str,
    tasks: list[MultiAgentTask],
) -> list[ResearchFinding]:
    role_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}

    for task in tasks:
        role = task.get("assigned_role", "unknown")
        status = task.get("status", "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1

    base_findings: list[ResearchFinding] = [
        {
            "title": "Planner output is available",
            "summary": "Day54 Researcher runs on top of Day53 Planner output instead of creating a new workflow from scratch.",
            "evidence": [
                f"objective={objective}",
                f"planning_mode={planning_mode}",
                f"task_count={len(tasks)}",
            ],
            "confidence": "high",
            "tags": ["planner_output", "multi_agent_state"],
        },
        {
            "title": "Researcher boundary is planning-context analysis only",
            "summary": "Researcher produces deterministic findings and artifacts, but does not execute Tool, Critic, or Supervisor graph logic.",
            "evidence": [
                "llm_used=false",
                "execution_boundary=research_only",
                "Tool / Critic / Supervisor remain unexecuted.",
            ],
            "confidence": "high",
            "tags": ["boundary", "ci_safe"],
        },
        {
            "title": "Task distribution is ready for later agents",
            "summary": "The planner-created task list already contains role assignments that future agents can consume.",
            "evidence": [
                f"role_counts={role_counts}",
                f"status_counts={status_counts}",
            ],
            "confidence": "high",
            "tags": ["task_distribution", "future_agents"],
        },
    ]

    if planning_mode == "implementation":
        base_findings.append(
            {
                "title": "Implementation task should be handled by Tool Agent later",
                "summary": "The researcher can inspect interfaces and constraints, but code changes should remain delegated to the future Tool Agent.",
                "evidence": [
                    "Implementation plans usually include researcher, tool, critic, and reflection roles.",
                    "Day54 must not execute Tool Agent.",
                ],
                "confidence": "high",
                "tags": ["implementation", "tool_agent_deferred"],
            }
        )
    elif planning_mode == "debugging":
        base_findings.append(
            {
                "title": "Debugging workflow needs reproduction before fixing",
                "summary": "For debugging requests, the researcher should identify likely failure scope but leave actual command execution to the future Tool Agent.",
                "evidence": [
                    "Reproduction and validation require tool execution.",
                    "Day54 is research-only.",
                ],
                "confidence": "medium",
                "tags": ["debugging", "tool_agent_deferred"],
            }
        )
    elif planning_mode == "documentation":
        base_findings.append(
            {
                "title": "Documentation workflow needs consistency checks",
                "summary": "Documentation updates should keep README, HANDOFF, Day docs, completed status, next milestone, and roadmap consistent.",
                "evidence": [
                    "Prior Day51-Day53 work required explicit bottom-section roadmap updates.",
                    "Day54 should continue preserving roadmap consistency.",
                ],
                "confidence": "high",
                "tags": ["documentation", "roadmap"],
            }
        )
    else:
        base_findings.append(
            {
                "title": "General workflow should stay incremental",
                "summary": "The current Multi-Agent implementation should continue adding one deterministic role at a time.",
                "evidence": [
                    "Day52 added state.",
                    "Day53 added planner.",
                    "Day54 adds researcher only.",
                ],
                "confidence": "high",
                "tags": ["incremental_delivery"],
            }
        )

    return base_findings


def _render_research_artifact(
    *,
    objective: str,
    planning_mode: str,
    researcher_task: MultiAgentTask,
    findings: list[ResearchFinding],
) -> str:
    lines = [
        "# Deterministic Research Notes",
        "",
        f"Objective: {objective}",
        f"Planning mode: {planning_mode}",
        f"Research task: {researcher_task['title']}",
        f"Research task id: {researcher_task['task_id']}",
        "",
        "## Findings",
        "",
    ]

    for index, finding in enumerate(findings, start=1):
        lines.extend(
            [
                f"{index}. {finding['title']}",
                f"   - summary: {finding['summary']}",
                f"   - confidence: {finding['confidence']}",
                f"   - tags: {', '.join(finding['tags'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Boundary",
            "",
            "- Researcher is deterministic and LLM-free.",
            "- Researcher only produces findings and artifacts.",
            "- Tool / Critic / Supervisor graph are not executed in Day54.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def run_deterministic_research(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = build_deterministic_plan(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    planner_memory = state["memory"]["planner"]
    planning_mode = planner_memory["planning_mode"]

    researcher_task = _ensure_researcher_task(
        state=state,
        objective=task,
        planning_mode=planning_mode,
    )

    state["current_role"] = "researcher"
    state["status"] = "pending"

    researcher_task["status"] = "running"
    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="researcher",
            message="Researcher started deterministic context analysis.",
            metadata={
                "task_id": researcher_task["task_id"],
                "planning_mode": planning_mode,
                "llm_used": False,
            },
        )
    )

    findings = _build_findings(
        objective=task,
        planning_mode=planning_mode,
        tasks=state["tasks"],
    )

    researcher_task["status"] = "completed"
    researcher_task["result"] = "Deterministic researcher produced research findings and a research artifact."
    researcher_task["metadata"] = {
        **researcher_task.get("metadata", {}),
        "research_completed": True,
        "finding_count": len(findings),
        "llm_used": False,
    }

    next_role = _find_next_pending_role_after_researcher(state)

    researcher_output: ResearcherOutput = {
        "researcher_role": "researcher",
        "planning_mode": planning_mode,
        "objective": task,
        "source_task_id": researcher_task["task_id"],
        "findings": findings,
        "constraints_checked": [
            "Researcher is deterministic and LLM-free.",
            "Tool / Critic / Supervisor graph are not executed in Day54.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "next_role": next_role,
        "execution_boundary": "research_only",
        "llm_used": False,
        "note": "Day54 executes only the Researcher step on top of Day53 Planner output.",
    }

    state["memory"]["researcher"] = researcher_output

    research_artifact: MultiAgentArtifact = create_multi_agent_artifact(
        name="deterministic_research_notes",
        artifact_type="markdown",
        content=_render_research_artifact(
            objective=task,
            planning_mode=planning_mode,
            researcher_task=researcher_task,
            findings=findings,
        ),
        created_by="researcher",
        metadata={
            "planning_mode": planning_mode,
            "source_task_id": researcher_task["task_id"],
            "finding_count": len(findings),
            "llm_used": False,
        },
    )
    state["artifacts"].append(research_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="researcher",
            message="Researcher added deterministic research artifact.",
            metadata={
                "artifact_id": research_artifact["artifact_id"],
                "artifact_type": research_artifact["artifact_type"],
                "source_task_id": researcher_task["task_id"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed",
            role="researcher",
            message="Researcher completed deterministic context analysis.",
            metadata={
                "task_id": researcher_task["task_id"],
                "planning_mode": planning_mode,
                "finding_count": len(findings),
                "llm_used": False,
            },
        )
    )

    return state