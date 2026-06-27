import re
from uuid import uuid4

from langchain_core.messages import AIMessage, ToolMessage

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
            }
        ],
    )


def agent_node(state: AgentState) -> dict:
    """
    Day3 minimal Tool Calling Agent node.

    This node manually simulates what an LLM with tool-calling ability would do:
    - read messages
    - decide whether a tool is needed
    - generate tool_calls if needed
    - summarize ToolMessage after tool execution
    """
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, ToolMessage):
        tool_name = getattr(last_message, "name", "tool")
        return {
            "messages": [
                AIMessage(
                    content=f"工具 `{tool_name}` 执行结果：{last_message.content}"
                )
            ]
        }

    user_text = str(last_message.content)
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
                content=f"Day3 agent response: {user_text}"
            )
        ]
    }