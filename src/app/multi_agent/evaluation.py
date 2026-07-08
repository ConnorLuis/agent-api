from __future__ import annotations

from collections import Counter
from typing import Any, Literal, TypedDict

from src.app.multi_agent.streaming import build_multi_agent_stream_events
from src.app.multi_agent.supervisor_graph import run_deterministic_supervisor_graph
from src.app.rag.retrieval_backend_modules.normalization import DEFAULT_RETRIEVAL_BACKEND


EvalCheckStatus = Literal["passed", "failed", "warning"]


class MultiAgentEvalCheck(TypedDict):
    check_name: str
    status: EvalCheckStatus
    summary: str
    evidence: list[str]


class MultiAgentEvalReport(TypedDict):
    eval_role: str
    objective: str
    planning_mode: str
    eval_pass: bool
    checks: list[MultiAgentEvalCheck]
    passed_check_count: int
    warning_check_count: int
    failed_check_count: int
    constraints_checked: list[str]
    preserved_endpoints: list[str]
    execution_boundary: str
    llm_used: bool
    note: str


class MultiAgentTraceReport(TypedDict):
    trace_id: str
    thread_id: str
    task: str
    graph_name: str
    graph_version: str
    stream_event_count: int
    state_event_count: int
    stream_event_counts: dict[str, int]
    execution_order: list[str]
    streamed_roles: list[str]
    artifact_creators: list[str]
    role_readiness_summary: dict[str, bool]
    boundary_flags: dict[str, Any]


EXPECTED_GRAPH_ROLES = [
    "planner",
    "researcher",
    "tool",
    "critic",
    "memory",
    "reflection",
]

EXPECTED_STREAMED_ROLES = [
    "planner",
    "researcher",
    "tool",
    "critic",
    "memory",
    "reflection",
    "supervisor",
]

EXPECTED_STREAM_EVENT_SEQUENCE = (
    ["metadata", "graph"]
    + ["node"] * 6
    + ["edge"] * 5
    + ["role"] * 7
    + ["artifact"] * 7
    + ["final", "done"]
)

EXPECTED_GRAPH_EDGES = [
    ("planner", "researcher"),
    ("researcher", "tool"),
    ("tool", "critic"),
    ("critic", "memory"),
    ("memory", "reflection"),
]

EXPECTED_ROLE_DEBUG_ENDPOINTS = [
    "/multi-agent/plan-debug",
    "/multi-agent/research-debug",
    "/multi-agent/tool-debug",
    "/multi-agent/critic-debug",
    "/multi-agent/memory-debug",
    "/multi-agent/reflection-debug",
]

EXPECTED_PRESERVED_ENDPOINTS = [
    "/multi-agent/stream",
    "/multi-agent/supervisor-debug",
    *EXPECTED_ROLE_DEBUG_ENDPOINTS,
]


def _first_stream_event_data(
    stream_events: list[dict[str, Any]],
    event_name: str,
) -> dict[str, Any]:
    for event in stream_events:
        if event.get("event") == event_name:
            return event.get("data", {})
    return {}


def _stream_event_data_list(
    stream_events: list[dict[str, Any]],
    event_name: str,
) -> list[dict[str, Any]]:
    return [
        event.get("data", {})
        for event in stream_events
        if event.get("event") == event_name
    ]


def _append_check(
    checks: list[MultiAgentEvalCheck],
    *,
    check_name: str,
    passed: bool,
    summary: str,
    evidence: list[str],
    warning: bool = False,
) -> None:
    if passed:
        status: EvalCheckStatus = "passed"
    elif warning:
        status = "warning"
    else:
        status = "failed"

    checks.append(
        {
            "check_name": check_name,
            "status": status,
            "summary": summary,
            "evidence": evidence,
        }
    )


def _count_checks(
    checks: list[MultiAgentEvalCheck],
    status: EvalCheckStatus,
) -> int:
    return sum(1 for check in checks if check["status"] == status)


def _build_trace_report(
    *,
    state: dict[str, Any],
    stream_events: list[dict[str, Any]],
) -> MultiAgentTraceReport:
    supervisor = state["memory"]["supervisor"]

    stream_event_counts = Counter(
        event.get("event", "unknown") for event in stream_events
    )
    role_events = _stream_event_data_list(stream_events, "role")
    artifact_events = _stream_event_data_list(stream_events, "artifact")

    role_readiness_summary = {
        item["role"]: item["ready"]
        for item in supervisor.get("role_readiness", [])
    }

    return {
        "trace_id": state["trace_id"],
        "thread_id": state["thread_id"],
        "task": state["task"],
        "graph_name": supervisor["graph_name"],
        "graph_version": supervisor["graph_version"],
        "stream_event_count": len(stream_events),
        "state_event_count": len(state.get("events", [])),
        "stream_event_counts": dict(stream_event_counts),
        "execution_order": supervisor["execution_order"],
        "streamed_roles": [event.get("role") for event in role_events],
        "artifact_creators": [event.get("created_by") for event in artifact_events],
        "role_readiness_summary": role_readiness_summary,
        "boundary_flags": {
            "llm_used": False,
            "default_retrieval_backend": DEFAULT_RETRIEVAL_BACKEND,
            "graph_fusion_default_changed": False,
            "streaming_mode": _first_stream_event_data(
                stream_events, "metadata"
            ).get("streaming_mode"),
        },
    }


def _build_eval_checks(
    *,
    state: dict[str, Any],
    stream_events: list[dict[str, Any]],
    trace_report: MultiAgentTraceReport,
) -> list[MultiAgentEvalCheck]:
    supervisor = state["memory"]["supervisor"]

    checks: list[MultiAgentEvalCheck] = []

    metadata_event = _first_stream_event_data(stream_events, "metadata")
    graph_event = _first_stream_event_data(stream_events, "graph")
    final_event = _first_stream_event_data(stream_events, "final")
    done_event = _first_stream_event_data(stream_events, "done")

    node_events = _stream_event_data_list(stream_events, "node")
    edge_events = _stream_event_data_list(stream_events, "edge")
    role_events = _stream_event_data_list(stream_events, "role")
    artifact_events = _stream_event_data_list(stream_events, "artifact")

    stream_event_names = [event.get("event") for event in stream_events]

    supervisor_orchestration_ok = supervisor.get("orchestration_pass") is True
    _append_check(
        checks,
        check_name="supervisor_orchestration_pass",
        passed=supervisor_orchestration_ok,
        summary="Supervisor graph should complete deterministic orchestration successfully.",
        evidence=[
            f"orchestration_pass={supervisor.get('orchestration_pass')}",
            f"completed_role_count={supervisor.get('completed_role_count')}",
            f"graph_name={supervisor.get('graph_name')}",
        ],
    )

    graph_consistency_ok = (
        graph_event.get("graph_name") == supervisor.get("graph_name")
        and graph_event.get("graph_version") == supervisor.get("graph_version")
        and graph_event.get("execution_order") == supervisor.get("execution_order")
        and graph_event.get("orchestration_pass")
        == supervisor.get("orchestration_pass")
    )
    _append_check(
        checks,
        check_name="stream_graph_matches_supervisor",
        passed=graph_consistency_ok,
        summary="Stream graph event should match Supervisor graph output.",
        evidence=[
            f"stream_graph_name={graph_event.get('graph_name')}",
            f"supervisor_graph_name={supervisor.get('graph_name')}",
            f"stream_execution_order={graph_event.get('execution_order')}",
            f"supervisor_execution_order={supervisor.get('execution_order')}",
        ],
    )

    stream_sequence_ok = stream_event_names == EXPECTED_STREAM_EVENT_SEQUENCE
    _append_check(
        checks,
        check_name="stream_event_sequence",
        passed=stream_sequence_ok,
        summary="Stream should emit deterministic metadata / graph / node / edge / role / artifact / final / done events.",
        evidence=[
            f"stream_event_count={len(stream_events)}",
            f"expected_stream_event_count={len(EXPECTED_STREAM_EVENT_SEQUENCE)}",
            f"stream_event_names={stream_event_names}",
        ],
    )

    node_coverage_ok = [event.get("node_id") for event in node_events] == EXPECTED_GRAPH_ROLES
    _append_check(
        checks,
        check_name="node_coverage",
        passed=node_coverage_ok,
        summary="Stream node events should cover Planner / Researcher / Tool / Critic / Memory / Reflection.",
        evidence=[
            f"node_ids={[event.get('node_id') for event in node_events]}",
            f"expected_node_ids={EXPECTED_GRAPH_ROLES}",
        ],
    )

    edge_coverage_ok = [
        (event.get("source"), event.get("target")) for event in edge_events
    ] == EXPECTED_GRAPH_EDGES
    _append_check(
        checks,
        check_name="edge_coverage",
        passed=edge_coverage_ok,
        summary="Stream edge events should match the explicit Supervisor graph edges.",
        evidence=[
            f"edges={[(event.get('source'), event.get('target')) for event in edge_events]}",
            f"expected_edges={EXPECTED_GRAPH_EDGES}",
        ],
    )

    streamed_roles = [event.get("role") for event in role_events]
    role_sequence_ok = streamed_roles == EXPECTED_STREAMED_ROLES
    _append_check(
        checks,
        check_name="role_stream_sequence",
        passed=role_sequence_ok,
        summary="Stream role events should replay all deterministic roles in order.",
        evidence=[
            f"streamed_roles={streamed_roles}",
            f"expected_streamed_roles={EXPECTED_STREAMED_ROLES}",
        ],
    )

    role_readiness_ok = all(
        item.get("ready") is True
        for item in supervisor.get("role_readiness", [])
    ) and all(
        event.get("status") == "completed"
        and event.get("memory_present") is True
        and event.get("artifact_count", 0) >= 1
        and event.get("completed_task_count", 0) >= 1
        for event in role_events
    )
    _append_check(
        checks,
        check_name="role_readiness_consistency",
        passed=role_readiness_ok,
        summary="Supervisor role_readiness and stream role payloads should agree.",
        evidence=[
            f"supervisor_role_readiness={supervisor.get('role_readiness')}",
            f"stream_role_payloads={role_events}",
        ],
    )

    artifact_creators = [event.get("created_by") for event in artifact_events]
    artifact_coverage_ok = artifact_creators == EXPECTED_STREAMED_ROLES
    _append_check(
        checks,
        check_name="artifact_coverage",
        passed=artifact_coverage_ok,
        summary="Stream artifact events should cover all role artifacts including Supervisor.",
        evidence=[
            f"artifact_creators={artifact_creators}",
            f"expected_artifact_creators={EXPECTED_STREAMED_ROLES}",
        ],
    )

    terminal_events_ok = (
        len(stream_events) >= 2
        and stream_events[-2].get("event") == "final"
        and stream_events[-1].get("event") == "done"
        and final_event.get("orchestration_pass") is True
        and done_event.get("status") == "done"
        and done_event.get("trace_id") == state["trace_id"]
    )
    _append_check(
        checks,
        check_name="terminal_stream_events",
        passed=terminal_events_ok,
        summary="Stream should end with final and done events carrying the same trace_id.",
        evidence=[
            f"penultimate_event={stream_events[-2].get('event') if len(stream_events) >= 2 else None}",
            f"last_event={stream_events[-1].get('event') if stream_events else None}",
            f"final_orchestration_pass={final_event.get('orchestration_pass')}",
            f"done_status={done_event.get('status')}",
            f"done_trace_id={done_event.get('trace_id')}",
        ],
    )

    trace_identity_ok = (
        metadata_event.get("trace_id") == state["trace_id"]
        and final_event.get("trace_id") == state["trace_id"]
        and done_event.get("trace_id") == state["trace_id"]
        and metadata_event.get("thread_id") == state["thread_id"]
        and final_event.get("thread_id") == state["thread_id"]
    )
    _append_check(
        checks,
        check_name="trace_identity_consistency",
        passed=trace_identity_ok,
        summary="Metadata, final, and done stream events should preserve trace and thread identity.",
        evidence=[
            f"state_trace_id={state['trace_id']}",
            f"metadata_trace_id={metadata_event.get('trace_id')}",
            f"final_trace_id={final_event.get('trace_id')}",
            f"done_trace_id={done_event.get('trace_id')}",
            f"state_thread_id={state['thread_id']}",
            f"metadata_thread_id={metadata_event.get('thread_id')}",
            f"final_thread_id={final_event.get('thread_id')}",
        ],
    )

    boundary_flags_ok = (
        DEFAULT_RETRIEVAL_BACKEND == "hybrid"
        and supervisor.get("llm_used") is False
        and metadata_event.get("llm_used") is False
        and final_event.get("llm_used") is False
        and metadata_event.get("graph_fusion_default_changed") is False
        and final_event.get("graph_fusion_default_changed") is False
        and "graph_fusion remains a non-default retrieval backend."
        in supervisor.get("constraints_checked", [])
    )
    _append_check(
        checks,
        check_name="boundary_flags",
        passed=boundary_flags_ok,
        summary="Eval / trace should remain LLM-free and preserve graph_fusion non-default boundary.",
        evidence=[
            f"DEFAULT_RETRIEVAL_BACKEND={DEFAULT_RETRIEVAL_BACKEND}",
            f"supervisor_llm_used={supervisor.get('llm_used')}",
            f"metadata_llm_used={metadata_event.get('llm_used')}",
            f"final_llm_used={final_event.get('llm_used')}",
            f"metadata_graph_fusion_default_changed={metadata_event.get('graph_fusion_default_changed')}",
            f"final_graph_fusion_default_changed={final_event.get('graph_fusion_default_changed')}",
        ],
    )

    role_debug_endpoints_ok = (
        set(supervisor.get("preserved_debug_endpoints", []))
        == set(EXPECTED_ROLE_DEBUG_ENDPOINTS)
        and set(final_event.get("preserved_debug_endpoints", []))
        == set(EXPECTED_ROLE_DEBUG_ENDPOINTS)
    )
    _append_check(
        checks,
        check_name="debug_endpoint_contracts",
        passed=role_debug_endpoints_ok,
        summary="Existing role-specific debug endpoints should remain preserved.",
        evidence=[
            f"supervisor_preserved_debug_endpoints={supervisor.get('preserved_debug_endpoints')}",
            f"stream_final_preserved_debug_endpoints={final_event.get('preserved_debug_endpoints')}",
            f"expected_role_debug_endpoints={EXPECTED_ROLE_DEBUG_ENDPOINTS}",
        ],
    )

    state_completed_roles = [
        event.get("role")
        for event in state.get("events", [])
        if event.get("event_type") == "task_completed"
    ]
    state_event_sequence_ok = all(
        role in state_completed_roles
        for role in EXPECTED_STREAMED_ROLES
    )
    _append_check(
        checks,
        check_name="state_event_completion_coverage",
        passed=state_event_sequence_ok,
        summary="State trace should contain task_completed events for all deterministic roles.",
        evidence=[
            f"state_completed_roles={state_completed_roles}",
            f"expected_completed_roles={EXPECTED_STREAMED_ROLES}",
        ],
    )

    trace_report_ok = (
        trace_report["stream_event_count"] == len(EXPECTED_STREAM_EVENT_SEQUENCE)
        and trace_report["streamed_roles"] == EXPECTED_STREAMED_ROLES
        and trace_report["artifact_creators"] == EXPECTED_STREAMED_ROLES
        and trace_report["boundary_flags"]["default_retrieval_backend"] == "hybrid"
    )
    _append_check(
        checks,
        check_name="trace_report_consistency",
        passed=trace_report_ok,
        summary="Trace report should summarize stream events, roles, artifacts, and boundary flags.",
        evidence=[
            f"stream_event_count={trace_report['stream_event_count']}",
            f"streamed_roles={trace_report['streamed_roles']}",
            f"artifact_creators={trace_report['artifact_creators']}",
            f"boundary_flags={trace_report['boundary_flags']}",
        ],
    )

    return checks


def run_deterministic_multi_agent_eval_trace(
    task: str,
    *,
    thread_id: str,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = run_deterministic_supervisor_graph(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )
    stream_events = build_multi_agent_stream_events(
        task=task,
        thread_id=thread_id,
        trace_id=trace_id,
        metadata=metadata,
    )

    trace_report = _build_trace_report(
        state=state,
        stream_events=stream_events,
    )
    checks = _build_eval_checks(
        state=state,
        stream_events=stream_events,
        trace_report=trace_report,
    )

    passed_count = _count_checks(checks, "passed")
    warning_count = _count_checks(checks, "warning")
    failed_count = _count_checks(checks, "failed")
    eval_pass = failed_count == 0

    supervisor = state["memory"]["supervisor"]

    eval_report: MultiAgentEvalReport = {
        "eval_role": "multi_agent_eval_trace",
        "objective": task,
        "planning_mode": supervisor["planning_mode"],
        "eval_pass": eval_pass,
        "checks": checks,
        "passed_check_count": passed_count,
        "warning_check_count": warning_count,
        "failed_check_count": failed_count,
        "constraints_checked": [
            "Multi-Agent eval / trace is deterministic and LLM-free.",
            "Eval validates Supervisor graph output and stream output consistency.",
            "Eval validates role readiness, event sequence, artifact coverage, and boundary flags.",
            "Eval preserves /multi-agent/stream.",
            "Eval preserves role-specific debug endpoints and /multi-agent/supervisor-debug.",
            "graph_fusion remains a non-default retrieval backend.",
        ],
        "preserved_endpoints": EXPECTED_PRESERVED_ENDPOINTS,
        "execution_boundary": "multi_agent_eval_trace_only",
        "llm_used": False,
        "note": "Day61 executes deterministic eval / trace checks on top of Day60 Multi-Agent streaming.",
    }

    return {
        "state": state,
        "stream_events": stream_events,
        "trace_report": trace_report,
        "eval_report": eval_report,
    }