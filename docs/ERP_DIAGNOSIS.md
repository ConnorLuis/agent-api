# ERP Diagnosis Reference Application

## 1. Positioning

This reference application turns a recurring enterprise ERP/ECP pain point into a concrete Agent-API business scenario:

> Users can report that document creation, submission, approval, or transfer failed, while the underlying cause may be role assignment, organization scope, data permission, approval-flow binding, approver resolution, transfer configuration, or document state.

The business prototype is inspired by prior ECP/ERP organization-permission work, but **does not use former-employer source code, production APIs, customer data, or production configuration**. The repository ships a fully fictional Synthetic ERP Service and synthetic dataset only.

The architecture goal is not to turn Agent-API into a vertical ERP-only repository. Agent-API remains the reusable orchestration platform; ERP diagnosis is a small reference application built on top of it.

## 2. Technology scope

The ERP reference app intentionally reuses only the Agent-API capabilities that fit this problem:

- LangGraph State and controlled workflow orchestration;
- Tool Calling for structured business facts;
- SQLite Checkpointer for short-term conversation state where needed;
- Agentic RAG for static ERP policy and operation documentation;
- MCP as the read-only business-tool boundary;
- MCP scopes and security policy for least privilege;
- Trace for execution evidence and audit-safe diagnostics;
- deterministic evaluation, failure injection, and business Golden Cases.

GraphRAG, Neo4j, and Multi-Agent remain platform capabilities, but they are **not required by the ERP diagnosis main path**.

## 3. Day-1 domain contract

### Root Cause Codes

The controlled taxonomy is defined in `src/app/business/erp_diagnosis/root_causes.py`:

- `ROLE_MISSING`
- `ORG_SCOPE_DENIED`
- `DATA_PERMISSION_DENIED`
- `APPROVAL_FLOW_UNBOUND`
- `APPROVER_UNRESOLVED`
- `TRANSFER_RULE_MISSING`
- `INVALID_DOCUMENT_STATE`
- `DEPENDENCY_UNAVAILABLE`
- `INSUFFICIENT_EVIDENCE`
- `NO_ISSUE_DETECTED`

The workflow may return more than one root-cause code when multiple independent checks fail. The final response must preserve evidence rather than forcing a single unsupported explanation.

### Diagnosis result shape

The controlled response contract includes:

- `status`
- `root_cause_codes`
- `root_cause_summary`
- `evidence`
- `policy_citations`
- `recommendations`
- `requires_human`
- `trace_id`

This keeps model-generated prose separate from machine-checkable diagnosis facts.

## 4. Synthetic ERP Service

The example service is located at:

```text
examples/synthetic_erp_service/
```

It contains more than 50 fully fictional records across users, documents, operation policies, approval flows, and transfer rules.

Run it independently:

```bash
python -m uvicorn examples.synthetic_erp_service.app:app --reload --port 8010
```

Read-only endpoints:

```text
GET /health
GET /users/{user_id}/access-profile
GET /documents/{document_id}/context?operation=SUBMIT
GET /permissions/check?user_id=...&document_id=...&operation=SUBMIT
GET /approval-flows/resolve?document_id=...
GET /transfer-rules/resolve?document_id=...&target_document_type=...
```

There are deliberately no role-update, permission-grant, approval-bind, or other write endpoints.

## 5. Frozen MCP tool design for Day 2

The ERP business boundary will expose exactly five read-only MCP tools in the first implementation:

```text
erp_get_user_access_profile(user_id)
erp_get_document_context(document_id, operation)
erp_check_operation_permission(user_id, document_id, operation)
erp_get_approval_context(document_id)
erp_get_transfer_context(document_id, target_document_type)
```

Why these five:

1. They map to stable business facts rather than UI actions.
2. They are composable but not excessively granular.
3. Permission diagnosis remains deterministic and returns evidence fields instead of forcing the LLM to infer RBAC rules from prose.
4. Static policy lookup remains an Agentic-RAG responsibility rather than being mixed into real-time ERP tools.
5. No write tool is registered, so least privilege is enforced structurally before runtime policy checks.

## 6. Security direction

Day 2 will add ERP-specific MCP scopes and authorization. The intended design is defense in depth:

```text
Tool exposure layer
  -> only read-only ERP tools exist
Scope layer
  -> principal must own explicit ERP read scopes
Runtime security policy
  -> write/network/destructive requests remain blocked
Audit layer
  -> store trace_id, tool name, decision, redacted argument summary/fingerprint, and result status
```

Raw business records and full user prompts should not be copied wholesale into security audit events.

## 7. Fallback boundary

A key business rule is:

> Fallback must not cross evidence types.

Static policy retrieval may have a safe degraded path. Real-time facts such as user roles, organization scope, document state, or approval binding must not be guessed from RAG when the business dependency is unavailable.

When a real-time ERP dependency cannot be read, the workflow should return `DEPENDENCY_UNAVAILABLE` rather than fabricating a diagnosis.
