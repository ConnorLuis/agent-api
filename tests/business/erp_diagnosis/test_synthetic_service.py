from fastapi.testclient import TestClient

from examples.synthetic_erp_service.app import app


client = TestClient(app)


def test_synthetic_service_is_explicitly_read_only_and_synthetic():
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert payload["synthetic"] is True


def test_synthetic_service_permission_endpoint_returns_structured_evidence():
    response = client.get(
        "/permissions/check",
        params={
            "user_id": "SYN-U001",
            "document_id": "SYN-PO-002",
            "operation": "SUBMIT",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["allowed"] is False
    assert "ORG_SCOPE_DENIED" in payload["reasons"]
    assert payload["role_granted"] is True


def test_synthetic_service_has_no_write_endpoint_for_role_changes():
    response = client.post(
        "/users/SYN-U001/roles",
        json={"role": "ERP_ADMIN"},
    )

    assert response.status_code == 404
