from src.app.observability.trace_store import get_trace_events


def test_erp_diagnose_endpoint_returns_business_diagnosis(client, unique_thread):
    trace_id = "test-erp-api-org-scope"
    response = client.post(
        "/erp/diagnose",
        headers={"x-trace-id": trace_id},
        json={
            "query": "为什么这张采购订单提交不了？",
            "user_id": "SYN-U001",
            "document_id": "SYN-PO-002",
            "operation": "SUBMIT",
            "thread_id": unique_thread("erp-api"),
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id
    data = response.json()
    assert data["trace_id"] == trace_id
    assert data["status"] == "diagnosed"
    assert "ORG_SCOPE_DENIED" in data["root_cause_codes"]
    assert data["verification_pass"] is True
    assert data["policy_citations"]


def test_erp_diagnose_endpoint_can_infer_operation_and_ids_from_query(client, unique_thread):
    response = client.post(
        "/erp/diagnose",
        json={
            "query": "SYN-U001 的 SYN-PO-002 为什么提交不了？",
            "thread_id": unique_thread("erp-api-infer"),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "SYN-U001"
    assert data["document_id"] == "SYN-PO-002"
    assert data["operation"] == "SUBMIT"
    assert "ORG_SCOPE_DENIED" in data["root_cause_codes"]


def test_erp_diagnosis_trace_avoids_raw_query_and_business_identifiers(client, unique_thread):
    trace_id = "test-erp-api-trace-minimal"
    response = client.post(
        "/erp/diagnose",
        headers={"x-trace-id": trace_id},
        json={
            "query": "SYN-U001 的 SYN-PO-002 为什么提交不了？",
            "thread_id": unique_thread("erp-trace"),
        },
    )
    assert response.status_code == 200

    events = get_trace_events(trace_id)
    diagnosis_events = [item for item in events if item["event_type"] == "erp_diagnosis_step"]
    assert diagnosis_events

    serialized = str([item["payload"] for item in diagnosis_events])
    assert "SYN-U001" not in serialized
    assert "SYN-PO-002" not in serialized
    assert "为什么提交不了" not in serialized
