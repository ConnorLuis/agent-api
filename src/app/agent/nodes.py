import re
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.app.agent.state import AgentState


CHINESE_DIGITS = {
    "零": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

CHINESE_SMALL_UNITS = {
    "十": 10,
    "百": 100,
    "千": 1000,
}

CHINESE_LARGE_UNITS = {
    "万": 10_000,
    "亿": 100_000_000,
}

CHINESE_NUMBER_PATTERN = re.compile(r"负?[零一二两三四五六七八九十百千万亿]+")
OPERATOR_PATTERN = r"(?:加上?|\+|add|乘以?|\*|×|multiply)"
MULTI_STEP_CONNECTOR_PATTERN = r"(?:再|然后|之后|接着)"


def _chinese_number_to_int(text: str) -> int:
    """Convert a Chinese integer string to an int.

    Supported examples include 六、十二、二十三、一百零二、二零二六、负七。
    """
    if not text:
        raise ValueError("Chinese number cannot be empty")

    negative = text.startswith("负")
    if negative:
        text = text[1:]

    if not text:
        raise ValueError("Chinese number cannot contain only a sign")

    # Strings without units are interpreted digit by digit, for example 二零二六.
    has_unit = any(
        char in CHINESE_SMALL_UNITS or char in CHINESE_LARGE_UNITS
        for char in text
    )
    if not has_unit:
        value = int("".join(str(CHINESE_DIGITS[char]) for char in text))
        return -value if negative else value

    total = 0
    section = 0
    current_digit = 0

    for char in text:
        if char in CHINESE_DIGITS:
            current_digit = CHINESE_DIGITS[char]
            continue

        if char in CHINESE_SMALL_UNITS:
            unit = CHINESE_SMALL_UNITS[char]
            if current_digit == 0:
                current_digit = 1
            section += current_digit * unit
            current_digit = 0
            continue

        if char in CHINESE_LARGE_UNITS:
            large_unit = CHINESE_LARGE_UNITS[char]
            section += current_digit
            total += section * large_unit
            section = 0
            current_digit = 0
            continue

        raise ValueError(f"Unsupported Chinese number character: {char}")

    value = total + section + current_digit
    return -value if negative else value


def _normalize_chinese_numbers(text: str) -> str:
    """Replace Chinese integer expressions in text with Arabic integers."""

    def replace(match: re.Match[str]) -> str:
        return str(_chinese_number_to_int(match.group(0)))

    return CHINESE_NUMBER_PATTERN.sub(replace, text)


def _normalize_operator(operator: str) -> str:
    lowered = operator.lower()

    if lowered in {"加", "加上", "+", "add"}:
        return "add"

    if lowered in {"乘", "乘以", "*", "×", "multiply"}:
        return "multiply"

    raise ValueError(f"Unsupported operator: {operator}")


def _parse_multi_step_calculation(
    text: str,
) -> tuple[str, int, int, str, int] | None:
    """Parse two sequential arithmetic operations.

    Example: ``2 加 3，再乘 4`` becomes
    ``("add", 2, 3, "multiply", 4)``.
    """
    normalized = _normalize_chinese_numbers(text)
    pattern = re.compile(
        rf"(-?\d+)\s*({OPERATOR_PATTERN})\s*(-?\d+)"
        rf"\s*[,，;；]?\s*{MULTI_STEP_CONNECTOR_PATTERN}\s*"
        rf"({OPERATOR_PATTERN})\s*(-?\d+)",
        re.IGNORECASE,
    )
    match = pattern.search(normalized)
    if match is None:
        return None

    return (
        _normalize_operator(match.group(2)),
        int(match.group(1)),
        int(match.group(3)),
        _normalize_operator(match.group(4)),
        int(match.group(5)),
    )


def _parse_single_calculation(text: str) -> tuple[str, int, int] | None:
    """Parse one supported arithmetic operation from text."""
    normalized = _normalize_chinese_numbers(text)
    pattern = re.compile(
        rf"(-?\d+)\s*({OPERATOR_PATTERN})\s*(-?\d+)",
        re.IGNORECASE,
    )
    match = pattern.search(normalized)
    if match is None:
        return None

    return (
        _normalize_operator(match.group(2)),
        int(match.group(1)),
        int(match.group(3)),
    )


def _get_current_turn_messages(messages: list) -> list:
    """Return messages belonging to the latest user turn."""
    for index in range(len(messages) - 1, -1, -1):
        if isinstance(messages[index], HumanMessage):
            return messages[index:]

    return messages


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
    """Build a deterministic answer from previous messages."""
    previous_tool_messages = [
        message
        for message in messages[:-1]
        if isinstance(message, ToolMessage)
    ]

    previous_human_messages = [
        message
        for message in messages[:-1]
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
        return AIMessage(content=f"我记得你之前说过：{last_human_message.content}")

    return AIMessage(content="当前 thread 中还没有可用的历史记忆。")


def agent_node(state: AgentState) -> dict:
    """Deterministic Tool Calling Agent node with short-term memory."""
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

        current_turn_messages = _get_current_turn_messages(messages)
        current_user_text = str(current_turn_messages[0].content)
        multi_step = _parse_multi_step_calculation(current_user_text)
        current_tool_messages = [
            message
            for message in current_turn_messages
            if isinstance(message, ToolMessage)
        ]

        # The first tool in a two-step expression has completed. Use its
        # numeric result as the first argument of the second operation.
        if multi_step is not None and len(current_tool_messages) == 1:
            first_tool, _, _, second_tool, final_operand = multi_step

            if tool_name == first_tool:
                return {
                    "messages": [
                        _build_tool_call(
                            tool_name=second_tool,
                            args={
                                "a": int(last_message.content),
                                "b": final_operand,
                            },
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
        return {"messages": [_answer_from_memory(messages)]}

    # RAG routing must run independently from arithmetic parsing.
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

    multi_step = _parse_multi_step_calculation(user_text)
    if multi_step is not None:
        first_tool, first_operand, second_operand, _, _ = multi_step
        return {
            "messages": [
                _build_tool_call(
                    tool_name=first_tool,
                    args={
                        "a": first_operand,
                        "b": second_operand,
                    },
                )
            ]
        }

    single_step = _parse_single_calculation(user_text)
    if single_step is not None:
        tool_name, first_operand, second_operand = single_step
        return {
            "messages": [
                _build_tool_call(
                    tool_name=tool_name,
                    args={
                        "a": first_operand,
                        "b": second_operand,
                    },
                )
            ]
        }

    return {
        "messages": [
            AIMessage(content=f"Day4 agent response: {user_text}")
        ]
    }
