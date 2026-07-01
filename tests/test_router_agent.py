def test_router_agent_calculator_route(client, unique_thread):
    trace_id = "router-test-trace-calc-001"
    thread_id = unique_thread("test-router-calc")

    response = client.post(
        "/agent/router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["route"] == "calculator"
    assert data["answer"] == "工具 `add` 执行结果：8"
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_router_agent_rag_route(client, unique_thread):
    trace_id = "router-test-trace-rag-001"
    thread_id = unique_thread("test-router-rag")

    response = client.post(
        "/agent/router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：RAG 是什么？",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["route"] == "rag"
    assert "根据知识库检索结果" in data["answer"]
    assert "RAG" in data["answer"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_router_agent_chat_route(client, unique_thread):
    trace_id = "router-test-trace-chat-001"
    thread_id = unique_thread("test-router-chat")

    response = client.post(
        "/agent/router-chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "你好，介绍一下你自己",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["route"] == "chat"
    assert data["answer"] == "Router chat response: 你好，介绍一下你自己"
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_router_agent_debug_rag_route(client, unique_thread):
    trace_id = "router-test-trace-debug-001"
    thread_id = unique_thread("test-router-debug-rag")

    response = client.post(
        "/agent/router-debug",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：LangGraph 是什么？",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    nodes = [step["node"] for step in data["steps"]]

    assert data["route"] == "rag"
    assert nodes == ["router", "rag"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id
    assert data["final_answer"].startswith("根据知识库检索结果")