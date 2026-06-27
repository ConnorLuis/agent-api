from fastapi import APIRouter

from src.app.agent.graph import invoke_agent
from src.app.schemas.agent import AgentChatRequest, AgentChatResponse

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
