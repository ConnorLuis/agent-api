# ERP Approval Diagnosis Rules

This is synthetic reference documentation used only by the Agent-API ERP diagnosis prototype.

## APPROVAL_FLOW_UNBOUND — 审批流未绑定

`APPROVAL_FLOW_UNBOUND` means no enabled approval flow can be resolved for the current document type and organization. The diagnosis should verify the document context first and then use the read-only approval-context tool. A missing flow should result in a configuration recommendation, not an automatic flow binding.

## APPROVER_UNRESOLVED — 审批人无法解析

`APPROVER_UNRESOLVED` means an approval flow exists but no active approver can be resolved from the synthetic configuration. Typical checks include approver account status and the flow's personnel mapping. The Agent must not create users, modify personnel mappings, or rewrite the approval flow.

## Submission and approval evidence

For submit or approve scenarios, permission evidence and approval-flow evidence are independent. A user can have correct role/data permission while the approval flow is still missing or has no effective approver. The diagnosis should preserve both evidence sources when multiple failures coexist.
