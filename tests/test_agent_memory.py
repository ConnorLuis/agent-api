def test_same_thread_has_memory(client, unique_thread):
    thread_id = unique_thread("test-memory-same")

    first = client.post(
        "/agent/chat",
        json={
            "message": "请计算 4 乘 9",
            "thread_id": thread_id,
        },
    )

    assert first.status_code == 200
    assert first.json()["answer"] == "工具 `multiply` 执行结果：36"

    second = client.post(
        "/agent/chat",
        json={
            "message": "我刚才计算了什么？",
            "thread_id": thread_id,
        },
    )

    assert second.status_code == 200
    assert second.json()["answer"] == "我记得上一轮工具 `multiply` 的执行结果是：36"


def test_different_thread_has_no_memory(client, unique_thread):
    thread_id = unique_thread("test-memory-different")

    response = client.post(
        "/agent/chat",
        json={
            "message": "我刚才计算了什么？",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "当前 thread 中还没有可用的历史记忆。"