from __future__ import annotations

import inspect
from dataclasses import asdict, is_dataclass
from typing import Any

from src.app.graph.extraction import extract_graph_items
from src.app.graph.retrieval import run_graph_retrieval_debug
from src.app.multi_agent.streaming import build_multi_agent_stream_events
from src.app.multi_agent.supervisor_graph import run_deterministic_supervisor_graph


SUPPORTED_ENDPOINT_PROBE_IDS = (
    "graph_extract_debug",
    "graph_retrieval_debug",
    "multi_agent_supervisor_debug",
    "multi_agent_stream",
    "observability_traces",
    "observability_trace_detail",
)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}

    if isinstance(value, list | tuple | set):
        return [_jsonable(item) for item in value]

    if is_dataclass(value):
        return _jsonable(asdict(value))

    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump())

    if hasattr(value, "dict"):
        return _jsonable(value.dict())

    return repr(value)


def _call_with_supported_kwargs(func, **kwargs):
    signature = inspect.signature(func)
    accepted_kwargs = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }
    return func(**accepted_kwargs)


def _summarize_graph_extraction(payload: dict[str, Any]) -> dict[str, Any]:
    counts = payload.get("counts") or payload.get("summary") or {}

    return {
        "documents": counts.get("documents", len(payload.get("documents", []))),
        "chunks": counts.get("chunks", len(payload.get("chunks", []))),
        "entities": counts.get("entities", len(payload.get("entities", []))),
        "relations": counts.get("relations", len(payload.get("relations", []))),
        "write_executed": False,
        "neo4j_required": False,
    }


def _summarize_graph_retrieval(payload: dict[str, Any]) -> dict[str, Any]:
    execution = payload.get("execution", {})
    counts = execution.get("counts", {})

    return {
        "query_entity_match_count": len(payload.get("query_entity_matches", [])),
        "matched_entity_count": counts.get(
            "matched_entities",
            len(payload.get("matched_entities", [])),
        ),
        "chunk_count": counts.get("chunks", len(payload.get("chunks", []))),
        "related_entity_count": counts.get(
            "related_entities",
            len(payload.get("related_entities", [])),
        ),
        "dry_run": payload.get("dry_run", True),
        "status": execution.get("status", "dry_run"),
        "live_neo4j_required": False,
    }


def _summarize_supervisor(payload: dict[str, Any]) -> dict[str, Any]:
    supervisor = payload.get("memory", {}).get("supervisor", {})
    summary = payload.get("summary", {})

    return {
        "current_role": payload.get("current_role"),
        "status": payload.get("status"),
        "task_count": summary.get("task_count", len(payload.get("tasks", []))),
        "event_count": summary.get("event_count", len(payload.get("events", []))),
        "artifact_count": summary.get("artifact_count", len(payload.get("artifacts", []))),
        "orchestration_pass": supervisor.get("orchestration_pass"),
        "completed_role_count": supervisor.get("completed_role_count"),
        "llm_used": supervisor.get("llm_used", False),
    }


def _summarize_stream_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts: dict[str, int] = {}
    streamed_roles: list[str] = []

    for event in events:
        event_type = event.get("event")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

        data = event.get("data", {})
        role = data.get("role")
        if event_type == "role" and role:
            streamed_roles.append(role)

    return {
        "event_count": len(events),
        "event_counts": event_counts,
        "streamed_roles": streamed_roles,
        "llm_used": False,
        "streaming_mode": "deterministic_replay_summary",
    }


def _call_observability_rest_endpoint(
    *,
    path: str,
    trace_id: str,
) -> dict[str, Any]:
    from fastapi.testclient import TestClient

    from src.app.main import app

    with TestClient(app) as client:
        response = client.get(
            path,
            headers={"x-trace-id": trace_id},
        )

    try:
        body = response.json()
    except ValueError:
        body = {"text": response.text}

    return {
        "status_code": response.status_code,
        "ok": 200 <= response.status_code < 300,
        "body": body,
    }


def _extract_trace_items(body: Any) -> list[Any]:
    if isinstance(body, list):
        return body

    if not isinstance(body, dict):
        return []

    for key in ("traces", "items", "events", "results", "data"):
        value = body.get(key)
        if isinstance(value, list):
            return value

    return []


def _extract_trace_id_from_item(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None

    for key in ("trace_id", "id"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value

    payload = item.get("payload")
    if isinstance(payload, dict):
        value = payload.get("trace_id")
        if isinstance(value, str) and value:
            return value

    return None


def _summarize_observability_traces(payload: dict[str, Any]) -> dict[str, Any]:
    body = payload.get("body")
    trace_items = _extract_trace_items(body)

    return {
        "status_code": payload.get("status_code"),
        "ok": payload.get("ok", False),
        "trace_item_count": len(trace_items),
        "read_only": True,
        "live_neo4j_required": False,
    }


def _summarize_observability_trace_detail(payload: dict[str, Any]) -> dict[str, Any]:
    body = payload.get("body")
    trace_found = payload.get("ok", False)

    event_count = 0
    if isinstance(body, dict):
        events = body.get("events")
        if isinstance(events, list):
            event_count = len(events)
        elif isinstance(body.get("trace"), list):
            event_count = len(body["trace"])
    elif isinstance(body, list):
        event_count = len(body)

    return {
        "status_code": payload.get("status_code"),
        "ok": payload.get("ok", False),
        "trace_found": trace_found,
        "event_count": event_count,
        "read_only": True,
        "live_neo4j_required": False,
    }


def build_mcp_endpoint_probe_report(
    *,
    endpoint_id: str,
    trace_id: str,
    query: str = "RAG 和 LangGraph 有什么关系？",
    task: str = "Implement a CI-safe Agentic RAG feature and validate it.",
    thread_id: str = "mcp-endpoint-probe-thread",
    source_filter: str = "agent_basics",
    max_chars: int = 300,
    include_related_entities: bool = True,
    dry_run: bool = True,
    target_trace_id: str | None = None,
    trace_limit: int = 20,
) -> dict[str, Any]:
    if endpoint_id not in SUPPORTED_ENDPOINT_PROBE_IDS:
        return {
            "report_name": "agent-api MCP endpoint probe report",
            "report_version": "day71_mcp_endpoint_probe_report_v1",
            "endpoint_id": endpoint_id,
            "trace_id": trace_id,
            "allowed": False,
            "status": "unsupported_endpoint_probe",
            "supported_endpoint_ids": list(SUPPORTED_ENDPOINT_PROBE_IDS),
            "safety": {
                "ci_safe": True,
                "read_only": True,
                "dry_run_enforced": True,
                "write_executed": False,
                "live_neo4j_required": False,
                "rest_endpoint_behavior_changed": False,
            },
        }

    dry_run = True

    if endpoint_id == "graph_extract_debug":
        result = _call_with_supported_kwargs(
            extract_graph_items,
            source_filter=source_filter,
            max_chars=max_chars,
            include_related_entities=include_related_entities,
        )
        result_payload = _jsonable(result)
        summary = _summarize_graph_extraction(result_payload)

    elif endpoint_id == "graph_retrieval_debug":
        result = _call_with_supported_kwargs(
            run_graph_retrieval_debug,
            query=query,
            trace_id=trace_id,
            dry_run=dry_run,
            related_entity_limit=10,
            chunk_limit=3,
        )
        result_payload = _jsonable(result)
        summary = _summarize_graph_retrieval(result_payload)

    elif endpoint_id == "multi_agent_supervisor_debug":
        result = _call_with_supported_kwargs(
            run_deterministic_supervisor_graph,
            task=task,
            thread_id=thread_id,
            trace_id=trace_id,
        )
        result_payload = _jsonable(result)
        summary = _summarize_supervisor(result_payload)

    elif endpoint_id == "multi_agent_stream":
        events = _call_with_supported_kwargs(
            build_multi_agent_stream_events,
            task=task,
            thread_id=thread_id,
            trace_id=trace_id,
        )
        result_payload = _jsonable(events)
        summary = _summarize_stream_events(result_payload)

    elif endpoint_id == "observability_traces":
        result_payload = _call_observability_rest_endpoint(
            path=f"/observability/traces?limit={trace_limit}",
            trace_id=trace_id,
        )
        summary = _summarize_observability_traces(result_payload)

    elif endpoint_id == "observability_trace_detail":
        selected_trace_id = target_trace_id

        if not selected_trace_id:
            list_payload = _call_observability_rest_endpoint(
                path=f"/observability/traces?limit={trace_limit}",
                trace_id=trace_id,
            )
            trace_items = _extract_trace_items(list_payload.get("body"))
            for item in trace_items:
                selected_trace_id = _extract_trace_id_from_item(item)
                if selected_trace_id:
                    break

        selected_trace_id = selected_trace_id or trace_id

        result_payload = _call_observability_rest_endpoint(
            path=f"/observability/traces/{selected_trace_id}",
            trace_id=trace_id,
        )
        result_payload["target_trace_id"] = selected_trace_id
        summary = _summarize_observability_trace_detail(result_payload)

    else:
        raise AssertionError(f"unhandled endpoint probe id: {endpoint_id}")

    return {
        "report_name": "agent-api MCP endpoint probe report",
        "report_version": "day71_mcp_endpoint_probe_report_v1",
        "endpoint_id": endpoint_id,
        "trace_id": trace_id,
        "allowed": True,
        "status": "completed",
        "probe": {
            "query": query,
            "task": task,
            "thread_id": thread_id,
            "source_filter": source_filter,
            "dry_run": dry_run,
            "target_trace_id": target_trace_id,
            "trace_limit": trace_limit,
        },
        "summary": summary,
        "result": result_payload,
        "safety": {
            "ci_safe": True,
            "read_only": True,
            "dry_run_enforced": True,
            "write_executed": False,
            "live_neo4j_required": False,
            "external_server_executed": False,
            "rest_endpoint_behavior_changed": False,
        },
    }
