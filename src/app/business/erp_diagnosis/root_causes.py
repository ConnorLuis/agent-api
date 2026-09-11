from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RootCauseCode(str, Enum):
    """Controlled root-cause taxonomy for the ERP diagnosis reference app."""

    ROLE_MISSING = "ROLE_MISSING"
    ORG_SCOPE_DENIED = "ORG_SCOPE_DENIED"
    DATA_PERMISSION_DENIED = "DATA_PERMISSION_DENIED"
    APPROVAL_FLOW_UNBOUND = "APPROVAL_FLOW_UNBOUND"
    APPROVER_UNRESOLVED = "APPROVER_UNRESOLVED"
    TRANSFER_RULE_MISSING = "TRANSFER_RULE_MISSING"
    INVALID_DOCUMENT_STATE = "INVALID_DOCUMENT_STATE"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_ISSUE_DETECTED = "NO_ISSUE_DETECTED"


@dataclass(frozen=True)
class RootCauseDefinition:
    code: RootCauseCode
    title: str
    description: str
    default_recommendation: str
    requires_human: bool = False


ROOT_CAUSE_DEFINITIONS: dict[RootCauseCode, RootCauseDefinition] = {
    RootCauseCode.ROLE_MISSING: RootCauseDefinition(
        code=RootCauseCode.ROLE_MISSING,
        title="角色缺失",
        description="当前用户缺少执行目标业务操作所需的业务角色。",
        default_recommendation="核对岗位职责与角色授权，由有权限的管理员补充正确角色后重试。",
    ),
    RootCauseCode.ORG_SCOPE_DENIED: RootCauseDefinition(
        code=RootCauseCode.ORG_SCOPE_DENIED,
        title="组织范围不足",
        description="单据所属组织不在当前用户可访问的组织数据范围内。",
        default_recommendation="核对用户组织授权范围，确认是否应包含该单据所属组织。",
    ),
    RootCauseCode.DATA_PERMISSION_DENIED: RootCauseDefinition(
        code=RootCauseCode.DATA_PERMISSION_DENIED,
        title="数据权限不足",
        description="用户虽然可能具备相关角色和组织范围，但缺少该单据类型或操作的数据权限。",
        default_recommendation="核对该单据类型对应的数据权限与操作权限配置。",
    ),
    RootCauseCode.APPROVAL_FLOW_UNBOUND: RootCauseDefinition(
        code=RootCauseCode.APPROVAL_FLOW_UNBOUND,
        title="审批流未绑定",
        description="当前单据类型和组织未解析到可用的审批流。",
        default_recommendation="核对审批流启用状态、适用组织以及单据类型绑定关系。",
    ),
    RootCauseCode.APPROVER_UNRESOLVED: RootCauseDefinition(
        code=RootCauseCode.APPROVER_UNRESOLVED,
        title="审批人无法解析",
        description="审批流存在，但无法解析出有效审批人。",
        default_recommendation="核对审批节点人员、角色映射和用户有效状态。",
    ),
    RootCauseCode.TRANSFER_RULE_MISSING: RootCauseDefinition(
        code=RootCauseCode.TRANSFER_RULE_MISSING,
        title="传单规则缺失",
        description="源单据到目标单据类型之间不存在可用的传单规则。",
        default_recommendation="核对源单类型、目标单类型、组织范围和传单规则启用状态。",
    ),
    RootCauseCode.INVALID_DOCUMENT_STATE: RootCauseDefinition(
        code=RootCauseCode.INVALID_DOCUMENT_STATE,
        title="单据状态不允许当前操作",
        description="当前单据状态与目标操作不兼容。",
        default_recommendation="核对单据生命周期状态以及该状态下允许执行的操作。",
    ),
    RootCauseCode.DEPENDENCY_UNAVAILABLE: RootCauseDefinition(
        code=RootCauseCode.DEPENDENCY_UNAVAILABLE,
        title="实时业务依赖不可用",
        description="诊断所需的实时业务事实无法从依赖服务读取。",
        default_recommendation="不要使用静态文档替代实时业务事实；恢复依赖服务后重新诊断。",
        requires_human=True,
    ),
    RootCauseCode.INSUFFICIENT_EVIDENCE: RootCauseDefinition(
        code=RootCauseCode.INSUFFICIENT_EVIDENCE,
        title="证据不足",
        description="当前输入或工具证据不足以形成可靠诊断。",
        default_recommendation="补充用户、单据、目标操作或目标单据类型等必要信息后重新诊断。",
        requires_human=True,
    ),
    RootCauseCode.NO_ISSUE_DETECTED: RootCauseDefinition(
        code=RootCauseCode.NO_ISSUE_DETECTED,
        title="未发现已知配置异常",
        description="基于当前可用证据，未发现受控诊断规则覆盖的异常。",
        default_recommendation="若问题仍存在，转人工检查未纳入当前原型的业务规则或外部依赖。",
        requires_human=True,
    ),
}


def get_root_cause_definition(code: RootCauseCode | str) -> RootCauseDefinition:
    normalized = RootCauseCode(code)
    return ROOT_CAUSE_DEFINITIONS[normalized]
