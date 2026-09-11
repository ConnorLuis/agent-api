# ERP Permission Diagnosis Rules

This document is synthetic reference material for the Agent-API ERP diagnosis application. It does not describe a former employer's production configuration.

## ROLE_MISSING — 角色缺失

`ROLE_MISSING` means the user does not hold a business role required by the target document operation. Diagnosis should compare the operation policy's required roles with the user's effective roles. The Agent must not grant or modify a role; it may only recommend that an authorized administrator review the assignment.

## ORG_SCOPE_DENIED — 组织范围不足

`ORG_SCOPE_DENIED` means the document organization is outside the user's authorized organization scope. A role match alone is not enough: role authorization and organization data scope are separate checks. The diagnosis should cite the document organization and the organization-scope decision returned by the read-only business tool.

## DATA_PERMISSION_DENIED — 数据权限不足

`DATA_PERMISSION_DENIED` means the user does not have the document-type/action permission required for the operation, or the effective user status prevents the permission from being used. The diagnosis must rely on real-time permission facts rather than infer permission from static documentation.

## INVALID_DOCUMENT_STATE — 单据状态不允许当前操作

`INVALID_DOCUMENT_STATE` means the document lifecycle state is incompatible with the requested operation. For example, a submit operation may be valid only from DRAFT or REJECTED according to the synthetic policy. The Agent should recommend checking lifecycle state and allowed transitions rather than modifying the document state itself.

## Safety boundary

The ERP diagnosis Agent is read-only. Static policy text explains rules but must never replace real-time user, role, organization, permission, or document-state facts when those dependencies are unavailable.
