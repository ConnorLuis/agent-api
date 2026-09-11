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

## 3. Controlled root-cause taxonomy

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

The FastAPI example service and the MCP tools share the same domain contract. MCP tools depend on the `ERPReadService` port rather than directly depending on the synthetic repository. The default `SyntheticERPReadService` is in-process and CI-safe, so CI does not require a network call to port 8010. A later HTTP or real-enterprise adapter can replace this implementation without changing MCP tool contracts or the diagnosis workflow.

## 5. MCP business-tool boundary

The first ERP reference implementation exposes exactly five read-only MCP tools:

```text
erp_get_user_access_profile(user_id)
erp_get_document_context(document_id, operation)
erp_check_operation_permission(user_id, document_id, operation)
erp_get_approval_context(document_id)
erp_get_transfer_context(document_id, target_document_type)
```

Why these five:

1. They map to stable business facts instead of UI actions.
2. They are composable but not excessively granular.
3. Permission diagnosis stays deterministic: role, organization scope, data permission, and document state are evaluated by business logic instead of being guessed by the LLM.
4. Static policy lookup remains an Agentic-RAG responsibility rather than being mixed into real-time ERP tools.
5. No write tool is registered, so least privilege is enforced structurally before runtime policy checks.

The MCP registry therefore grows from 10 platform tools to 15 total tools. The five ERP tools are category `erp`, read-only, CI-safe, do not require Neo4j, and do not require network access in the synthetic implementation.

## 6. ERP MCP scopes and least privilege

Each ERP tool owns one explicit scope:

```text
erp_get_user_access_profile      -> mcp:erp:user_access:read
erp_get_document_context         -> mcp:erp:document:read
erp_check_operation_permission   -> mcp:erp:permission:read
erp_get_approval_context         -> mcp:erp:approval:read
erp_get_transfer_context         -> mcp:erp:transfer:read
```

The ERP workflow uses a dedicated principal:

```text
erp-diagnosis-readonly-principal
```

It receives the two protocol-level discovery scopes (`mcp:tools:list`, `mcp:resources:read`) plus those five ERP read scopes. It does not receive RAG, GraphRAG, system-management, external-server, write, live-Neo4j, or network privileges.

The broader `ci-safe-principal` also contains the ERP read scopes only so the standard MCP registry/security-report regression path can validate all registered tools in CI.

Security remains defense in depth:

```text
Tool exposure layer
  -> only read-only ERP tools exist
Scope layer
  -> principal must own the exact ERP read scope
Runtime security policy
  -> write/network/destructive requests remain blocked
Audit layer
  -> record only minimum diagnostic metadata
```

Prompt instructions are not treated as authorization.

## 7. Audit design

ERP tool calls emit `erp_mcp_tool_audit` events into the existing trace store.

The audit event stores:

- `trace_id` through the trace-store envelope;
- MCP tool name;
- principal id;
- allow/deny decision and authorization reason;
- argument **names**, not argument values;
- HMAC-SHA256 parameter fingerprint;
- outcome (`completed`, `not_found`, `denied`, `dependency_error`, or `invalid_request`);
- minimal result summary such as permission reason codes.

The audit event does **not** copy raw user ids, document ids, prompts, role lists, organization lists, or full business payloads.

`ERP_AUDIT_HMAC_KEY` may be supplied by the environment. The committed fallback key exists only because this repository contains synthetic data; a real integration must load the HMAC key from a secret store.

## 8. Tool result and audit data are intentionally different

The Agent still needs structured ERP facts in the MCP tool result so it can diagnose the request. For example, the permission tool can return role, organization-scope, data-permission, and state-check results.

The **audit log** is deliberately smaller. This distinction prevents observability from becoming an accidental copy of sensitive business records.

## 9. Fallback boundary

A key business rule is:

> Fallback must not cross evidence types.

Static policy retrieval may have a safe degraded path. Real-time facts such as user roles, organization scope, document state, or approval binding must not be guessed from RAG when the business dependency is unavailable.

When a real-time ERP dependency cannot be read, the MCP wrapper returns `dependency_unavailable`; the later diagnosis workflow will map that to `DEPENDENCY_UNAVAILABLE` rather than fabricating a diagnosis.

## 10. Next step

The next implementation stage builds the LangGraph diagnosis workflow and ERP policy knowledge base on top of this MCP boundary. The workflow will combine:

```text
real-time ERP facts from MCP
+
static ERP policy evidence from Agentic RAG
+
controlled Root Cause Codes
```

GraphRAG, Neo4j, and Multi-Agent will remain outside the ERP main path unless a future business requirement actually needs them.
