def test_rag_search_endpoint(client):
    trace_id = "rag-test-trace-001"

    response = client.post(
        "/rag/search",
        headers={"x-trace-id": trace_id},
        json={
            "query": "RAG 是什么？",
            "k": 2,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["query"] == "RAG 是什么？"
    assert data["trace_id"] == trace_id
    assert len(data["results"]) >= 1
    assert "RAG" in data["results"][0]["content"]


def test_agent_chat_rag_tool(client, unique_thread):
    trace_id = "rag-agent-test-trace-001"
    thread_id = unique_thread("test-agent-rag")

    response = client.post(
        "/agent/chat",
        headers={"x-trace-id": trace_id},
        json={
            "message": "请搜索知识库：RAG 是什么？",
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id
    assert "根据知识库检索结果" in data["answer"]
    assert "RAG" in data["answer"]


def test_agent_debug_rag_tool_path(client, unique_thread):
    trace_id = "rag-debug-test-trace-001"
    thread_id = unique_thread("test-debug-rag")

    response = client.post(
        "/agent/debug",
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

    assert nodes == ["agent", "tools", "agent"]
    assert data["thread_id"] == thread_id
    assert data["trace_id"] == trace_id
    assert data["final_answer"].startswith("根据知识库检索结果")