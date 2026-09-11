from __future__ import annotations

import json
import os
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

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
    implementation. The HTTP adapter below proves the same port can cross a
    service boundary without changing the business tool contracts.
    """

    network_required = False
    adapter_kind = "synthetic_in_process"
    loopback_only = True

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


class SyntheticERPHttpReadService:
    """
    Read-only HTTP adapter for the local Synthetic ERP Service.

    This adapter is intentionally loopback-only. It exists to prove that the
    MCP business contract can cross a microservice boundary without using any
    former-employer API, code, data, or configuration.

    A real enterprise integration should provide a separate ERPReadService
    implementation with explicit authentication, TLS, service discovery, and
    organization-specific network policy.
    """

    network_required = True
    adapter_kind = "synthetic_http"
    loopback_only = True

    _LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout_seconds: float = 2.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv(
                "ERP_SYNTHETIC_HTTP_BASE_URL",
                "http://127.0.0.1:8010",
            )
        ).rstrip("/")
        self.timeout_seconds = float(timeout_seconds)
        self._validate_loopback_base_url()

    def _validate_loopback_base_url(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "http":
            raise ValueError(
                "Synthetic ERP HTTP adapter only accepts http:// loopback URLs"
            )
        hostname = (parsed.hostname or "").lower()
        if hostname not in self._LOOPBACK_HOSTS:
            raise ValueError(
                "Synthetic ERP HTTP adapter is loopback-only; "
                f"unsupported host: {hostname or '<missing>'}"
            )

    def _get_json(
        self,
        path: str,
        *,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        suffix = ""
        if query:
            suffix = "?" + urlencode(
                {
                    key: (
                        value.value
                        if isinstance(value, ERPOperation)
                        else value
                    )
                    for key, value in query.items()
                    if value is not None
                }
            )
        request = Request(
            f"{self.base_url}{path}{suffix}",
            method="GET",
            headers={"Accept": "application/json"},
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 404:
                return None
            raise RuntimeError(
                f"Synthetic ERP HTTP dependency returned HTTP {exc.code}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                "Synthetic ERP HTTP dependency is unavailable"
            ) from exc

        try:
            value = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Synthetic ERP HTTP dependency returned invalid JSON"
            ) from exc

        if not isinstance(value, dict):
            raise RuntimeError(
                "Synthetic ERP HTTP dependency returned a non-object payload"
            )
        return value

    def health(self) -> dict[str, Any]:
        payload = self._get_json("/health")
        if payload is None:
            raise RuntimeError("Synthetic ERP HTTP health endpoint not found")
        return payload

    def get_user_access_profile(self, user_id: str) -> UserAccessProfile | None:
        payload = self._get_json(f"/users/{user_id}/access-profile")
        return UserAccessProfile.model_validate(payload) if payload else None

    def get_document_context(
        self,
        *,
        document_id: str,
        operation: ERPOperation,
    ) -> DocumentContext | None:
        payload = self._get_json(
            f"/documents/{document_id}/context",
            query={"operation": operation},
        )
        return DocumentContext.model_validate(payload) if payload else None

    def check_operation_permission(
        self,
        *,
        user_id: str,
        document_id: str,
        operation: ERPOperation,
    ) -> PermissionCheckResult | None:
        payload = self._get_json(
            "/permissions/check",
            query={
                "user_id": user_id,
                "document_id": document_id,
                "operation": operation,
            },
        )
        return PermissionCheckResult.model_validate(payload) if payload else None

    def resolve_approval_context(self, document_id: str) -> ApprovalContext | None:
        payload = self._get_json(
            "/approval-flows/resolve",
            query={"document_id": document_id},
        )
        return ApprovalContext.model_validate(payload) if payload else None

    def resolve_transfer_context(
        self,
        *,
        document_id: str,
        target_document_type: str,
    ) -> TransferContext | None:
        payload = self._get_json(
            "/transfer-rules/resolve",
            query={
                "document_id": document_id,
                "target_document_type": target_document_type,
            },
        )
        return TransferContext.model_validate(payload) if payload else None


def get_default_erp_read_service() -> ERPReadService:
    """
    Return the deterministic in-process adapter used by normal tests and CI.

    The HTTP adapter is selected explicitly for end-to-end validation so the
    default workflow never acquires an implicit network dependency.
    """

    return SyntheticERPReadService()
