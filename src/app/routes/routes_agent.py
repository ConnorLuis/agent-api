from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.app.agent.graph import debug_agent, invoke_agent
from src.app.agent.router_graph import debug_router_agent, invoke_router_agent
from src.app.agent.llm_graph import debug_llm_agent, invoke_llm_agent
from src.app.agent.streaming import stream_agent_events, stream_llm_agent_events
from src.app.core.config import get_settings
from src.app.core.request_context import get_trace_id
from src.app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentDebugResponse,
    AgentLLMChatResponse, AgentRouterChatResponse, AgentRouterDebugResponse,
)

router = APIRouter()


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    result = invoke_agent(
        message=request.message,
        thread_id=request.thread_id
    )

    final_message = result["messages"][-1]

    return AgentChatResponse(
        answer = str(final_message.content),
        thread_id = result.get("thread_id", request.thread_id),
        trace_id=get_trace_id(),
    )


@router.post("/debug", response_model=AgentDebugResponse)
def agent_debug(request: AgentChatRequest) -> AgentDebugResponse:
    result = debug_agent(
        message=request.message,
        thread_id=request.thread_id
    )

    return AgentDebugResponse(**result, trace_id=get_trace_id())


@router.post("/llm-chat", response_model=AgentLLMChatResponse)
def agent_llm_chat(request: AgentChatRequest) -> AgentLLMChatResponse:
    result = invoke_llm_agent(
        message=request.message,
        thread_id=request.thread_id
    )

    final_message = result["messages"][-1]

    return AgentLLMChatResponse(
        answer = str(final_message.content),
        thread_id = result.get("thread_id", request.thread_id),
        provider = "ollama",
        model = get_settings().ollama_model,
        trace_id=get_trace_id(),
    )


@router.post("/llm-debug", response_model=AgentDebugResponse)
def agent_llm_debug(request: AgentChatRequest) -> AgentDebugResponse:
    result = debug_llm_agent(
        message=request.message,
        thread_id=request.thread_id
    )

    return AgentDebugResponse(**result, trace_id=get_trace_id())


@router.post("/stream")
def agent_stream(request: AgentChatRequest) -> StreamingResponse:
    trace_id = get_trace_id()

    return StreamingResponse(
        stream_agent_events(
            message=request.message,
            thread_id=request.thread_id,
            trace_id=trace_id,
        ),
        media_type="text/event-stream",
    )


@router.post("/llm-stream")
def agent_llm_stream(request: AgentChatRequest) -> StreamingResponse:
    trace_id = get_trace_id()

    return StreamingResponse(
        stream_llm_agent_events(
            message=request.message,
            thread_id=request.thread_id,
            trace_id=trace_id,
        ),
        media_type="text/event-stream",
    )


@router.post("/router-chat", response_model=AgentRouterChatResponse)
def agent_router_chat(request: AgentChatRequest) -> AgentRouterChatResponse:
    result = invoke_router_agent(
        message=request.message,
        thread_id=request.thread_id,
    )

    return AgentRouterChatResponse(
        answer=result["final_answer"],
        route=result["route"],
        thread_id=result["thread_id"],
        trace_id=get_trace_id(),
    )


@router.post("/router-debug", response_model=AgentRouterDebugResponse)
def agent_router_debug(request: AgentChatRequest) -> AgentRouterDebugResponse:
    result = debug_router_agent(
        message=request.message,
        thread_id=request.thread_id,
    )

    return AgentRouterDebugResponse(
        **result,
        trace_id=get_trace_id(),
    )