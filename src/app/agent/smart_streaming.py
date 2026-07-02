from collections.abc import Generator

from src.app.agent.smart_router import invoke_smart_agent
from src.app.core.sse import sse_event


def stream_smart_agent_events(
    message: str,
    thread_id: str | None,
    router_mode: str,
    router_provider: str,
    trace_id: str | None,
) -> Generator[str, None, None]:
    result = invoke_smart_agent(
        message=message,
        thread_id=thread_id,
        router_mode=router_mode,
        router_provider=router_provider,
    )

    final_thread_id = result["thread_id"]
    route = result["route"]
    route_reason = result["route_reason"]
    final_router_mode = result["router_mode"]
    final_router_provider = result["router_provider"]
    final_router_model = result["router_model"]
    final_answer = result["answer"]

    yield sse_event(
        event="metadata",
        data={
            "thread_id": final_thread_id,
            "trace_id": trace_id,
            "router_mode": final_router_mode,
            "router_provider": final_router_provider,
            "router_model": final_router_model,
        }
    )

    yield sse_event(
        event="route",
        data={
            "route": route,
            "route_reason": route_reason,
            "router_mode": final_router_mode,
            "router_provider": final_router_provider,
            "router_model": final_router_model,
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="answer_chunk",
        data={
            "chunk": final_answer,
            "route": route,
            "router_mode": final_router_mode,
            "router_provider": final_router_provider,
            "router_model": final_router_model,
            "thread_id": final_thread_id,
            "trace_id": trace_id,
        },
    )

    yield sse_event(
        event="final",
        data={
            "answer": final_answer,
            "route": route,
            "route_reason": route_reason,
            "router_mode": final_router_mode,
            "router_provider": final_router_provider,
            "router_model": final_router_model,
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
