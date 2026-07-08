from fastapi import APIRouter

from src.app.core.request_context import get_trace_id
from src.app.multi_agent.planner import build_deterministic_plan
from src.app.multi_agent.researcher import run_deterministic_research
from src.app.multi_agent.state import (
    initialize_multi_agent_state,
    summarize_multi_agent_state,
)
from src.app.multi_agent.tool_agent import run_deterministic_tool_agent
from src.app.schemas.multi_agent import (
    MultiAgentStateDebugRequest,
    MultiAgentStateDebugResponse, MultiAgentPlanDebugResponse, MultiAgentPlanDebugRequest,
    MultiAgentResearchDebugResponse, MultiAgentResearchDebugRequest, MultiAgentToolDebugResponse,
    MultiAgentToolDebugRequest,
)


router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])


@router.post("/state-debug", response_model=MultiAgentStateDebugResponse)
def debug_multi_agent_state(
    request: MultiAgentStateDebugRequest,
) -> MultiAgentStateDebugResponse:
    trace_id = get_trace_id()

    state = initialize_multi_agent_state(
        task=request.task,
        thread_id=request.thread_id,
        trace_id=trace_id,
        metadata=request.metadata,
    )

    return MultiAgentStateDebugResponse(
        task=state["task"],
        thread_id=state["thread_id"],
        trace_id=state["trace_id"],
        current_role=state["current_role"],
        status=state["status"],
        tasks=state["tasks"],
        events=state["events"],
        artifacts=state["artifacts"],
        memory=state["memory"],
        summary=summarize_multi_agent_state(state),
    )


@router.post("/plan-debug", response_model=MultiAgentPlanDebugResponse)
def debug_multi_agent_plan(
    request: MultiAgentPlanDebugRequest,
) -> MultiAgentPlanDebugResponse:
    trace_id = get_trace_id()

    state = build_deterministic_plan(
        task=request.task,
        thread_id=request.thread_id,
        trace_id=trace_id,
        metadata=request.metadata,
    )
    plan = state["memory"]["planner"]

    return MultiAgentPlanDebugResponse(
        task=state["task"],
        thread_id=state["thread_id"],
        trace_id=state["trace_id"],
        current_role=state["current_role"],
        status=state["status"],
        planning_mode=plan["planning_mode"],
        plan=plan,
        tasks=state["tasks"],
        events=state["events"],
        artifacts=state["artifacts"],
        memory=state["memory"],
        summary=summarize_multi_agent_state(state),
    )


@router.post("/research-debug", response_model=MultiAgentResearchDebugResponse)
def debug_multi_agent_research(
    request: MultiAgentResearchDebugRequest,
) -> MultiAgentResearchDebugResponse:
    trace_id = get_trace_id()

    state = run_deterministic_research(
        task=request.task,
        thread_id=request.thread_id,
        trace_id=trace_id,
        metadata=request.metadata,
    )
    research = state["memory"]["researcher"]

    return MultiAgentResearchDebugResponse(
        task=state["task"],
        thread_id=state["thread_id"],
        trace_id=state["trace_id"],
        current_role=state["current_role"],
        status=state["status"],
        planning_mode=research["planning_mode"],
        research=research,
        tasks=state["tasks"],
        events=state["events"],
        artifacts=state["artifacts"],
        memory=state["memory"],
        summary=summarize_multi_agent_state(state),
    )


@router.post("/tool-debug", response_model=MultiAgentToolDebugResponse)
def debug_multi_agent_tool(
    request: MultiAgentToolDebugRequest,
) -> MultiAgentToolDebugResponse:
    trace_id = get_trace_id()

    state = run_deterministic_tool_agent(
        task=request.task,
        thread_id=request.thread_id,
        trace_id=trace_id,
        metadata=request.metadata,
    )
    tool = state["memory"]["tool"]

    return MultiAgentToolDebugResponse(
        task=state["task"],
        thread_id=state["thread_id"],
        trace_id=state["trace_id"],
        current_role=state["current_role"],
        status=state["status"],
        planning_mode=tool["planning_mode"],
        tool=tool,
        tasks=state["tasks"],
        events=state["events"],
        artifacts=state["artifacts"],
        memory=state["memory"],
        summary=summarize_multi_agent_state(state),
    )