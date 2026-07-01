def test_router_calculator_route_delegates_to_agent_memory(client, unique_thread):
    thread_id = unique_thread("test-router-delegation-calc")

    router_response = client.post(
        "/agent/router-chat",
        headers={"x-trace-id": "router-delegation-calc-001"},
        json={
            "message": "请计算 4 乘 9",
            "thread_id": thread_id,
        },
    )

    assert router_response.status_code == 200

    router_data = router_response.json()
    assert router_data["route"] == "calculator"
    assert router_data["answer"] == "工具 `multiply` 执行结果：36"

    memory_response = client.post(
        "/agent/chat",
        headers={"x-trace-id": "router-delegation-calc-002"},
        json={
            "message": "我刚才计算了什么？",
            "thread_id": thread_id,
        },
    )

    assert memory_response.status_code == 200

    memory_data = memory_response.json()
    assert memory_data["thread_id"] == thread_id
    assert memory_data["trace_id"] == "router-delegation-calc-002"
    assert memory_data["answer"] == "我记得上一轮工具 `multiply` 的执行结果是：36"


def test_router_rag_route_delegates_to_agent_memory(client, unique_thread):
    thread_id = unique_thread("test-router-delegation-rag")

    router_response = client.post(
        "/agent/router-chat",
        headers={"x-trace-id": "router-delegation-rag-001"},
        json={
            "message": "请搜索知识库：LangGraph 是什么？",
            "thread_id": thread_id,
        },
    )

    assert router_response.status_code == 200

    router_data = router_response.json()
    assert router_data["route"] == "rag"
    assert "根据知识库检索结果" in router_data["answer"]
    assert "LangGraph" in router_data["answer"]

    memory_response = client.post(
        "/agent/chat",
        headers={"x-trace-id": "router-delegation-rag-002"},
        json={
            "message": "我刚才检索了什么？",
            "thread_id": thread_id,
        },
    )

    assert memory_response.status_code == 200

    memory_data = memory_response.json()
    assert memory_data["thread_id"] == thread_id
    assert memory_data["trace_id"] == "router-delegation-rag-002"
    assert "search_knowledge_base" in memory_data["answer"]
    assert "LangGraph" in memory_data["answer"]