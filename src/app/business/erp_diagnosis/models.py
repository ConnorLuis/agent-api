from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from src.app.business.erp_diagnosis.root_causes import RootCauseCode


class ERPOperation(str, Enum):
    CREATE = "CREATE"
    SUBMIT = "SUBMIT"
    APPROVE = "APPROVE"
    TRANSFER = "TRANSFER"
    VIEW = "VIEW"


class ERPDocumentState(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class DataPermissionRecord(BaseModel):
    document_type: str
    actions: list[ERPOperation]


class UserAccessRecord(BaseModel):
    user_id: str
    display_name: str
    active: bool = True
    roles: list[str] = Field(default_factory=list)
    org_scope: list[str] = Field(default_factory=list)
    data_permissions: list[DataPermissionRecord] = Field(default_factory=list)


class DocumentRecord(BaseModel):
    document_id: str
    document_type: str
    org_id: str
    state: ERPDocumentState
    creator_user_id: str
    amount: float | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class OperationPolicyRecord(BaseModel):
    document_type: str
    operation: ERPOperation
    required_roles: list[str] = Field(default_factory=list)
    allowed_states: list[ERPDocumentState] = Field(default_factory=list)


class ApprovalFlowRecord(BaseModel):
    flow_id: str
    document_type: str
    org_id: str
    enabled: bool = True
    approver_user_ids: list[str] = Field(default_factory=list)


class TransferRuleRecord(BaseModel):
    rule_id: str
    source_document_type: str
    target_document_type: str
    org_id: str
    enabled: bool = True


class SyntheticERPDataset(BaseModel):
    dataset_name: str
    disclaimer: str
    users: list[UserAccessRecord]
    documents: list[DocumentRecord]
    operation_policies: list[OperationPolicyRecord]
    approval_flows: list[ApprovalFlowRecord]
    transfer_rules: list[TransferRuleRecord]


class UserAccessProfile(BaseModel):
    user_id: str
    active: bool
    roles: list[str]
    org_scope: list[str]
    data_permissions: list[DataPermissionRecord]


class DocumentContext(BaseModel):
    document: DocumentRecord
    operation: ERPOperation
    required_roles: list[str]
    allowed_states: list[ERPDocumentState]


class PermissionCheckResult(BaseModel):
    user_id: str
    document_id: str
    operation: ERPOperation
    allowed: bool
    user_active: bool
    role_granted: bool
    org_scope_granted: bool
    data_permission_granted: bool
    state_allowed: bool
    required_roles: list[str]
    matched_roles: list[str]
    reasons: list[RootCauseCode] = Field(default_factory=list)


class ApprovalContext(BaseModel):
    document_id: str
    bound: bool
    flow_id: str | None = None
    approver_user_ids: list[str] = Field(default_factory=list)
    active_approver_user_ids: list[str] = Field(default_factory=list)
    approver_resolved: bool = False


class TransferContext(BaseModel):
    document_id: str
    source_document_type: str
    target_document_type: str
    org_id: str
    rule_found: bool
    rule_id: str | None = None


class EvidenceItem(BaseModel):
    source_type: Literal["tool", "policy", "system"]
    source_id: str
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class DiagnosisResult(BaseModel):
    status: Literal["diagnosed", "no_issue", "needs_input", "dependency_unavailable"]
    root_cause_codes: list[RootCauseCode] = Field(default_factory=list)
    root_cause_summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    policy_citations: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    requires_human: bool = False
    trace_id: str


class ERPDiagnosisRequest(BaseModel):
    query: str = Field(min_length=1)
    user_id: str | None = None
    document_id: str | None = None
    operation: ERPOperation | None = None
    target_document_type: str | None = None
    thread_id: str | None = None


class ERPDiagnosisResponse(DiagnosisResult):
    thread_id: str
    user_id: str | None = None
    document_id: str | None = None
    operation: ERPOperation | None = None
    target_document_type: str | None = None
    steps: list[str] = Field(default_factory=list)
    verification_pass: bool
    verification_flags: list[str] = Field(default_factory=list)
