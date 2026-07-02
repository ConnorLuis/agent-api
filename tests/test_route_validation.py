from src.app.agent.route_validation import validate_route_decision


def test_validate_route_decision_valid_mock_route():
    result = validate_route_decision(
        route="calculator",
        router_provider="mock",
    )

    assert result.route == "calculator"
    assert result.route_valid is True
    assert result.fallback_used is False
    assert result.route_confidence == 1.0
    assert result.validation_reason == "Route is valid."


def test_validate_route_decision_invalid_route_fallback_to_chat():
    result = validate_route_decision(
        route="unknown_route",
        router_provider="ollama",
    )

    assert result.route == "chat"
    assert result.route_valid is False
    assert result.fallback_used is True
    assert result.route_confidence == 0.0
    assert "Invalid route `unknown_route`" in result.validation_reason
    assert "Fallback to `chat`" in result.validation_reason


def test_llm_router_chat_returns_route_validation_metadata(client, unique_thread):
    trace_id = "llm-router-validation-001"
    thread_id = unique_thread("test-llm-router-validation")

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

    assert data["route"] == "calculator"
    assert data["route_confidence"] == 1.0
    assert data["route_valid"] is True
    assert data["fallback_used"] is False
    assert data["validation_reason"] == "Route is valid."


def test_smart_chat_returns_route_validation_metadata(client, unique_thread):
    trace_id = "smart-chat-validation-001"
    thread_id = unique_thread("test-smart-chat-validation")

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

    assert data["route"] == "calculator"
    assert data["router_mode"] == "deterministic"
    assert data["route_confidence"] == 1.0
    assert data["route_valid"] is True
    assert data["fallback_used"] is False
    assert data["validation_reason"] == "Route is valid."


def test_smart_stream_returns_route_validation_metadata(client, unique_thread):
    trace_id = "smart-stream-validation-001"
    thread_id = unique_thread("test-smart-stream-validation")

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
    assert '"route_confidence": 1.0' in body
    assert '"route_valid": true' in body
    assert '"fallback_used": false' in body
    assert '"validation_reason": "Route is valid."' in body