from fastapi import APIRouter

from fastapi import APIRouter

from src.app.observability.trace_store import (
    get_trace_events,
    list_recent_trace_ids,
)
from src.app.schemas.observability import (
    TraceEventsResponse,
    TraceListResponse,
)

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/traces", response_model=TraceListResponse)
def list_observability_traces(
    limit: int = 20,
) -> TraceListResponse:
    safe_limit = max(1, min(limit, 100))
    traces = list_recent_trace_ids(limit=safe_limit)

    return TraceListResponse(
        limit=safe_limit,
        traces=traces,
    )


@router.get("/traces/{trace_id}", response_model=TraceEventsResponse)
def get_observability_trace(
    trace_id: str,
) -> TraceEventsResponse:
    events = get_trace_events(trace_id=trace_id)

    return TraceEventsResponse(
        trace_id=trace_id,
        total_events=len(events),
        events=events,
    )