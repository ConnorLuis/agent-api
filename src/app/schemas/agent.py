from pydantic import BaseModel, Field

class AgentChatRequest(BaseModel):
    message: str = Field(..., description="User input message")
    thread_id: str | None = Field(default=None, description="Conversation thread id")


class AgentChatResponse(BaseModel):
    answer: str
    thread_id: str | None = None