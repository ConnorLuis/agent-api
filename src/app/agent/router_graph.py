import re
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from typing_extensions import NotRequired

from src.app.agent.graph import invoke_agent
from src.app.rag.retriever import search_knowledge

class RouterState(MessagesState):
    thread_id: str
    route: NotRequired[str]


def _extract_two_ints(text: str) -> tuple[int, int] | None:
    numbers = re.findall(r"-?\d+", text)
    if len(numbers) < 2:
        return None
    return int(numbers[0]), int(numbers[1])


def _classify_route(text: str) -> str:
    lowered = text.lower()

    has_two_ints = _extract_two_ints(text) is not None

    calculator_keywords = [
        "计算",
        "加",
        "+",
        "add",
        "乘",
        "*",
        "multiply",
    ]

    rag_keywords = [
        "rag",
        "知识库",
        "检索",
        "搜索",
        "langgraph",
        "agent是什么",
        "agent 是什么",
    ]

    if has_two_ints and any(keyword in lowered for keyword in calculator_keywords):
        return "calculator"

    if any(keyword in lowered for keyword in rag_keywords):
        return "rag"

    return "chat"


def _delegate_to_deterministic_agent(state: RouterState) -> str:
    last_message = state["messages"][-1]
    user_text = str(last_message.content)

    thread_id = state.get("thread_id") or f"router-child-{uuid4().hex[:8]}"

    result = invoke_agent(
        message=user_text,
        thread_id=thread_id,
    )

    return _get_final_answer_from_agent_result(result)

def _get_final_answer_from_agent_result(result: dict) -> str:
    messages = result.get("messages", [])

    if not messages:
        return ""

    return str(messages[-1].content)

def router_node(state: RouterState) -> dict:
    last_message = state["messages"][-1]
    user_text = str(last_message.content)

    route = _classify_route(user_text)

    return {
        route: route
    }


def route_condition(state: RouterState) -> str:
    last_message = state["messages"][-1]
    user_text = str(last_message.content)
    return _classify_route(user_text)


def calculator_node(state: RouterState) -> dict:
    answer = _delegate_to_deterministic_agent(state)

    return {
        "messages": [
            AIMessage(
                content=answer,
            )
        ]
    }


def rag_node(state: RouterState) -> dict:
    answer = _delegate_to_deterministic_agent(state)

    return {
        "messages": [
            AIMessage(
                content=answer,
            )
        ]
    }


def chat_node(state: RouterState) -> dict:
    last_message = state["messages"][-1]
    user_text = str(last_message.content)

    return {
        "messages": [
            AIMessage(
                content=f"Router chat response: {user_text}"
            )
        ]
    }


def builder_router_agent_graph():
    builder = StateGraph(RouterState)

    builder.add_node("router", router_node)
    builder.add_node("calculator", calculator_node)
    builder.add_node("rag", rag_node)
    builder.add_node("chat", chat_node)

    builder.add_edge(START, "router")

    builder.add_conditional_edges("router", route_condition, {"calculator": "calculator", "rag": "rag", "chat": "chat"},)

    builder.add_edge("calculator", END)
    builder.add_edge("rag", END)
    builder.add_edge("chat", END)

    return builder.compile()


router_agent_graph = builder_router_agent_graph()


def serialize_message(message: BaseMessage) -> dict:
    return {
        "type": message.__class__.__name__,
        "content": str(message.content),
        "tool_calls": getattr(message, "tool_calls", None),
        "name": getattr(message, "name", None),
    }


def invoke_router_agent(message: str, thread_id: str | None = None) -> dict:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"
    route = _classify_route(message)

    initial_state: RouterState = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    result = router_agent_graph.invoke(initial_state,)

    return {
        "thread_id": final_thread_id,
        "route": route,
        "messages": result["messages"],
        "final_answer": str(result["messages"][-1].content),
        "messages_count": len(result["messages"])
    }


def debug_router_agent(message: str, thread_id: str | None = None) -> dict:
    final_thread_id = thread_id or f"thread-{uuid4().hex[:8]}"

    initial_state = {
        "messages": [HumanMessage(content=message)],
        "thread_id": final_thread_id,
    }

    steps = []
    route = _classify_route(message)
    messages_count = 1
    final_answer = ""

    for update in router_agent_graph.stream(
        initial_state,
        stream_mode="updates",
    ):
        for node_name, node_update in update.items():
            if not isinstance(node_update, dict):
                node_update = {}

            if "route" in node_update:
                route = node_update["route"]

            messages = node_update.get("messages", [])

            if not isinstance(messages, list):
                messages = [messages]

            if messages:
                messages_count += len(messages)
                final_answer = str(messages[-1].content)

            steps.append(
                {
                    "node": node_name,
                    "messages": [serialize_message(message) for message in messages]
                }
            )

    if not final_answer:
        result = invoke_router_agent(
            message=message,
            thread_id=final_thread_id,
        )
        final_answer = result["final_answer"]
        messages_count = result["messages_count"]

    return {
        "thread_id": final_thread_id,
        "route": route,
        "steps": steps,
        "final_answer": final_answer,
        "messages_count": messages_count,
    }





































































































