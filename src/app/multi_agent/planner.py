from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.app.multi_agent.state import (
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
    initialize_multi_agent_state,
)


PlanningMode = Literal[
    "implementation",
    "debugging",
    "research",
    "documentation",
    "review",
    "general",
]


class PlannerOutput(TypedDict):
    planner_role: str
    planning_mode: PlanningMode
    objective: str
    constraints: list[str]
    task_ids: list[str]
    next_role: str
    execution_boundary: str
    llm_used: bool
    note: str


def infer_planning_mode(task: str) -> PlanningMode:
    normalized = task.strip().lower()

    debugging_terms = [
        "报错",
        "失败",
        "修复",
        "debug",
        "traceback",
        "error",
        "failed",
        "test failure",
        "ci failed",
        "ci 红",
    ]
    implementation_terms = [
        "实现",
        "新增",
        "开发",
        "构建",
        "build",
        "add",
        "implement",
        "planner agent",
        "multi-agent",
    ]
    documentation_terms = [
        "readme",
        "handoff",
        "文档",
        "docs",
        "document",
        "生成day",
        "生成 day",
    ]
    research_terms = [
        "调研",
        "研究",
        "比较",
        "生成 day",
    ]
    research_terms = [
        "调研",
        "研究",
        "比较",
        "分析方案",
        "research",
        "compare",
    ]
    review_terms = [
        "review",
        "复盘",
        "检查",
        "评审",
        "总结",
    ]

    if any(term in normalized for term in debugging_terms):
        return "debugging"
    if any(term in normalized for term in implementation_terms):
        return "implementation"
    if any(term in normalized for term in documentation_terms):
        return "documentation"
    if any(term in normalized for term in research_terms):
        return "research"
    if any(term in normalized for term in review_terms):
        return "review"

    return "general"


def _build_task_specs(mode: PlanningMode, objective: str) -> list[dict[str, Any]]:
    if mode == "debugging":
        return [
            {
                "title": "Reproduce and isolate the failure",
                "description": f"Reproduce the reported issue and identify the smallest failing scope for: {objective}",
                "assigned_role": "tool",
            },
            {
                "title": "Inspect related context",
                "description": "Review relevant code, tests, logs, and recent changes before proposing a fix.",
                "assigned_role": "researcher",
            },
            {
                "title": "Prepare minimal fix plan",
                "description": "Convert the failure analysis into a minimal implementation plan.",
                "assigned_role": "planner",
            },
            {
                "title": "Validate the fix",
                "description": "Run targeted tests first, then full pytest if the targeted tests pass.",
                "assigned_role": "critic",
            },
            {
                "title": "Summarize debugging outcome",
                "description": "Summarize root cause, fix, validation, and remaining risks.",
                "assigned_role": "reflection",
            },
        ]

    if mode == "documentation":
        return [
            {
                "title": "Define documentation scope",
                "description": f"Identify which documents need to be updated for: {objective}",
                "assigned_role": "planner",
            },
            {
                "title": "Draft documentation update",
                "description": "Prepare concise documentation changes without changing runtime behavior.",
                "assigned_role": "tool",
            },
            {
                "title": "Check roadmap consistency",
                "description": "Verify README / HANDOFF / Day docs do not contradict the locked roadmap.",
                "assigned_role": "critic",
            },
            {
                "title": "Summarize documentation status",
                "description": "Summarize what changed and what the next milestone is.",
                "assigned_role": "reflection",
            },
        ]

    if mode == "research":
        return [
            {
                "title": "Clarify research question",
                "description": f"Turn the user request into a focused research question: {objective}",
                "assigned_role": "planner",
            },
            {
                "title": "Collect relevant evidence",
                "description": "Gather relevant project context or external references if explicitly needed.",
                "assigned_role": "researcher",
            },
            {
                "title": "Compare options",
                "description": "Compare candidate solutions by cost, risk, complexity, and project fit.",
                "assigned_role": "critic",
            },
            {
                "title": "Produce recommendation",
                "description": "Return a concrete recommendation and next action.",
                "assigned_role": "reflection",
            },
        ]

    if mode == "review":
        return [
            {
                "title": "Define review checklist",
                "description": f"Build a checklist for reviewing: {objective}",
                "assigned_role": "planner",
            },
            {
                "title": "Inspect implementation and tests",
                "description": "Review code paths, tests, docs, and behavior boundaries.",
                "assigned_role": "critic",
            },
            {
                "title": "Identify risks and gaps",
                "description": "List regressions, unclear boundaries, or missing validation.",
                "assigned_role": "critic",
            },
            {
                "title": "Prepare review summary",
                "description": "Summarize pass/fail status and recommended follow-up.",
                "assigned_role": "reflection",
            },
        ]

    if mode == "implementation":
        return [
            {
                "title": "Define implementation boundary",
                "description": f"Clarify scope, non-goals, and acceptance criteria for: {objective}",
                "assigned_role": "planner",
            },
            {
                "title": "Inspect existing interfaces",
                "description": "Review existing state, schemas, routes, and tests before editing code.",
                "assigned_role": "researcher",
            },
            {
                "title": "Implement minimal code changes",
                "description": "Apply the smallest code change that satisfies the planned interface.",
                "assigned_role": "tool",
            },
            {
                "title": "Validate behavior",
                "description": "Run targeted tests and full pytest, then check no unrelated defaults changed.",
                "assigned_role": "critic",
            },
            {
                "title": "Prepare handoff summary",
                "description": "Summarize files changed, tests passed, and next milestone.",
                "assigned_role": "reflection",
            },
        ]

    return [
        {
            "title": "Clarify objective",
            "description": f"Clarify the user objective and expected outcome: {objective}",
            "assigned_role": "planner",
        },
        {
            "title": "Collect context",
            "description": "Collect relevant project context before choosing an execution path.",
            "assigned_role": "researcher",
        },
        {
            "title": "Execute planned work",
            "description": "Execute the planned work in the smallest safe increment.",
            "assigned_role": "tool",
        },
        {
            "title": "Review result",
            "description": "Review the result against the original objective and project boundaries.",
            "assigned_role": "critic",
        },
    ]


def _render_plan_artifact(
    *,
    objective: str,
    mode: PlanningMode,
    planned_tasks: list[MultiAgentTask],
) -> str:
    lines = [
        "# Deterministic Multi-Agent Plan",
        "",
        f"Objective: {objective}",
        f"Planning mode: {mode}",
        "",
        "## Planned tasks",
        "",
    ]

    for index, task in enumerate(planned_tasks, start=1):
        lines.extend(
            [
                f"{index}. {task['title']}",
                f"   - role: {task['assigned_role']}",
                f"   - status: {task['status']}",
                f"   - task_id: {task['task_id']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Boundary",
            "",
            "- Planner is deterministic and LLM-free.",
            "- Researcher / Tool / Critic / Supervisor graph are not executed in Day53.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def build_deterministic_plan(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = initialize_multi_agent_state(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    mode = infer_planning_mode(task)
    state["current_role"] = "planner"
    state["status"] = "pending"

    initial_task = state["tasks"][0]
    initial_task["status"] = "completed"
    initial_task["result"] = "Deterministic planner generated a structured execution plan."
    initial_task["metadata"] = {
        **initial_task.get("metadata", {}),
        "planning_mode": mode,
        "planner_completed": True,
    }

    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="planner",
            message="Planner started deterministic task decomposition.",
            metadata={
                "planning_mode": mode,
                "llm_used": False,
            },
        )
    )

    planned_tasks: list[MultiAgentTask] = []
    for task_spec in _build_task_specs(mode, task):
        planned_task = create_multi_agent_task(
            title=task_spec["title"],
            description=task_spec["description"],
            assigned_role=task_spec["assigned_role"],
            status="pending",
            metadata={
                "created_by": "planner",
                "planning_mode": mode,
            },
        )
        planned_tasks.append(planned_task)
        state["tasks"].append(planned_task)
        state["events"].append(
            create_multi_agent_event(
                event_type="task_added",
                role="planner",
                message=f"Planner added task: {planned_task['title']}",
                metadata={
                    "task_id": planned_task["task_id"],
                    "assigned_role": planned_task["assigned_role"],
                },
            )
        )

    next_role = planned_tasks[0]["assigned_role"] if planned_tasks else "planner"

    planner_output: PlannerOutput = {
        "planner_role": "planner",
        "planning_mode": mode,
        "objective": task,
        "constraints": [
            "Planner is deterministic and LLM-free.",
            "Researcher / Tool / Critic / Supervisor graph are not executed in Day53.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "task_ids": [planned_task["task_id"] for planned_task in planned_tasks],
        "next_role": next_role,
        "execution_boundary": "planning_only",
        "llm_used": False,
        "note": "Day53 only creates a deterministic plan on top of Day52 state.",
    }

    state["memory"]["planner"] = planner_output

    plan_artifact = create_multi_agent_artifact(
        name="deterministic_multi_agent_plan",
        artifact_type="markdown",
        content=_render_plan_artifact(
            objective=task,
            mode=mode,
            planned_tasks=planned_tasks,
        ),
        created_by="planner",
        metadata={
            "planning_mode": mode,
            "llm_used": False,
        },
    )
    state["artifacts"].append(plan_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="planner",
            message="Planner added deterministic plan artifact.",
            metadata={
                "artifact_id": plan_artifact["artifact_id"],
                "artifact_type": plan_artifact["artifact_type"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed",
            role="planner",
            message="Planner completed deterministic task decomposition.",
            metadata={
                "planning_mode": mode,
                "planned_task_count": len(planned_tasks),
                "llm_used": False,
            },
        )
    )

    return state