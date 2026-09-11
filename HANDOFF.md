# Agent-API 项目交接文档

## 1. 最终定位

项目名称：

> **智能体编排与企业流程诊断平台（Agent-API）**

项目由两层组成：

```text
通用 Agent-API Platform
        ↓
ERP Permission / Workflow Diagnosis Reference Application
```

业务层来源于企业 ECP/ERP 权限与流程排障经验，但仓库只使用完全虚构的 Synthetic ERP 数据和接口，不包含任何前公司源码、生产接口、客户数据或生产配置。

## 2. ERP Reference Application

业务入口：

```text
POST /erp/diagnose
```

主图：

```text
analyze_request
→ collect_business_evidence
→ diagnose_root_cause
→ [optional] retrieve_policy
→ compose_diagnosis
→ verify_diagnosis
```

实时业务事实来自 5 个只读 MCP Tool：

```text
erp_get_user_access_profile
erp_get_document_context
erp_check_operation_permission
erp_get_approval_context
erp_get_transfer_context
```

静态规范来自：

```text
knowledge/erp/permission_rules.md
knowledge/erp/approval_rules.md
knowledge/erp/transfer_rules.md
```

Root Cause Taxonomy：

```text
ROLE_MISSING
ORG_SCOPE_DENIED
DATA_PERMISSION_DENIED
APPROVAL_FLOW_UNBOUND
APPROVER_UNRESOLVED
TRANSFER_RULE_MISSING
INVALID_DOCUMENT_STATE
DEPENDENCY_UNAVAILABLE
INSUFFICIENT_EVIDENCE
NO_ISSUE_DETECTED
```

## 3. ERP 数据与服务边界

### Default path

```text
SyntheticERPReadService
→ in-process fictional JSON dataset
```

用于 CI、Golden Case 和快速回归，默认不依赖网络。

### HTTP E2E path

```text
SyntheticERPHttpReadService
→ HTTP
→ examples.synthetic_erp_service FastAPI
```

用途：证明同一 `ERPReadService` Contract 可以跨微服务边界。

HTTP Adapter 仅允许：

```text
127.0.0.1
localhost
::1
```

不允许任意远程 URL。

## 4. ERP MCP Security

默认 Principal：

```text
erp-diagnosis-readonly-principal
allow_network = false
allow_write_tools = false
allow_live_neo4j = false
```

Synthetic HTTP E2E 使用：

```text
erp-diagnosis-loopback-http-principal
allow_network = true
allow_write_tools = false
allow_live_neo4j = false
```

网络能力还受到 HTTP Adapter loopback allowlist 二次限制。

ERP Registry 中不存在任何写 Tool。

## 5. Audit / Trace

业务 Tool Audit：

```text
event_type = erp_mcp_tool_audit
```

只记录：

- Tool Name
- Principal
- Authorization
- Parameter Names
- HMAC Parameter Fingerprint
- Outcome
- Minimal Result Summary

不记录原始业务参数。

Workflow Trace：

```text
event_type = erp_diagnosis_step
```

用于恢复节点级执行链和 Failure Attribution。

## 6. ERP Business Golden Acceptance

文件：

```text
eval_cases/erp_diagnosis_golden.jsonl
```

当前冻结集：

```text
20 / 20 passed
14 diagnostic cases
6 controlled-abstention cases
4 fault-injection cases
```

验收项包括：

- Root Cause Exact Match
- Required Tool Hit
- Forbidden Tool Absent
- Read-only Tool Set
- Policy Source Hit
- Controlled Abstention
- Verification Pass
- Trace Coverage
- Audit Privacy
- Failure Trace Coverage

运行：

```bash
python scripts/run_erp_diagnosis_eval.py
```

## 7. Synthetic HTTP E2E

运行：

```bash
python scripts/run_erp_http_e2e.py
```

该验证会启动临时 loopback Uvicorn Server，然后检查：

- HTTP Health
- MCP Tool over HTTP
- `requested_network=true`
- no-network Principal 被拒绝
- loopback HTTP Principal 可执行只读查询
- Root Cause Exact Match
- Policy Citations
- Verification Pass

## 8. 原平台能力

仍保留：

```text
FastAPI
LangGraph Agent
Tool Calling
SQLite Checkpointer
Router / Smart Chat
RAG / Vector / Hybrid / Chroma / Rerank
Agentic RAG
GraphRAG / Neo4j
Multi-Agent
MCP
SSE
Trace / Eval / Failure Injection
```

其中 GraphRAG 和 Multi-Agent 是平台能力，不强行进入 ERP 主链。

## 9. 原通用 Closure

历史通用闭环仍保留：

```text
Generic Agent Closure Golden Cases = 40 / 40
```

不要把通用 Closure 与 ERP 20 个业务 Golden Cases 合并成一个模糊数字；面试时应分别解释两套数据集验证的能力。

## 10. 关键边界

必须保留以下口径：

1. Synthetic ERP 数据全部虚构。
2. 没有对接前公司的生产代码和数据。
3. ERP Agent 是 Reference Application，不宣称生产上线。
4. 20/20 只说明冻结 Synthetic Contract 全部通过。
5. 实时业务依赖失败时不得用静态 RAG 猜实时权限。
6. Audit 不应完整留存敏感业务 Payload。
7. MCP Prompt 不是授权机制；真正授权由 Scope / Principal / Security Policy 控制。
8. Checkpoint 恢复不等于外部副作用 exactly-once。
9. GraphRAG 的 deterministic extraction / dry-run 不等于生产知识图谱质量。
10. Multi-Agent 当前是固定、可测试的角色编排，不是并发自治集群。

## 11. 回归命令

```bash
python -m pip check
python -W error -m compileall -q src examples scripts tests
python -m pytest -q

python scripts/run_erp_diagnosis_eval.py
python scripts/run_erp_http_e2e.py

git diff --check
```

## 12. CI

`.github/workflows/ci.yml` 必须继续保持：

- Python 3.10
- `pip check`
- warnings-as-errors compile
- full pytest
- ERP Business Golden Acceptance
- Synthetic ERP HTTP E2E
- `LLM_PROVIDER=mock`
- `NEO4J_ENABLED=false`
- main-agent MCP default disabled
