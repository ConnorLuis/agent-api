from collections.abc import Iterator
from uuid import uuid4

from langchain_core.messages import HumanMessage

from src.app.agent.graph import invoke_agent
from src.app.agent.llm_graph import (
    _build_config,
    llm_agent_graph,
    serialize_message,
)
from src.app.agent.state import AgentState
from src.app.core.sse import sse_event


def _chunk_text(text: str, chunk_size: int = 8) -> Iterator[str]:
    """
    Split text into small chunks for deterministic streaming demos.
    """
    for index in range(0, len(text), chunk_size):
        yield text[index : index + chunk_size]


def stream_agent_events(message: str, thread_id: str | None, trace_id: str | None) -> Iterator[str]:
    """
    Stream deterministic Agent final answer as SSE chunks.

    This endpoint is stable and can be covered by pytest/CI.
    """
    final_thread_id = thread_id or f"debug-thread-{uuid4().hex[:8]}"

    yield sse_event("metadata", {"thread_id": final_thread_id, "trace_id": trace_id, "mode": "deterministic",},)

    result = invoke_agent(message=message, thread_id=final_thread_id)

    final_message = result["messages"][-1]
    answer = str(final_message.content)

    for chunk in _chunk_text(answer):
        yield sse_event("answer_chunk", {"content": chunk, "thread_id": final_thread_id, "trace_id": trace_id,},)

    yield  sse_event("final", {"answer": answer, "thread_id": final_thread_id, "trace_id": trace_id,},)
    yield sse_event("done", {"thread_id": final_thread_id, "trace_id": trace_id,},)


def stream_llm_agent_events(message: str, thread_id: str | None, trace_id: str | None) -> Iterator[str]:
    """
    Stream real LLM Tool Calling Agent graph updates as SSE events.

    This is graph-step streaming, not token-level streaming:
    - agent step
    - tools step
    - agent final step

    It is intended for local/manual Ollama verification.
    """
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    yield sse_event("metadata", {
        "thread_id": final_thread_id,
        "trace_id": trace_id,
        "mode": "llm_tool_calling",
    },)

    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    config = _build_config(final_thread_id)

    for update in llm_agent_graph.stream(
        initial_state,
        config=config,
        stream_mode="updates",
    ):
        for node_name, node_update in update.items():
            messages = node_update.get("messages", [])

            if not isinstance(messages, list):
                messages = [ messages]

            yield sse_event("step", {"node": node_name, "messages": [serialize_message(m) for m in messages], "thread_id": final_thread_id, "trace_id": trace_id,})


    final_state = llm_agent_graph.get_state(config).values
    final_messages = final_state["messages"]
    final_answer = str(final_messages[-1].content)

    yield sse_event("final", {"answer": final_answer, "thread_id": final_thread_id, "trace_id": trace_id,})
    yield sse_event("done", {"thread_id": final_thread_id, "trace_id": trace_id,})