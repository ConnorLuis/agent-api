from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.repository import get_default_synthetic_erp_repository


app = FastAPI(
    title="Synthetic ERP Service",
    description=(
        "Fully fictional, read-only ERP service for validating Agent-API tool orchestration. "
        "It contains no former-employer code or production data."
    ),
    version="0.1.0",
)

repository = get_default_synthetic_erp_repository()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "dataset": repository.dataset.dataset_name,
        "read_only": True,
        "synthetic": True,
    }


@app.get("/users/{user_id}/access-profile")
def get_user_access_profile(user_id: str) -> dict:
    result = repository.get_user_access_profile(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="synthetic user not found")
    return result.model_dump(mode="json")


@app.get("/documents/{document_id}/context")
def get_document_context(
    document_id: str,
    operation: ERPOperation = Query(...),
) -> dict:
    result = repository.get_document_context(
        document_id=document_id,
        operation=operation,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="synthetic document not found")
    return result.model_dump(mode="json")


@app.get("/permissions/check")
def check_permission(
    user_id: str,
    document_id: str,
    operation: ERPOperation,
) -> dict:
    result = repository.check_operation_permission(
        user_id=user_id,
        document_id=document_id,
        operation=operation,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="synthetic user or document not found")
    return result.model_dump(mode="json")


@app.get("/approval-flows/resolve")
def resolve_approval_flow(document_id: str) -> dict:
    result = repository.resolve_approval_context(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="synthetic document not found")
    return result.model_dump(mode="json")


@app.get("/transfer-rules/resolve")
def resolve_transfer_rule(document_id: str, target_document_type: str) -> dict:
    result = repository.resolve_transfer_context(
        document_id=document_id,
        target_document_type=target_document_type,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="synthetic document not found")
    return result.model_dump(mode="json")
