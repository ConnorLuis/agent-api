from uuid import uuid4

from src.app.agent.llm_router import invoke_llm_router_agent
from src.app.agent.router_graph import invoke_router_agent


def _normalize_router_mode(router_mode: str | None) -> str:
    mode = (router_mode or "deterministic").strip().lower()

    if mode in {"llm", "llm_router", "llm-router"}:
        return "llm"

    return "deterministic"


def invoke_smart_agent(
    message: str,
    thread_id: str | None = None,
    router_mode: str = "deterministic",
    router_provider: str = "mock",
) -> dict:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"
    mode = _normalize_router_mode(router_mode)

    if mode == "llm":
        result = invoke_llm_router_agent(message=message, thread_id=final_thread_id, router_provider=router_provider)

        return {
            "answer": result["answer"],
            "route": result["route"],
            "route_reason": result["route_reason"],
            "router_mode": "llm",
            "router_provider": result["router_provider"],
            "router_model": result["router_model"],
            "thread_id": result["thread_id"],
        }

    result = invoke_router_agent(message=message, thread_id=final_thread_id)

    route = result["route"]

    return {
        "answer": result["final_answer"],
        "route": route,
        "route_reason": f"Deterministic router selected {route} by rule-based classification.",
        "router_mode": "deterministic",
        "router_provider": "deterministic",
        "router_model": "rule-based-router",
        "thread_id": result["thread_id"],
    }