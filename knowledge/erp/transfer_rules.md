# ERP Document Transfer Diagnosis Rules

This document contains fictional transfer-policy guidance for the Agent-API reference application.

## TRANSFER_RULE_MISSING — 传单规则缺失

`TRANSFER_RULE_MISSING` means no enabled source-document to target-document rule can be resolved for the document's organization. The diagnosis requires the source document context, target document type, operation permission, and read-only transfer-rule result.

A transfer failure must not be repaired automatically. The Agent can recommend that an authorized administrator review source type, target type, organization applicability, and rule enablement.

## Evidence boundary

Static transfer documentation can explain how transfer rules are interpreted, but it cannot prove that a particular live rule exists. If the real-time ERP dependency is unavailable, the workflow must return `DEPENDENCY_UNAVAILABLE` rather than infer a transfer configuration from this document.
