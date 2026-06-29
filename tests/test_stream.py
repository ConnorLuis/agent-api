def test_agent_stream_add_tool(client, unique_thread):
    trace_id = "stream-test-trace-001"
    thread_id = unique_thread("test-stream-add")

    with client.stream(
        "POST",
        "/agent/stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id
    assert "event: metadata" in body
    assert "event: answer_chunk" in body
    assert "event: final" in body
    assert "event: done" in body
    assert "工具 `add` 执行结果：8" in body
    assert thread_id in body
    assert trace_id in body


def test_agent_stream_multiply_tool(client, unique_thread):
    trace_id = "stream-test-trace-002"
    thread_id = unique_thread("test-stream-mul")

    with client.stream(
        "POST",
        "/agent/stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 6 乘 7",
            "thread_id": thread_id,
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id
    assert "event: metadata" in body
    assert "event: answer_chunk" in body
    assert "event: final" in body
    assert "event: done" in body
    assert "工具 `multiply` 执行结果：42" in body
    assert thread_id in body
    assert trace_id in body