from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.service import (
    ERPReadService,
    get_default_erp_read_service,
)


ERPFaultPoint = Literal[
    "user_access",
    "document_context",
    "permission_check",
    "approval_context",
    "transfer_context",
]


class ERPInjectedDependencyError(RuntimeError):
    """Deterministic exception used only by the synthetic ERP failure harness."""


@dataclass
class FaultInjectingERPReadService:
    """
    Read-only ERP service decorator for deterministic failure injection.

    The decorator preserves the same ERPReadService contract and raises only at
    the selected read boundary. It never introduces write behavior.
    """

    fault_point: ERPFaultPoint
    base: ERPReadService | None = None

    def __post_init__(self) -> None:
        if self.base is None:
            self.base = get_default_erp_read_service()

    def _maybe_fail(self, point: ERPFaultPoint) -> None:
        if point == self.fault_point:
            raise ERPInjectedDependencyError(
                f"synthetic ERP dependency failure at {point}"
            )

    def get_user_access_profile(self, user_id: str):
        self._maybe_fail("user_access")
        return self.base.get_user_access_profile(user_id)

    def get_document_context(
        self,
        *,
        document_id: str,
        operation: ERPOperation,
    ):
        self._maybe_fail("document_context")
        return self.base.get_document_context(
            document_id=document_id,
            operation=operation,
        )

    def check_operation_permission(
        self,
        *,
        user_id: str,
        document_id: str,
        operation: ERPOperation,
    ):
        self._maybe_fail("permission_check")
        return self.base.check_operation_permission(
            user_id=user_id,
            document_id=document_id,
            operation=operation,
        )

    def resolve_approval_context(self, document_id: str):
        self._maybe_fail("approval_context")
        return self.base.resolve_approval_context(document_id)

    def resolve_transfer_context(
        self,
        *,
        document_id: str,
        target_document_type: str,
    ):
        self._maybe_fail("transfer_context")
        return self.base.resolve_transfer_context(
            document_id=document_id,
            target_document_type=target_document_type,
        )
