from __future__ import annotations

from fastapi import APIRouter, Request

from src.app.business.erp_diagnosis.models import (
    ERPDiagnosisRequest,
    ERPDiagnosisResponse,
)
from src.app.business.erp_diagnosis.workflow import invoke_erp_diagnosis


router = APIRouter(prefix="/erp", tags=["erp"])


def _resolve_trace_id(request: Request) -> str | None:
    header_trace_id = request.headers.get("x-trace-id")
    if header_trace_id:
        return header_trace_id

    try:
        from src.app.core.request_context import get_trace_id

        return get_trace_id()
    except Exception:
        return None


@router.post("/diagnose", response_model=ERPDiagnosisResponse)
def diagnose_erp_issue(
    payload: ERPDiagnosisRequest,
    request: Request,
) -> dict:
    return invoke_erp_diagnosis(
        query=payload.query,
        user_id=payload.user_id,
        document_id=payload.document_id,
        operation=payload.operation,
        target_document_type=payload.target_document_type,
        thread_id=payload.thread_id,
        trace_id=_resolve_trace_id(request),
    )
