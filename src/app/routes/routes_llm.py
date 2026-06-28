from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from src.app.core.request_context import get_trace_id
from src.app.llm.base import LLMProviderError
from src.app.llm.factory import get_chat_provider
from src.app.schemas.llm import LLMChatRequest, LLMChatResponse

router = APIRouter()

@router.post("/chat", response_model=LLMChatResponse)
def llm_chat(request: LLMChatRequest) -> LLMChatResponse:
    try:
        provider = get_chat_provider(provider=request.provider)
        response = provider.invoke(
            [HumanMessage(content=request.message)]
        )
    except LLMProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return LLMChatResponse(
        answer=str(response.content),
        provider=provider.provider,
        model=provider.model_name,
        trace_id=get_trace_id(),
    )