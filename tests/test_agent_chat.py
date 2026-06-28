def test_agent_chat_normal(client, unique_thread):
    thread_id = unique_thread("test-normal")

    response = client.post(
        "/agent/chat",
        json={
            "message": "你好，这是测试",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["thread_id"] == thread_id
    assert "你好，这是测试" in data["answer"]


def test_agent_chat_add_tool(client, unique_thread):
    thread_id = unique_thread("test-add")

    response = client.post(
        "/agent/chat",
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["thread_id"] == thread_id
    assert data["answer"] == "工具 `add` 执行结果：8"


def test_agent_chat_multiply_tool(client, unique_thread):
    thread_id = unique_thread("test-multiply")

    response = client.post(
        "/agent/chat",
        json={
            "message": "请计算 6 乘 7",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["thread_id"] == thread_id
    assert data["answer"] == "工具 `multiply` 执行结果：42"