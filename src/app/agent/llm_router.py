import json
import re
from dataclasses import dataclass
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage

from src.app.agent.graph import invoke_agent
from src.app.agent.router_graph import _classify_route
from src.app.core.config import get_settings


VALID_ROUTES = {"calculator", "rag", "chat"}


@dataclass
class RouterDecision:
    route: str
    reason: str
    provider: str
    model: str


def _normalize_route(route: str) -> str:
    normalized = route.strip().lower()

    if normalized in VALID_ROUTES:
        return normalized

    return "chat"


def _get_final_answer_from_agent_result(result: dict) -> str:
    messages = result.get("messages", [])

    if not messages:
        return ""

    return str(messages[-1].content)


def _run_selected_route(message: str, thread_id: str, route: str) -> str:
    if route in {"calculator", "rag"}:
        result = invoke_agent(message=message, thread_id=thread_id)
        return _get_final_answer_from_agent_result(result)

    return f"Router chat response: {message}"


def _get_setting(name: str, default: str) -> str:
    value = getattr(get_settings(), name, None)

    if value is not None:
        return str(value)

    value = getattr(get_settings(), name.upper(), None)

    if value is not None:
        return str(value)

    return  default


def _parse_route_from_text(text: str) -> tuple[str, str]:
    content = text.strip()

    try:
        data = json.loads(content)
        route = _normalize_route(str(data.get("route", "chat")))
        reason = str(data.get("reason", "LLM router decision."))
        return route, reason
    except json.JSONDecodeError:
        pass

    match = re.search(r"\b(calculator|rag|chat)\b", content.lower())

    if match:
        route = _normalize_route(match.group(1))
        return route, content

    return "chat", "Failed to parse LLM router output, fallback to chat."


def classify_route_with_mock_llm(message: str) -> RouterDecision:
    route = _classify_route(message)

    reason_map = {
        "calculator": "Mock LLM router selected calculator because the message contains arithmetic intent.",
        "rag": "Mock LLM router selected rag because the message contains knowledge-base or retrieval intent.",
        "chat": "Mock LLM router selected chat because no tool-specific intent was detected.",
    }

    return RouterDecision(
        route=route,
        reason=reason_map[route],
        provider="mock",
        model="mock-router"
    )


def classify_router_with_ollama(message: str) -> RouterDecision:
    from langchain_ollama import ChatOllama

    base_url = _get_setting("ollama_base_url", "http://localhost:11434")
    model = _get_setting("ollama_model", "qwen2.5:7b")
    temperature = float(_get_setting("ollama_temperature", "0.0"))

    llm = ChatOllama(base_url=base_url, model=model, temperature=temperature)

    system_prompt = """
    You are a routing classifier for an Agent backend.

    Classify the user message into exactly one route:

    calculator:
    - arithmetic questions
    - addition, multiplication, numeric calculation

    rag:
    - knowledge base search
    - retrieval
    - RAG
    - LangGraph
    - Agent concept questions

    chat:
    - normal conversation
    - greetings
    - messages that do not need tools

    Return only valid JSON:
    {"route": "calculator|rag|chat", "reason": "short reason"}
    """.strip()

    response = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=message)]
    )

    route, reason = _parse_route_from_text(str(response.content))

    return RouterDecision(
        route=route,
        reason=reason,
        provider="ollama",
        model=model
    )


def classify_route_with_llm(message: str, router_provider: str = "mock") -> RouterDecision:
    provider = (router_provider or "mock").strip().lower()

    if provider == "ollama":
        return classify_router_with_ollama(message)

    return classify_route_with_mock_llm(message)


def invoke_llm_router_agent(message: str, thread_id: str | None = None, router_provider: str = "mock") -> dict:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    decision = classify_route_with_llm(message=message, router_provider=router_provider)

    answer = _run_selected_route(message=message, thread_id=final_thread_id, route=decision.route)

    return {
        "answer": answer,
        "route": decision.route,
        "route_reason": decision.reason,
        "router_provider": decision.provider,
        "router_model": decision.model,
        "thread_id": final_thread_id,
    }