def test_router_stream_calculator_route(client, unique_thread):
    trace_id = "router-stream-calc-001"
    thread_id = unique_thread("test-router-stream-calc")

    response = client.post(
        "/agent/router-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    body = response.text

    assert "event: metadata" in body
    assert "event: route" in body
    assert "event: answer_chunk" in body
    assert "event: final" in body
    assert "event: done" in body

    assert '"route": "calculator"' in body
    assert "工具 `add` 执行结果：8" in body
    assert thread_id in body
    assert trace_id in body


def test_router_stream_rag_route(client, unique_thread):
    trace_id = "router-stream-rag-001"
    thread_id = unique_thread("test-router-stream-rag")

    response = client.post(
        "/agent/router-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：RAG 是什么？",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    body = response.text

    assert "event: metadata" in body
    assert "event: route" in body
    assert "event: answer_chunk" in body
    assert "event: final" in body
    assert "event: done" in body

    assert '"route": "rag"' in body
    assert "根据知识库检索结果" in body
    assert "knowledge/agent_basics.md" in body
    assert thread_id in body
    assert trace_id in body


def test_router_stream_chat_route(client, unique_thread):
    trace_id = "router-stream-chat-001"
    thread_id = unique_thread("test-router-stream-chat")

    response = client.post(
        "/agent/router-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "你好，介绍一下你自己",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    body = response.text

    assert "event: metadata" in body
    assert "event: route" in body
    assert "event: answer_chunk" in body
    assert "event: final" in body
    assert "event: done" in body

    assert '"route": "chat"' in body
    assert "Router chat response: 你好，介绍一下你自己" in body
    assert thread_id in body
    assert trace_id in body