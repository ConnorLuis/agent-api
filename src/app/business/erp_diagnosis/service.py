from __future__ import annotations

from typing import Protocol

from src.app.business.erp_diagnosis.models import (
    ApprovalContext,
    DocumentContext,
    ERPOperation,
    PermissionCheckResult,
    TransferContext,
    UserAccessProfile,
)
from src.app.business.erp_diagnosis.repository import (
    SyntheticERPRepository,
    get_default_synthetic_erp_repository,
)


class ERPReadService(Protocol):
    """Stable read-only port consumed by ERP MCP tools."""

    def get_user_access_profile(self, user_id: str) -> UserAccessProfile | None: ...

    def get_document_context(
        self,
        *,
        document_id: str,
        operation: ERPOperation,
    ) -> DocumentContext | None: ...

    def check_operation_permission(
        self,
        *,
        user_id: str,
        document_id: str,
        operation: ERPOperation,
    ) -> PermissionCheckResult | None: ...

    def resolve_approval_context(self, document_id: str) -> ApprovalContext | None: ...

    def resolve_transfer_context(
        self,
        *,
        document_id: str,
        target_document_type: str,
    ) -> TransferContext | None: ...


class SyntheticERPReadService:
    """
    CI-safe in-process adapter for the fully fictional dataset.

    The MCP layer depends on ERPReadService rather than this repository-backed
    implementation. A later HTTP/real-service adapter can therefore replace it
    without changing the MCP tool contracts or diagnosis workflow.
    """

    def __init__(self, repository: SyntheticERPRepository | None = None) -> None:
        self.repository = repository or get_default_synthetic_erp_repository()

    def get_user_access_profile(self, user_id: str) -> UserAccessProfile | None:
        return self.repository.get_user_access_profile(user_id)

    def get_document_context(
        self,
        *,
        document_id: str,
        operation: ERPOperation,
    ) -> DocumentContext | None:
        return self.repository.get_document_context(
            document_id=document_id,
            operation=operation,
        )

    def check_operation_permission(
        self,
        *,
        user_id: str,
        document_id: str,
        operation: ERPOperation,
    ) -> PermissionCheckResult | None:
        return self.repository.check_operation_permission(
            user_id=user_id,
            document_id=document_id,
            operation=operation,
        )

    def resolve_approval_context(self, document_id: str) -> ApprovalContext | None:
        return self.repository.resolve_approval_context(document_id)

    def resolve_transfer_context(
        self,
        *,
        document_id: str,
        target_document_type: str,
    ) -> TransferContext | None:
        return self.repository.resolve_transfer_context(
            document_id=document_id,
            target_document_type=target_document_type,
        )


def get_default_erp_read_service() -> ERPReadService:
    return SyntheticERPReadService()
