from uuid import uuid4

from src.app.agent.llm_router import invoke_llm_router_agent
from src.app.agent.router_graph import invoke_router_agent
from src.app.agent.route_validation import validate_route_decision


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
            "route_confidence": result["route_confidence"],
            "route_valid": result["route_valid"],
            "fallback_used": result["fallback_used"],
            "validation_reason": result["validation_reason"],
            "thread_id": result["thread_id"],
        }

    result = invoke_router_agent(message=message, thread_id=final_thread_id)

    route = result["route"]

    validation = validate_route_decision(
        route=route,
        router_provider="deterministic",
        fallback_route="chat",
    )

    return {
        "answer": result["final_answer"],
        "route": validation.route,
        "route_reason": (
            f"Deterministic router selected {validation.route} "
            "by rule-based classification."
        ),
        "router_mode": "deterministic",
        "router_provider": "deterministic",
        "router_model": "rule-based-router",
        "route_confidence": validation.route_confidence,
        "route_valid": validation.route_valid,
        "fallback_used": validation.fallback_used,
        "validation_reason": validation.validation_reason,
        "thread_id": result["thread_id"],
    }