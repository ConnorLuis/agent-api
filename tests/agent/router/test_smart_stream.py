def test_smart_stream_deterministic_calculator_route(client, unique_thread):
    trace_id = "smart-stream-deterministic-calc-001"
    thread_id = unique_thread("test-smart-stream-deterministic-calc")

    response = client.post(
        "/agent/smart-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
            "router_mode": "deterministic",
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
    assert '"router_mode": "deterministic"' in body
    assert '"router_provider": "deterministic"' in body
    assert '"router_model": "rule-based-router"' in body
    assert "Deterministic router selected calculator" in body
    assert "工具 `add` 执行结果：8" in body
    assert thread_id in body
    assert trace_id in body


def test_smart_stream_llm_mock_rag_route(client, unique_thread):
    trace_id = "smart-stream-llm-rag-001"
    thread_id = unique_thread("test-smart-stream-llm-rag")

    response = client.post(
        "/agent/smart-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：RAG 是什么？",
            "thread_id": thread_id,
            "router_mode": "llm",
            "router_provider": "mock",
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
    assert '"router_mode": "llm"' in body
    assert '"router_provider": "mock"' in body
    assert '"router_model": "mock-router"' in body
    assert "Mock LLM router selected rag" in body
    assert "根据知识库检索结果" in body
    assert "knowledge/agent_basics.md" in body
    assert thread_id in body
    assert trace_id in body


def test_smart_stream_llm_mock_chat_route(client, unique_thread):
    trace_id = "smart-stream-llm-chat-001"
    thread_id = unique_thread("test-smart-stream-llm-chat")

    response = client.post(
        "/agent/smart-stream",
        headers={"x-trace-id": trace_id},
        json={
            "message": "你好，介绍一下你自己",
            "thread_id": thread_id,
            "router_mode": "llm",
            "router_provider": "mock",
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
    assert '"router_mode": "llm"' in body
    assert '"router_provider": "mock"' in body
    assert '"router_model": "mock-router"' in body
    assert "Mock LLM router selected chat" in body
    assert "Router chat response: 你好，介绍一下你自己" in body
    assert thread_id in body
    assert trace_id in body