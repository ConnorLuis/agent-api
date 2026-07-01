from collections.abc import Generator

from src.app.agent.router_graph import invoke_router_agent
from src.app.core.sse import sse_event


def stream_router_agent_events(
    message: str,
    thread_id: str | None = None,
    trace_id: str | None = None,
) -> Generator[str, None, None]:
    result = invoke_router_agent(
        message=message,
        thread_id=thread_id,
    )

    final_thread_id = result["thread_id"]
    route = result["route"]
    final_answer = result["final_answer"]

    yield sse_event(
        event="metadata",
        data={
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="route",
        data={
            "route": route,
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="answer_chunk",
        data={
            "chunk": final_answer,
            "route": route,
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="final",
        data={
            "answer": final_answer,
            "route": route,
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="done",
        data={
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )