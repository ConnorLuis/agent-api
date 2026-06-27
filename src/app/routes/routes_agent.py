from fastapi import APIRouter

from src.app.agent.graph import debug_agent, invoke_agent
from src.app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentDebugResponse
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
        thread_id = result.get("thread_id", request.thread_id)
    )


@router.post("/debug", response_model=AgentDebugResponse)
def agent_debug(request: AgentChatRequest) -> AgentDebugResponse:
    result = debug_agent(
        message=request.message,
        thread_id=request.thread_id
    )

    return AgentDebugResponse(**result)