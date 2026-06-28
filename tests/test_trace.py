def test_health_returns_generated_trace_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-trace-id") is not None
    assert response.headers["x-trace-id"].startswith("trace-")


def test_health_reuses_request_trace_id(client):
    response = client.get(
        "/health",
        headers={"x-trace-id": "manual-test-trace-001"},
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == "manual-test-trace-001"


def test_agent_chat_returns_trace_id_in_header_and_body(client, unique_thread):
    trace_id = "chat-test-trace-001"
    thread_id = unique_thread("test-trace-chat")

    response = client.post(
        "/agent/chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 3 加 5",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["answer"] == "工具 `add` 执行结果：8"
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id


def test_agent_debug_returns_trace_id_in_header_and_body(client, unique_thread):
    trace_id = "debug-test-trace-001"
    thread_id = unique_thread("test-trace-debug")

    response = client.post(
        "/agent/debug",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请计算 8 乘 9",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["thread_id"] == thread_id
    assert data["final_answer"] == "工具 `multiply` 执行结果：72"
    assert data["trace_id"] == trace_id