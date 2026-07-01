from typing import Any
from pydantic import BaseModel, Field

class AgentChatRequest(BaseModel):
    message: str = Field(..., description="User input message")
    thread_id: str | None = Field(default=None, description="Conversation thread id")


class AgentChatResponse(BaseModel):
    answer: str
    thread_id: str | None = None
    trace_id: str | None = None


class DebugMessage(BaseModel):
    type: str
    content: str
    tool_calls: list[dict[str, Any]] | None =None
    name: str | None = None


class DebugStep(BaseModel):
    node:  str
    messages: list[DebugMessage]


class AgentDebugResponse(BaseModel):
    thread_id: str
    steps: list[DebugStep]
    final_answer: str
    messages_count: int
    trace_id: str | None = None


class AgentLLMChatResponse(BaseModel):
    answer: str
    thread_id: str | None = None
    provider: str = "ollama"
    model: str | None = None
    trace_id: str | None = None


class AgentRouterChatResponse(BaseModel):
    answer: str
    route:  str
    thread_id: str | None = None
    trace_id: str | None = None


class AgentRouterDebugResponse(BaseModel):
    thread_id: str
    route: str
    steps: list[DebugStep]
    final_answer: str
    messages_count: int
    trace_id: str | None = None
