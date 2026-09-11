from src.app.business.erp_diagnosis.audit import (
    build_erp_tool_audit_payload,
    fingerprint_parameters,
)


def test_parameter_fingerprint_is_stable_but_does_not_expose_raw_values(monkeypatch):
    monkeypatch.setenv("ERP_AUDIT_HMAC_KEY", "unit-test-secret")
    parameters = {
        "user_id": "SYN-U001",
        "document_id": "SYN-PO-002",
        "operation": "SUBMIT",
    }

    first = fingerprint_parameters(parameters)
    second = fingerprint_parameters(dict(reversed(list(parameters.items()))))

    assert first == second
    assert len(first) == 64
    assert "SYN-U001" not in first
    assert "SYN-PO-002" not in first


def test_business_audit_payload_records_names_not_raw_values(monkeypatch):
    monkeypatch.setenv("ERP_AUDIT_HMAC_KEY", "unit-test-secret")
    payload = build_erp_tool_audit_payload(
        tool_name="erp_check_operation_permission",
        principal_id="erp-diagnosis-readonly-principal",
        allowed=True,
        authorization_reason="allowed",
        parameters={
            "user_id": "SYN-U001",
            "document_id": "SYN-PO-002",
            "operation": "SUBMIT",
        },
        outcome="completed",
        result_summary={
            "allowed": False,
            "reason_codes": ["ORG_SCOPE_DENIED"],
        },
    )

    serialized = str(payload)
    assert payload["parameter_names"] == ["document_id", "operation", "user_id"]
    assert payload["raw_argument_values_recorded"] is False
    assert payload["synthetic_reference_application"] is True
    assert "SYN-U001" not in serialized
    assert "SYN-PO-002" not in serialized
    assert "ORG_SCOPE_DENIED" in serialized
