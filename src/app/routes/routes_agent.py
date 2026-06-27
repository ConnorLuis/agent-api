from fastapi import APIRouter

from src.app.schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter()


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    return AgentChatResponse(
        answer = f"Agent mock response: {request.message}",
        thread_id = request.thread_id
    )
