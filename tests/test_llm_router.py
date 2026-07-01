def test_llm_router_mock_calculator_route(client, unique_thread):
    trace_id = "llm-router-mock-calc-001"
    thread_id = unique_thread("test-llm-router-mock-calc")

    response = client.post(
        "/agent/llm-router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
            "router_provider": "mock",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["answer"] == "工具 `add` 执行结果：8"
    assert data["route"] == "calculator"
    assert data["router_provider"] == "mock"
    assert data["router_model"] == "mock-router"
    assert "calculator" in data["route_reason"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_llm_router_mock_rag_route(client, unique_thread):
    trace_id = "llm-router-mock-rag-001"
    thread_id = unique_thread("test-llm-router-mock-rag")

    response = client.post(
        "/agent/llm-router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：RAG 是什么？",
            "thread_id": thread_id,
            "router_provider": "mock",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["route"] == "rag"
    assert data["router_provider"] == "mock"
    assert data["router_model"] == "mock-router"
    assert "rag" in data["route_reason"]
    assert "根据知识库检索结果" in data["answer"]
    assert "knowledge/agent_basics.md" in data["answer"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_llm_router_mock_chat_route(client, unique_thread):
    trace_id = "llm-router-mock-chat-001"
    thread_id = unique_thread("test-llm-router-mock-chat")

    response = client.post(
        "/agent/llm-router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "你好，介绍一下你自己",
            "thread_id": thread_id,
            "router_provider": "mock",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["answer"] == "Router chat response: 你好，介绍一下你自己"
    assert data["route"] == "chat"
    assert data["router_provider"] == "mock"
    assert data["router_model"] == "mock-router"
    assert "chat" in data["route_reason"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id