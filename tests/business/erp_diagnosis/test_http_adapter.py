from __future__ import annotations

import socket
import threading
import time

import pytest
import uvicorn

from examples.synthetic_erp_service.app import app as synthetic_erp_app
from src.app.business.erp_diagnosis.mcp_tools import (
    run_erp_check_operation_permission_mcp_tool,
)
from src.app.business.erp_diagnosis.root_causes import RootCauseCode
from src.app.business.erp_diagnosis.service import SyntheticERPHttpReadService
from src.app.business.erp_diagnosis.workflow import (
    build_erp_diagnosis_graph,
    invoke_erp_diagnosis,
)
from src.app.mcp_integration.permissions import get_erp_diagnosis_mcp_principal


@pytest.fixture(scope="module")
def synthetic_http_service():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    port = int(sock.getsockname()[1])

    config = uvicorn.Config(
        synthetic_erp_app,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(
        target=server.run,
        kwargs={"sockets": [sock]},
        daemon=True,
    )
    thread.start()

    service = SyntheticERPHttpReadService(
        base_url=f"http://127.0.0.1:{port}",
        timeout_seconds=2.0,
    )
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        try:
            if service.health()["status"] == "ok":
                break
        except Exception:
            time.sleep(0.05)
    else:
        server.should_exit = True
        thread.join(timeout=5.0)
        pytest.fail("synthetic ERP HTTP service did not become ready")

    try:
        yield service
    finally:
        server.should_exit = True
        thread.join(timeout=5.0)


def test_http_adapter_is_loopback_only():
    with pytest.raises(ValueError, match="loopback-only"):
        SyntheticERPHttpReadService(
            base_url="http://example.com:8010",
        )


def test_http_adapter_reads_same_structured_business_contract(synthetic_http_service):
    permission = synthetic_http_service.check_operation_permission(
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
    )

    assert permission is not None
    assert permission.allowed is False
    assert permission.org_scope_granted is False
    assert permission.reasons == [RootCauseCode.ORG_SCOPE_DENIED]


def test_mcp_http_adapter_marks_network_and_enforces_principal(synthetic_http_service):
    denied = run_erp_check_operation_permission_mcp_tool(
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        trace_id="test-erp-http-denied",
        service=synthetic_http_service,
        principal=get_erp_diagnosis_mcp_principal(),
    )
    assert denied["allowed"] is False
    assert denied["authorization"]["reason"] == "network_access_is_not_allowed"
    assert denied["mcp_boundary"]["network_required"] is True

    allowed = run_erp_check_operation_permission_mcp_tool(
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        trace_id="test-erp-http-allowed",
        service=synthetic_http_service,
    )
    assert allowed["allowed"] is True
    assert allowed["authorization"]["principal_id"] == (
        "erp-diagnosis-loopback-http-principal"
    )
    assert allowed["security_decision"]["requested_access"]["requested_network"] is True
    assert allowed["mcp_boundary"]["network_required"] is True
    assert allowed["mcp_boundary"]["loopback_only"] is True
    assert allowed["mcp_boundary"]["write_capability_exposed"] is False


def test_full_diagnosis_workflow_can_use_http_microservice_boundary(
    synthetic_http_service,
    unique_thread,
):
    graph = build_erp_diagnosis_graph(
        service=synthetic_http_service,
        with_checkpointer=False,
    )
    result = invoke_erp_diagnosis(
        query="为什么这张采购订单提交不了？",
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation="SUBMIT",
        thread_id=unique_thread("erp-http-e2e"),
        trace_id="test-erp-http-workflow",
        graph=graph,
    )

    assert result["status"] == "diagnosed"
    assert set(result["root_cause_codes"]) == {
        RootCauseCode.ORG_SCOPE_DENIED.value,
        RootCauseCode.APPROVAL_FLOW_UNBOUND.value,
    }
    assert result["verification_pass"] is True
    assert any(
        "knowledge/erp/permission_rules.md" in citation
        for citation in result["policy_citations"]
    )
    assert any(
        "knowledge/erp/approval_rules.md" in citation
        for citation in result["policy_citations"]
    )
