from __future__ import annotations

import json
import socket
import sys
import threading
import time
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.synthetic_erp_service.app import app as synthetic_erp_app
from src.app.business.erp_diagnosis.mcp_tools import (
    run_erp_check_operation_permission_mcp_tool,
)
from src.app.business.erp_diagnosis.service import SyntheticERPHttpReadService
from src.app.business.erp_diagnosis.workflow import (
    build_erp_diagnosis_graph,
    invoke_erp_diagnosis,
)
from src.app.business.erp_diagnosis.root_causes import RootCauseCode


def _start_loopback_server() -> tuple[uvicorn.Server, threading.Thread, int]:
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
        name="synthetic-erp-http-e2e",
    )
    thread.start()
    return server, thread, port


def _wait_until_ready(
    service: SyntheticERPHttpReadService,
    *,
    timeout_seconds: float = 5.0,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            health = service.health()
            if health.get("status") == "ok":
                return
        except Exception as exc:  # pragma: no cover - diagnostic only
            last_error = exc
        time.sleep(0.05)
    raise RuntimeError(
        f"Synthetic ERP HTTP service did not become ready: {last_error}"
    )


def main() -> int:
    server, thread, port = _start_loopback_server()
    service = SyntheticERPHttpReadService(
        base_url=f"http://127.0.0.1:{port}",
        timeout_seconds=2.0,
    )

    try:
        _wait_until_ready(service)

        tool_payload = run_erp_check_operation_permission_mcp_tool(
            user_id="SYN-U001",
            document_id="SYN-PO-002",
            operation="SUBMIT",
            trace_id="erp-http-e2e-tool-001",
            service=service,
        )

        graph = build_erp_diagnosis_graph(
            service=service,
            with_checkpointer=False,
        )
        diagnosis = invoke_erp_diagnosis(
            query="为什么这张采购订单提交不了？",
            user_id="SYN-U001",
            document_id="SYN-PO-002",
            operation="SUBMIT",
            thread_id="erp-http-e2e-thread-001",
            trace_id="erp-http-e2e-diagnosis-001",
            graph=graph,
        )

        expected_codes = {
            RootCauseCode.ORG_SCOPE_DENIED.value,
            RootCauseCode.APPROVAL_FLOW_UNBOUND.value,
        }
        actual_codes = set(diagnosis["root_cause_codes"])

        checks = {
            "http_health": service.health().get("status") == "ok",
            "mcp_tool_allowed": tool_payload.get("allowed") is True,
            "network_requested": bool(
                (tool_payload.get("security_decision") or {})
                .get("requested_access", {})
                .get("requested_network")
            ),
            "network_boundary_marked": bool(
                (tool_payload.get("mcp_boundary") or {})
                .get("network_required")
            ),
            "loopback_boundary_marked": bool(
                (tool_payload.get("mcp_boundary") or {})
                .get("loopback_only")
            ),
            "no_write_capability": not bool(
                (tool_payload.get("mcp_boundary") or {})
                .get("write_capability_exposed", True)
            ),
            "root_cause_exact_match": actual_codes == expected_codes,
            "verification_pass": diagnosis.get("verification_pass") is True,
            "permission_policy_cited": any(
                "knowledge/erp/permission_rules.md" in citation
                for citation in diagnosis.get("policy_citations", [])
            ),
            "approval_policy_cited": any(
                "knowledge/erp/approval_rules.md" in citation
                for citation in diagnosis.get("policy_citations", [])
            ),
        }
        all_passed = all(checks.values())

        print(
            json.dumps(
                {
                    "all_passed": all_passed,
                    "base_url": service.base_url,
                    "checks": checks,
                    "tool_principal": (
                        tool_payload.get("authorization") or {}
                    ).get("principal_id"),
                    "root_cause_codes": diagnosis["root_cause_codes"],
                    "policy_citations": diagnosis["policy_citations"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if all_passed else 1
    finally:
        server.should_exit = True
        thread.join(timeout=5.0)


if __name__ == "__main__":
    raise SystemExit(main())
