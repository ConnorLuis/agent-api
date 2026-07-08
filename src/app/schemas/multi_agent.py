from typing import Any, Literal

from pydantic import BaseModel, Field


MultiAgentRole = Literal[
    "supervisor",
    "planner",
    "researcher",
    "tool",
    "critic",
    "memory",
    "reflection",
]

MultiAgentTaskStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
]


class MultiAgentStateDebugRequest(BaseModel):
    task: str = Field(..., min_length=1)
    thread_id: str = Field(default="multi-agent-debug-thread")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentStateDebugResponse(BaseModel):
    task: str
    thread_id: str
    trace_id: str
    current_role: MultiAgentRole
    status: MultiAgentTaskStatus
    tasks: list[dict[str, Any]]
    events: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    memory: dict[str, Any]
    summary: dict[str, Any]


class MultiAgentPlanDebugRequest(BaseModel):
    task: str = Field(..., min_length=1)
    thread_id: str = Field(default="multi-agent-plan-debug-thread")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentPlanDebugResponse(BaseModel):
    task: str
    thread_id: str
    trace_id: str
    current_role: MultiAgentRole
    status: MultiAgentTaskStatus
    planning_mode: str
    plan: dict[str, Any]
    tasks: list[dict[str, Any]]
    events: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    memory: dict[str, Any]
    summary: dict[str, Any]


class MultiAgentResearchDebugRequest(BaseModel):
    task: str = Field(..., min_length=1)
    thread_id: str = Field(default="multi-agent-research-debug-thread")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentResearchDebugResponse(BaseModel):
    task: str
    thread_id: str
    trace_id: str
    current_role: MultiAgentRole
    status: MultiAgentTaskStatus
    planning_mode: str
    research: dict[str, Any]
    tasks: list[dict[str, Any]]
    events: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    memory: dict[str, Any]
    summary: dict[str, Any]


class MultiAgentToolDebugRequest(BaseModel):
    task: str = Field(..., min_length=1)
    thread_id: str = Field(default="multi-agent-tool-debug-thread")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentToolDebugResponse(BaseModel):
    task: str
    thread_id: str
    trace_id: str
    current_role: MultiAgentRole
    status: MultiAgentTaskStatus
    planning_mode: str
    tool: dict[str, Any]
    tasks: list[dict[str, Any]]
    events: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    memory: dict[str, Any]
    summary: dict[str, Any]