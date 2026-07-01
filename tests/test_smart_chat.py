def test_smart_chat_deterministic_calculator_route(client, unique_thread):
    trace_id = "smart-chat-deterministic-calc-001"
    thread_id = unique_thread("test-smart-chat-deterministic-calc")

    response = client.post(
        "/agent/smart-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
            "router_mode": "deterministic",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["answer"] == "工具 `add` 执行结果：8"
    assert data["route"] == "calculator"
    assert data["route_reason"] == (
        "Deterministic router selected calculator by rule-based classification."
    )
    assert data["router_mode"] == "deterministic"
    assert data["router_provider"] == "deterministic"
    assert data["router_model"] == "rule-based-router"
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_smart_chat_llm_mock_rag_route(client, unique_thread):
    trace_id = "smart-chat-llm-rag-001"
    thread_id = unique_thread("test-smart-chat-llm-rag")

    response = client.post(
        "/agent/smart-chat",
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

    data = response.json()
    assert data["route"] == "rag"
    assert data["router_mode"] == "llm"
    assert data["router_provider"] == "mock"
    assert data["router_model"] == "mock-router"
    assert "rag" in data["route_reason"]
    assert "根据知识库检索结果" in data["answer"]
    assert "knowledge/agent_basics.md" in data["answer"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_smart_chat_llm_mock_chat_route(client, unique_thread):
    trace_id = "smart-chat-llm-chat-001"
    thread_id = unique_thread("test-smart-chat-llm-chat")

    response = client.post(
        "/agent/smart-chat",
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

    data = response.json()
    assert data["answer"] == "Router chat response: 你好，介绍一下你自己"
    assert data["route"] == "chat"
    assert data["router_mode"] == "llm"
    assert data["router_provider"] == "mock"
    assert data["router_model"] == "mock-router"
    assert "chat" in data["route_reason"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id