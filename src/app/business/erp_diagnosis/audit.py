from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

from src.app.observability.trace_store import record_trace_event


ERP_AUDIT_EVENT_TYPE = "erp_mcp_tool_audit"
_DEMO_AUDIT_KEY = "synthetic-erp-demo-audit-key"


def _audit_key() -> bytes:
    """
    Return the HMAC key used only to pseudonymize audit parameters.

    The committed default is acceptable only because this reference application ships
    synthetic data. A real integration must inject ERP_AUDIT_HMAC_KEY from a secret store.
    """

    return os.getenv("ERP_AUDIT_HMAC_KEY", _DEMO_AUDIT_KEY).encode("utf-8")


def fingerprint_parameters(parameters: dict[str, Any]) -> str:
    canonical = json.dumps(
        parameters,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hmac.new(_audit_key(), canonical, hashlib.sha256).hexdigest()


def build_erp_tool_audit_payload(
    *,
    tool_name: str,
    principal_id: str,
    allowed: bool,
    authorization_reason: str,
    parameters: dict[str, Any],
    outcome: str,
    result_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a minimum-data audit payload without storing raw business arguments."""

    return {
        "tool_name": tool_name,
        "principal_id": principal_id,
        "allowed": allowed,
        "authorization_reason": authorization_reason,
        "parameter_names": sorted(parameters),
        "parameter_fingerprint": fingerprint_parameters(parameters),
        "raw_argument_values_recorded": False,
        "outcome": outcome,
        "result_summary": result_summary or {},
        "synthetic_reference_application": True,
    }


def record_erp_tool_audit(
    *,
    trace_id: str,
    tool_name: str,
    principal_id: str,
    allowed: bool,
    authorization_reason: str,
    parameters: dict[str, Any],
    outcome: str,
    result_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = build_erp_tool_audit_payload(
        tool_name=tool_name,
        principal_id=principal_id,
        allowed=allowed,
        authorization_reason=authorization_reason,
        parameters=parameters,
        outcome=outcome,
        result_summary=result_summary,
    )
    return record_trace_event(
        trace_id=trace_id,
        event_type=ERP_AUDIT_EVENT_TYPE,
        payload=payload,
    )
