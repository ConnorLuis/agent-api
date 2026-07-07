def test_llm_chat_mock_provider(client):
    response = client.post(
        "/llm/chat",
        json={
            "message": "hello mock llm",
            "provider": "mock",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "Mock LLM response: hello mock llm"
    assert data["provider"] == "mock"
    assert data["model"] == "mock-echo"
    assert data["trace_id"] is not None


def test_llm_chat_ollama_provider_with_trace_id(client):
    trace_id = "llm-test-trace-001"

    response = client.post(
        "/llm/chat",
        headers={
            "x-trace-id": trace_id
        },
        json={
            "message": "hello trace llm",
            "provider": "mock",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()
    assert data["answer"] == "Mock LLM response: hello trace llm"
    assert data["provider"] == "mock"
    assert data["model"] == "mock-echo"
    assert data["trace_id"] == trace_id