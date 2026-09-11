from __future__ import annotations

import json
from pathlib import Path

from src.app.business.erp_diagnosis.models import (
    ApprovalContext,
    ApprovalFlowRecord,
    DocumentContext,
    DocumentRecord,
    ERPOperation,
    OperationPolicyRecord,
    PermissionCheckResult,
    SyntheticERPDataset,
    TransferContext,
    TransferRuleRecord,
    UserAccessProfile,
    UserAccessRecord,
)
from src.app.business.erp_diagnosis.root_causes import RootCauseCode


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SYNTHETIC_ERP_DATA_PATH = (
    PROJECT_ROOT
    / "examples"
    / "synthetic_erp_service"
    / "data"
    / "synthetic_erp_data.json"
)


class SyntheticERPRepository:
    """Read-only repository backed by a fully fictional ERP dataset."""

    def __init__(self, data_path: Path | str = DEFAULT_SYNTHETIC_ERP_DATA_PATH) -> None:
        self.data_path = Path(data_path)
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.dataset = SyntheticERPDataset.model_validate(raw)

        self._users = {item.user_id: item for item in self.dataset.users}
        self._documents = {item.document_id: item for item in self.dataset.documents}

    def get_user(self, user_id: str) -> UserAccessRecord | None:
        return self._users.get(user_id)

    def get_document(self, document_id: str) -> DocumentRecord | None:
        return self._documents.get(document_id)

    def get_user_access_profile(self, user_id: str) -> UserAccessProfile | None:
        user = self.get_user(user_id)
        if user is None:
            return None
        return UserAccessProfile(
            user_id=user.user_id,
            active=user.active,
            roles=list(user.roles),
            org_scope=list(user.org_scope),
            data_permissions=list(user.data_permissions),
        )

    def _find_operation_policy(
        self,
        *,
        document_type: str,
        operation: ERPOperation,
    ) -> OperationPolicyRecord | None:
        for policy in self.dataset.operation_policies:
            if policy.document_type == document_type and policy.operation == operation:
                return policy
        return None

    def get_document_context(
        self,
        *,
        document_id: str,
        operation: ERPOperation,
    ) -> DocumentContext | None:
        document = self.get_document(document_id)
        if document is None:
            return None

        policy = self._find_operation_policy(
            document_type=document.document_type,
            operation=operation,
        )
        return DocumentContext(
            document=document,
            operation=operation,
            required_roles=list(policy.required_roles) if policy else [],
            allowed_states=list(policy.allowed_states) if policy else [],
        )

    def check_operation_permission(
        self,
        *,
        user_id: str,
        document_id: str,
        operation: ERPOperation,
    ) -> PermissionCheckResult | None:
        user = self.get_user(user_id)
        context = self.get_document_context(document_id=document_id, operation=operation)
        if user is None or context is None:
            return None

        required_roles = context.required_roles
        matched_roles = sorted(set(required_roles).intersection(user.roles))
        role_granted = not required_roles or bool(matched_roles)
        org_scope_granted = context.document.org_id in user.org_scope
        data_permission_granted = any(
            permission.document_type == context.document.document_type
            and operation in permission.actions
            for permission in user.data_permissions
        )
        state_allowed = (
            not context.allowed_states
            or context.document.state in context.allowed_states
        )

        reasons: list[RootCauseCode] = []
        if not user.active:
            reasons.append(RootCauseCode.DATA_PERMISSION_DENIED)
        if not role_granted:
            reasons.append(RootCauseCode.ROLE_MISSING)
        if not org_scope_granted:
            reasons.append(RootCauseCode.ORG_SCOPE_DENIED)
        if not data_permission_granted:
            reasons.append(RootCauseCode.DATA_PERMISSION_DENIED)
        if not state_allowed:
            reasons.append(RootCauseCode.INVALID_DOCUMENT_STATE)

        return PermissionCheckResult(
            user_id=user_id,
            document_id=document_id,
            operation=operation,
            allowed=len(reasons) == 0,
            user_active=user.active,
            role_granted=role_granted,
            org_scope_granted=org_scope_granted,
            data_permission_granted=data_permission_granted,
            state_allowed=state_allowed,
            required_roles=required_roles,
            matched_roles=matched_roles,
            reasons=reasons,
        )

    def resolve_approval_context(self, document_id: str) -> ApprovalContext | None:
        document = self.get_document(document_id)
        if document is None:
            return None

        flow: ApprovalFlowRecord | None = None
        for candidate in self.dataset.approval_flows:
            if (
                candidate.document_type == document.document_type
                and candidate.org_id == document.org_id
                and candidate.enabled
            ):
                flow = candidate
                break

        if flow is None:
            return ApprovalContext(document_id=document_id, bound=False)

        active_approvers = [
            user_id
            for user_id in flow.approver_user_ids
            if (self.get_user(user_id) is not None and self.get_user(user_id).active)
        ]
        return ApprovalContext(
            document_id=document_id,
            bound=True,
            flow_id=flow.flow_id,
            approver_user_ids=list(flow.approver_user_ids),
            active_approver_user_ids=active_approvers,
            approver_resolved=bool(active_approvers),
        )

    def resolve_transfer_context(
        self,
        *,
        document_id: str,
        target_document_type: str,
    ) -> TransferContext | None:
        document = self.get_document(document_id)
        if document is None:
            return None

        rule: TransferRuleRecord | None = None
        for candidate in self.dataset.transfer_rules:
            if (
                candidate.source_document_type == document.document_type
                and candidate.target_document_type == target_document_type
                and candidate.org_id in {document.org_id, "*"}
                and candidate.enabled
            ):
                rule = candidate
                break

        return TransferContext(
            document_id=document_id,
            source_document_type=document.document_type,
            target_document_type=target_document_type,
            org_id=document.org_id,
            rule_found=rule is not None,
            rule_id=rule.rule_id if rule else None,
        )


def get_default_synthetic_erp_repository() -> SyntheticERPRepository:
    return SyntheticERPRepository()
