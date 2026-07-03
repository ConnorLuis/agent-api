from typing import Any

from pydantic import BaseModel


class TraceEventInfo(BaseModel):
    event_id: int
    trace_id: str
    event_type: str
    payload: dict[str, Any]
    created_at_ms: int


class TraceEventsResponse(BaseModel):
    trace_id: str
    total_events: int
    events: list[TraceEventInfo]


class TraceSummaryInfo(BaseModel):
    trace_id: str
    event_count: int
    last_event_at_ms: int


class TraceListResponse(BaseModel):
    limit: int
    traces: list[TraceSummaryInfo]