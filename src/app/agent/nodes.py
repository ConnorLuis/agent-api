import re
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.app.agent.state import AgentState


def _extract_two_ints(text: str) -> tuple[int, int] | None:
    numbers = re.findall(r"-?\d+", text)

    if len(numbers) < 2:
        return None

    return int(numbers[0]), int(numbers[1])


def _build_tool_call(tool_name: str, args: dict) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": tool_name,
                "args": args,
                "id": f"call_{uuid4().hex[:8]}",
                "type": "tool_call",
            }
        ],
    )

def _is_memory_question(text: str) -> bool:
    lowered = text.lower()

    keywords = [
        "刚才",
        "上一轮",
        "上一次",
        "之前",
        "历史",
        "记得",
        "remember",
        "last time",
    ]

    return any(keyword in lowered for keyword in keywords)


def _should_search_knowledge(text: str) -> bool:
    keywords = [
        "rag",
        "RAG",
        "知识库",
        "检索",
        "搜索",
        "agent是什么",
        "Agent是什么",
        "langgraph",
        "LangGraph",
    ]
    return any(keyword in text for keyword in keywords)


def _answer_from_memory(messages: list) -> AIMessage:
    """
    Build a simple answer from previous messages.

    This is a deterministic mock memory reader for Day4.
    Later, a real LLM will read the same messages and answer naturally.
    """
    previous_tool_messages = [
        message for message in messages[:-1]
        if isinstance(message, ToolMessage)
    ]

    previous_human_messages = [
        message for message in messages[:-1]
        if isinstance(message, HumanMessage)
    ]

    if previous_tool_messages:
        last_tool_message = previous_tool_messages[-1]
        tool_name = getattr(last_tool_message, "name", "tool")

        return AIMessage(
            content=(
                f"我记得上一轮工具 `{tool_name}` 的执行结果是："
                f"{last_tool_message.content}"
            )
        )

    if previous_human_messages:
        last_human_message = previous_human_messages[-1]

        return AIMessage(
            content=f"我记得你之前说过：{last_human_message.content}"
        )

    return AIMessage(content="当前 thread 中还没有可用的历史记忆。")


def agent_node(state: AgentState) -> dict:
    """
    Day4 Tool Calling Agent node with short-term memory.

    It manually simulates:
    - tool call decision
    - tool result summarization
    - memory-aware response based on previous messages
    """
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, ToolMessage):
        tool_name = getattr(last_message, "name", "tool")

        if tool_name == "search_knowledge_base":
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "根据知识库检索结果：\n"
                            f"{last_message.content}"
                        )
                    )
                ]
            }

        return {
            "messages": [
                AIMessage(
                    content=f"工具 `{tool_name}` 执行结果：{last_message.content}"
                )
            ]
        }

    user_text = str(last_message.content)

    if _is_memory_question(user_text):
        return {
            "messages": [
                _answer_from_memory(messages)
            ]
        }

    # RAG 判断要放在数字计算判断之前或之外。
    # 否则“RAG 是什么？”这种没有数字的问题不会触发知识库工具。
    if _should_search_knowledge(user_text):
        return {
            "messages": [
                _build_tool_call(
                    tool_name="search_knowledge_base",
                    args={
                        "query": user_text,
                        "k": 3,
                    },
                )
            ]
        }

    pair = _extract_two_ints(user_text)

    if pair is not None:
        a, b = pair

        if any(keyword in user_text.lower() for keyword in ["乘", "*", "multiply"]):
            return {
                "messages": [
                    _build_tool_call(
                        tool_name="multiply",
                        args={"a": a, "b": b},
                    )
                ]
            }

        if any(keyword in user_text.lower() for keyword in ["加", "+", "add"]):
            return {
                "messages": [
                    _build_tool_call(
                        tool_name="add",
                        args={"a": a, "b": b},
                    )
                ]
            }



    return {
        "messages": [
            AIMessage(
                content=f"Day4 agent response: {user_text}"
            )
        ]
    }





