def test_debug_normal_steps(client, unique_thread):
    thread_id = unique_thread("test-debug-normal")

    response = client.post(
        "/agent/debug",
        json={
            "message": "你好，这是 debug 普通测试",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    nodes = [step["node"] for step in data["steps"]]

    assert data["thread_id"] == thread_id
    assert nodes == ["agent"]
    assert data["messages_count"] == 2
    assert "你好，这是 debug 普通测试" in data["final_answer"]


def test_debug_tool_call_steps(client, unique_thread):
    thread_id = unique_thread("test-debug-tool")

    response = client.post(
        "/agent/debug",
        json={
            "message": "请计算 8 乘 9",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    nodes = [step["node"] for step in data["steps"]]

    assert data["thread_id"] == thread_id
    assert nodes == ["agent", "tools", "agent"]
    assert data["final_answer"] == "工具 `multiply` 执行结果：72"
    assert data["messages_count"] == 4

    first_step_message = data["steps"][0]["messages"][0]
    assert first_step_message["type"] == "AIMessage"
    assert first_step_message["tool_calls"][0]["name"] == "multiply"

    tool_step_message = data["steps"][1]["messages"][0]
    assert tool_step_message["type"] == "ToolMessage"
    assert tool_step_message["content"] == "72"
    assert tool_step_message["name"] == "multiply"