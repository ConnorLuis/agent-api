from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def _new_thread_id(label: str) -> str:
    return f"test-{label}-{uuid4().hex}"


def _post_debug(message: str, *, thread_id: str | None = None) -> dict:
    final_thread_id = thread_id or _new_thread_id("arithmetic")
    response = client.post(
        "/agent/debug",
        json={
            "message": message,
            "thread_id": final_thread_id,
        },
        headers={"x-trace-id": f"trace-{uuid4().hex}"},
    )

    assert response.status_code == 200, response.text
    return response.json()


def _extract_tool_calls(payload: dict) -> list[dict]:
    tool_calls: list[dict] = []

    for step in payload["steps"]:
        if step["node"] != "agent":
            continue

        for message in step["messages"]:
            tool_calls.extend(message.get("tool_calls") or [])

    return tool_calls


def _extract_tool_messages(payload: dict) -> list[dict]:
    tool_messages: list[dict] = []

    for step in payload["steps"]:
        if step["node"] != "tools":
            continue

        for message in step["messages"]:
            if message.get("type") == "ToolMessage":
                tool_messages.append(message)

    return tool_messages


def test_agent_debug_multiplies_single_digit_chinese_numbers():
    payload = _post_debug("请计算六乘七")

    tool_calls = _extract_tool_calls(payload)
    tool_messages = _extract_tool_messages(payload)

    assert [call["name"] for call in tool_calls] == ["multiply"]
    assert tool_calls[0]["args"] == {"a": 6, "b": 7}
    assert [(message["name"], message["content"]) for message in tool_messages] == [
        ("multiply", "42")
    ]
    assert payload["final_answer"] == "工具 `multiply` 执行结果：42"


def test_agent_debug_multiplies_compound_chinese_number():
    payload = _post_debug("请计算十二乘三")

    tool_calls = _extract_tool_calls(payload)

    assert [call["name"] for call in tool_calls] == ["multiply"]
    assert tool_calls[0]["args"] == {"a": 12, "b": 3}
    assert payload["final_answer"] == "工具 `multiply` 执行结果：36"


def test_agent_debug_adds_then_multiplies_in_two_tool_calls():
    payload = _post_debug("请计算 2 加 3，再乘 4")

    tool_calls = _extract_tool_calls(payload)
    tool_messages = _extract_tool_messages(payload)

    assert [call["name"] for call in tool_calls] == ["add", "multiply"]
    assert tool_calls[0]["args"] == {"a": 2, "b": 3}
    assert tool_calls[1]["args"] == {"a": 5, "b": 4}
    assert [(message["name"], message["content"]) for message in tool_messages] == [
        ("add", "5"),
        ("multiply", "20"),
    ]
    assert payload["final_answer"] == "工具 `multiply` 执行结果：20"


def test_agent_debug_multiplies_then_adds_in_two_tool_calls():
    payload = _post_debug("请计算 2 乘 3，然后加 4")

    tool_calls = _extract_tool_calls(payload)
    tool_messages = _extract_tool_messages(payload)

    assert [call["name"] for call in tool_calls] == ["multiply", "add"]
    assert tool_calls[0]["args"] == {"a": 2, "b": 3}
    assert tool_calls[1]["args"] == {"a": 6, "b": 4}
    assert [(message["name"], message["content"]) for message in tool_messages] == [
        ("multiply", "6"),
        ("add", "10"),
    ]
    assert payload["final_answer"] == "工具 `add` 执行结果：10"


def test_agent_debug_uses_latest_human_message_in_same_thread():
    thread_id = _new_thread_id("same-thread")

    first_payload = _post_debug("请计算 1 加 1", thread_id=thread_id)
    second_payload = _post_debug(
        "请计算 2 加 3，之后乘 4",
        thread_id=thread_id,
    )

    assert first_payload["final_answer"] == "工具 `add` 执行结果：2"
    assert [
        call["name"] for call in _extract_tool_calls(second_payload)
    ] == ["add", "multiply"]
    assert second_payload["final_answer"] == "工具 `multiply` 执行结果：20"
