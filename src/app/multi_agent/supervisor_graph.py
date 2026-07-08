from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.app.multi_agent.reflection_agent import run_deterministic_reflection_agent
from src.app.multi_agent.state import (
    MultiAgentArtifact,
    MultiAgentState,
    MultiAgentTask,
    create_multi_agent_artifact,
    create_multi_agent_event,
    create_multi_agent_task,
)


SupervisorNodeStatus = Literal["completed", "skipped"]


class SupervisorGraphNode(TypedDict):
    node_id: str
    role: str
    status: SupervisorNodeStatus
    memory_key: str
    artifact_expected: bool
    summary: str


class SupervisorGraphEdge(TypedDict):
    source: str
    target: str
    condition: str


class SupervisorRoleReadiness(TypedDict):
    role: str
    memory_present: bool
    artifact_count: int
    completed_task_count: int
    ready: bool


class SupervisorGraphOutput(TypedDict):
    supervisor_role: str
    planning_mode: str
    objective: str
    source_task_id: str
    graph_name: str
    graph_version: str
    nodes: list[SupervisorGraphNode]
    edges: list[SupervisorGraphEdge]
    execution_order: list[str]
    role_readiness: list[SupervisorRoleReadiness]
    orchestration_pass: bool
    completed_role_count: int
    constraints_checked: list[str]
    preserved_debug_endpoints: list[str]
    next_role: str | None
    execution_boundary: str
    llm_used: bool
    note: str


def _find_pending_supervisor_task(state: MultiAgentState) -> MultiAgentTask | None:
    for task in state.get("tasks", []):
        if task.get("assigned_role") == "supervisor" and task.get("status") == "pending":
            return task
    return None


def _ensure_supervisor_task(
    state: MultiAgentState,
    *,
    objective: str,
    planning_mode: str,
) -> MultiAgentTask:
    supervisor_task = _find_pending_supervisor_task(state)
    if supervisor_task is not None:
        return supervisor_task

    supervisor_task = create_multi_agent_task(
        title="Orchestrate deterministic multi-agent graph",
        description=(
            "Run and validate the explicit Planner / Researcher / Tool / Critic / "
            f"Memory / Reflection graph for: {objective}"
        ),
        assigned_role="supervisor",
        status="pending",
        metadata={
            "created_by": "supervisor_fallback",
            "planning_mode": planning_mode,
            "reason": "No pending supervisor task existed before Day59 Supervisor graph.",
        },
    )
    state["tasks"].append(supervisor_task)
    state["events"].append(
        create_multi_agent_event(
            event_type="task_added",
            role="supervisor",
            message="Supervisor graph added fallback supervisor orchestration task.",
            metadata={
                "task_id": supervisor_task["task_id"],
                "planning_mode": planning_mode,
            },
        )
    )
    return supervisor_task


def _artifact_count_by_creator(state: MultiAgentState, creator: str) -> int:
    return sum(
        1
        for artifact in state.get("artifacts", [])
        if artifact.get("created_by") == creator
    )


def _completed_task_count_by_role(state: MultiAgentState, role: str) -> int:
    return sum(
        1
        for task in state.get("tasks", [])
        if task.get("assigned_role") == role and task.get("status") == "completed"
    )


def _build_supervisor_nodes(state: MultiAgentState) -> list[SupervisorGraphNode]:
    memory = state.get("memory", {})

    role_specs = [
        (
            "planner",
            "planner",
            "Planner decomposes the initial objective into deterministic role-assigned tasks.",
        ),
        (
            "researcher",
            "researcher",
            "Researcher analyzes planner context and produces deterministic findings.",
        ),
        (
            "tool",
            "tool",
            "Tool Agent simulates CI-safe implementation execution records.",
        ),
        (
            "critic",
            "critic",
            "Critic validates task transitions, memory outputs, artifacts, and boundaries.",
        ),
        (
            "memory",
            "memory",
            "Memory Agent summarizes Critic-approved workflow memory into state memory.",
        ),
        (
            "reflection",
            "reflection",
            "Reflection Agent reviews the completed deterministic role chain.",
        ),
    ]

    nodes: list[SupervisorGraphNode] = []
    for node_id, memory_key, summary in role_specs:
        nodes.append(
            {
                "node_id": node_id,
                "role": node_id,
                "status": "completed" if memory_key in memory else "skipped",
                "memory_key": memory_key,
                "artifact_expected": True,
                "summary": summary,
            }
        )

    return nodes


def _build_supervisor_edges() -> list[SupervisorGraphEdge]:
    return [
        {
            "source": "planner",
            "target": "researcher",
            "condition": "planner memory and deterministic plan are available",
        },
        {
            "source": "researcher",
            "target": "tool",
            "condition": "researcher findings are available",
        },
        {
            "source": "tool",
            "target": "critic",
            "condition": "tool execution records are available",
        },
        {
            "source": "critic",
            "target": "memory",
            "condition": "critic validation_pass is true",
        },
        {
            "source": "memory",
            "target": "reflection",
            "condition": "approved memory snapshot is available",
        },
    ]


def _build_role_readiness(state: MultiAgentState) -> list[SupervisorRoleReadiness]:
    readiness: list[SupervisorRoleReadiness] = []

    for role in ["planner", "researcher", "tool", "critic", "memory", "reflection"]:
        memory_present = role in state.get("memory", {})
        artifact_count = _artifact_count_by_creator(state, role)
        completed_task_count = _completed_task_count_by_role(state, role)

        readiness.append(
            {
                "role": role,
                "memory_present": memory_present,
                "artifact_count": artifact_count,
                "completed_task_count": completed_task_count,
                "ready": (
                    memory_present
                    and artifact_count >= 1
                    and completed_task_count >= 1
                ),
            }
        )

    return readiness


def _render_supervisor_artifact(
    *,
    objective: str,
    planning_mode: str,
    supervisor_task: MultiAgentTask,
    nodes: list[SupervisorGraphNode],
    edges: list[SupervisorGraphEdge],
    role_readiness: list[SupervisorRoleReadiness],
    orchestration_pass: bool,
) -> str:
    lines = [
        "# Deterministic Supervisor Graph Report",
        "",
        f"Objective: {objective}",
        f"Planning mode: {planning_mode}",
        f"Supervisor task: {supervisor_task['title']}",
        f"Supervisor task id: {supervisor_task['task_id']}",
        f"Orchestration pass: {orchestration_pass}",
        "",
        "## Nodes",
        "",
    ]

    for index, node in enumerate(nodes, start=1):
        lines.extend(
            [
                f"{index}. {node['node_id']}",
                f"   - role: {node['role']}",
                f"   - status: {node['status']}",
                f"   - memory_key: {node['memory_key']}",
                f"   - summary: {node['summary']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Edges",
            "",
        ]
    )

    for index, edge in enumerate(edges, start=1):
        lines.extend(
            [
                f"{index}. {edge['source']} -> {edge['target']}",
                f"   - condition: {edge['condition']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Role readiness",
            "",
        ]
    )

    for item in role_readiness:
        lines.extend(
            [
                f"- {item['role']}: ready={item['ready']}, "
                f"memory_present={item['memory_present']}, "
                f"artifact_count={item['artifact_count']}, "
                f"completed_task_count={item['completed_task_count']}",
            ]
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Supervisor graph is deterministic and LLM-free.",
            "- Supervisor graph orchestrates existing role-specific deterministic agents.",
            "- Existing role-specific debug endpoints are preserved.",
            "- Supervisor graph does not connect to external tools, storage, or Neo4j.",
            "- graph_fusion remains a non-default retrieval backend.",
        ]
    )

    return "\n".join(lines)


def run_deterministic_supervisor_graph(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> MultiAgentState:
    state = run_deterministic_reflection_agent(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    planner_memory = state["memory"]["planner"]
    planning_mode = planner_memory["planning_mode"]

    supervisor_task = _ensure_supervisor_task(
        state=state,
        objective=task,
        planning_mode=planning_mode,
    )

    state["current_role"] = "supervisor"
    state["status"] = "completed"

    supervisor_task["status"] = "running"
    state["events"].append(
        create_multi_agent_event(
            event_type="task_started",
            role="supervisor",
            message="Supervisor graph started deterministic orchestration validation.",
            metadata={
                "task_id": supervisor_task["task_id"],
                "planning_mode": planning_mode,
                "llm_used": False,
            },
        )
    )

    nodes = _build_supervisor_nodes(state)
    edges = _build_supervisor_edges()
    execution_order = [node["node_id"] for node in nodes]
    role_readiness = _build_role_readiness(state)

    orchestration_pass = (
        execution_order
        == ["planner", "researcher", "tool", "critic", "memory", "reflection"]
        and all(node["status"] == "completed" for node in nodes)
        and all(item["ready"] for item in role_readiness)
        and state["memory"]["critic"].get("validation_pass") is True
        and state["memory"]["memory"].get("approved") is True
        and state["memory"]["reflection"]["readiness_summary"]["supervisor_readiness"][
            "ready_for_supervisor_graph_next"
        ]
        is True
    )

    supervisor_task["status"] = "completed" if orchestration_pass else "failed"
    supervisor_task["result"] = (
        "Deterministic Supervisor graph completed orchestration validation."
        if orchestration_pass
        else "Deterministic Supervisor graph found orchestration validation failures."
    )
    supervisor_task["metadata"] = {
        **supervisor_task.get("metadata", {}),
        "supervisor_completed": orchestration_pass,
        "orchestration_pass": orchestration_pass,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "completed_role_count": sum(1 for node in nodes if node["status"] == "completed"),
        "llm_used": False,
    }

    supervisor_output: SupervisorGraphOutput = {
        "supervisor_role": "supervisor",
        "planning_mode": planning_mode,
        "objective": task,
        "source_task_id": supervisor_task["task_id"],
        "graph_name": "deterministic_multi_agent_supervisor_graph",
        "graph_version": "day59_supervisor_graph_v1",
        "nodes": nodes,
        "edges": edges,
        "execution_order": execution_order,
        "role_readiness": role_readiness,
        "orchestration_pass": orchestration_pass,
        "completed_role_count": sum(
            1 for node in nodes if node["status"] == "completed"
        ),
        "constraints_checked": [
            "Supervisor graph is deterministic and LLM-free.",
            "Supervisor graph orchestrates Planner / Researcher / Tool / Critic / Memory / Reflection.",
            "Existing role-specific debug endpoints are preserved.",
            "Supervisor graph does not use external tools or external storage in Day59.",
            "Supervisor graph does not connect Multi-Agent to Neo4j in Day59.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "preserved_debug_endpoints": [
            "/multi-agent/plan-debug",
            "/multi-agent/research-debug",
            "/multi-agent/tool-debug",
            "/multi-agent/critic-debug",
            "/multi-agent/memory-debug",
            "/multi-agent/reflection-debug",
        ],
        "next_role": None,
        "execution_boundary": "supervisor_orchestration_only",
        "llm_used": False,
        "note": "Day59 executes a deterministic Supervisor graph on top of Day58 Reflection Agent state flow.",
    }

    state["memory"]["supervisor"] = supervisor_output

    supervisor_artifact: MultiAgentArtifact = create_multi_agent_artifact(
        name="deterministic_supervisor_graph_report",
        artifact_type="markdown",
        content=_render_supervisor_artifact(
            objective=task,
            planning_mode=planning_mode,
            supervisor_task=supervisor_task,
            nodes=nodes,
            edges=edges,
            role_readiness=role_readiness,
            orchestration_pass=orchestration_pass,
        ),
        created_by="supervisor",
        metadata={
            "planning_mode": planning_mode,
            "source_task_id": supervisor_task["task_id"],
            "orchestration_pass": orchestration_pass,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "llm_used": False,
        },
    )
    state["artifacts"].append(supervisor_artifact)

    state["events"].append(
        create_multi_agent_event(
            event_type="artifact_added",
            role="supervisor",
            message="Supervisor graph added deterministic orchestration artifact.",
            metadata={
                "artifact_id": supervisor_artifact["artifact_id"],
                "artifact_type": supervisor_artifact["artifact_type"],
                "source_task_id": supervisor_task["task_id"],
            },
        )
    )

    state["events"].append(
        create_multi_agent_event(
            event_type="task_completed" if orchestration_pass else "task_failed",
            role="supervisor",
            message=(
                "Supervisor graph completed deterministic orchestration validation."
                if orchestration_pass
                else "Supervisor graph found deterministic orchestration failures."
            ),
            metadata={
                "task_id": supervisor_task["task_id"],
                "planning_mode": planning_mode,
                "orchestration_pass": orchestration_pass,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "llm_used": False,
            },
        )
    )

    return state