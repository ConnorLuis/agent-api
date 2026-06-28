from typing import Literal

from pydantic import BaseModel, Field

class LLMChatRequest(BaseModel):
    message: str = Field(..., description="User input message")
    provider: Literal["mock", "ollama"] | None = Field(
        default=None,
        description="Optional LLM provider override",
    )

class LLMChatResponse(BaseModel):
    answer: str
    provider: str
    model:  str
    trace_id: str | None = None