# 智能体编排与企业流程诊断平台（Agent-API）

结合企业 ECP/ERP 组织权限开发经历，将单据创建、审批流转等场景中依赖人工排查角色、组织范围和业务配置的问题抽象为企业流程诊断任务；基于 Agent-API 通用底座实现 **ERP 单据权限与流程诊断 Agent Reference Application**。

业务原型来源于过去参与企业 ECP/ERP 权限模块时观察到的真实问题，但仓库**没有使用前公司的源码、生产接口、客户数据或生产配置**。项目根据相同类型的业务合同构造完全虚构的 Synthetic ERP Service，用于验证 Agent 的工具编排、知识增强、故障诊断、安全边界和工程验收。

Agent-API 底座保留并复用：

- LangGraph State / Conditional Routing
- Tool Calling
- SQLite Checkpointer
- Agentic RAG
- MCP Server / Client / Registry / Security
- Trace / Audit
- Evaluation / Failure Injection
- GraphRAG / Neo4j（平台扩展能力，不强行进入 ERP 主链）
- Multi-Agent（平台扩展能力，不强行进入 ERP 主链）

---

## 1. 为什么需要这个业务 Agent

典型企业 ERP 故障：

- 用户创建或提交单据失败；
- 审批流转不下去；
- 单据传单 / 下推失败；
- 用户能看到角色，却仍没有目标组织的数据权限；
- 审批流存在，但无法解析出有效审批人。

传统排查通常需要实施或运维人员人工查看角色、组织范围、数据权限、单据状态、审批流和传单规则。

本项目把这类问题拆成两类证据：

```text
实时业务事实
→ MCP Read-only Tools
→ 用户 / 单据 / 权限 / 审批 / 传单上下文

静态业务规范
→ Agentic RAG
→ ERP 权限 / 审批 / 传单规则文档
```

然后由 LangGraph Diagnosis Workflow 把两类证据组合成受控 Root Cause、引用和建议。

---

## 2. ERP Diagnosis 主链

```text
POST /erp/diagnose
        ↓
analyze_request
        ↓
collect_business_evidence
        ↓
read-only ERP MCP tools
        ↓
diagnose_root_cause
        ↓
controlled Root Cause Code
        ↓
retrieve_policy
        ↓
Agentic RAG (hybrid)
        ↓
compose_diagnosis
        ↓
verify_diagnosis
        ↓
structured response + trace
```

当前 ERP 主链**没有为了展示技术而强行引入 GraphRAG 或 Multi-Agent**。

---

## 3. 五个只读 ERP MCP Tools

```text
erp_get_user_access_profile
erp_get_document_context
erp_check_operation_permission
erp_get_approval_context
erp_get_transfer_context
```

核心原则：

- 不暴露任何角色、权限、审批流写操作；
- 每个 Tool 使用独立 ERP Read Scope；
- Tool Result 可以包含诊断需要的结构化业务事实；
- Audit Trace 只保留参数名、HMAC 参数指纹、授权结果和最小结果摘要；
- 原始业务参数不复制进业务审计事件。

MCP Registry 当前合计 **15 个 Tool**：10 个平台 Tool + 5 个 ERP Read-only Tool。

---

## 4. Root Cause Taxonomy

业务根因不是由 LLM 自由生成，而是约束在受控 Code 中：

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

LLM / RAG 负责理解与解释，实时业务事实由 Tool 提供，核心诊断原因由结构化规则和受控 Taxonomy 约束。

---

## 5. Policy RAG

ERP 规范知识库：

```text
knowledge/erp/
├── permission_rules.md
├── approval_rules.md
└── transfer_rules.md
```

根因先决定 Policy Domain，再在对应文档域内执行 Agentic RAG：

```text
ROLE / ORG / DATA / STATE
→ permission_rules.md

APPROVAL_FLOW / APPROVER
→ approval_rules.md

TRANSFER_RULE
→ transfer_rules.md
```

这样可以避免已经确定为“权限域”的 Root Cause 被全局相似度错误地引用到审批规则。

默认后端继续使用 `hybrid`，不隐式依赖实时 Neo4j。

---

## 6. Synthetic ERP Service

目录：

```text
examples/synthetic_erp_service/
```

数据全部虚构，包含：

- 用户与角色；
- 组织授权范围；
- 数据权限；
- 单据及生命周期状态；
- 审批流；
- 传单规则。

服务只提供 GET 接口，没有角色、权限、审批流写接口。

### In-process adapter

默认 CI / Golden Case 使用：

```text
SyntheticERPReadService
```

优点：

- 确定性；
- 无网络依赖；
- 快速回归。

### HTTP adapter

最终 E2E 增加：

```text
SyntheticERPHttpReadService
```

它通过真实 HTTP 访问 Synthetic ERP FastAPI Service，同时满足：

- 仅允许 loopback 地址；
- MCP Security 明确记录 `requested_network=true`；
- 普通 no-network ERP Principal 会被拒绝；
- 专用 loopback HTTP Principal 仍然只有 ERP read scopes；
- 仍不暴露任何 write tool。

验证：

```bash
python scripts/run_erp_http_e2e.py
```

详细边界见 `docs/ERP_DIAGNOSIS_E2E.md`。

---

## 7. 安全原则

### 7.1 Capability 最小化

模型无法发现不存在的写 Tool。

```text
不存在：
erp_grant_role
erp_update_permission
erp_bind_approval_flow
...
```

### 7.2 Scope + Runtime Security

ERP Tools 需要独立 read scope，并继续通过现有 MCP Security Policy。

### 7.3 Network Boundary

默认 ERP Workflow 无网络依赖。

Synthetic HTTP E2E 必须同时满足：

```text
loopback URL validation
+
requested_network=true
+
network-enabled readonly principal
```

### 7.4 Fallback 不跨证据类型

```text
静态 Policy RAG 故障
→ 可以做知识侧降级

实时 ERP 事实依赖故障
→ DEPENDENCY_UNAVAILABLE
→ 不允许拿静态文档猜用户当前权限
```

---

## 8. 审计与 Trace

两层记录：

```text
erp_diagnosis_step
→ Workflow 节点、状态、Root Cause、Citation 数量

erp_mcp_tool_audit
→ Tool、Principal、授权结果、参数指纹、最小结果摘要
```

业务审计默认：

```text
raw_argument_values_recorded = false
```

真实接入时 `ERP_AUDIT_HMAC_KEY` 必须由 Secret Manager / Environment Secret 注入。

---

## 9. 业务 Golden Acceptance

冻结 ERP 数据集：

```text
eval_cases/erp_diagnosis_golden.jsonl
```

固定 **20 个业务 Golden Cases**，覆盖：

- 角色缺失；
- 组织范围不足；
- 数据权限不足；
- 单据状态异常；
- 审批流未绑定；
- 审批人无法解析；
- 传单规则缺失；
- 正常操作；
- 多根因；
- 输入不足；
- 不存在单据；
- 实时依赖故障与受控弃权。

验收维度：

```text
Root Cause Exact Match
Required Tool Hit
Forbidden Tool Absent
Read-only Tool Set
Policy Source Hit
Controlled Abstention
Verification Pass
Trace Coverage
Audit Event Count
Audit Raw Argument Absence
Failure Trace Coverage
```

当前已验证业务基线：

```text
ERP Business Golden Cases     20 / 20 passed
Diagnostic cases              14
Abstention cases               6
Fault-injection cases          4
All business metrics           100% on the frozen synthetic set
```

这个结果只证明冻结 Synthetic Business Contract，不代表真实 ERP 生产覆盖率或统计泛化能力。

原平台 Closure Golden Cases 仍保留：

```text
Generic Agent Closure         40 / 40 passed
```

---

## 10. 通用 Agent-API 平台能力

ERP Reference Application 只是平台的一个业务实例。

底座同时保留：

### Tool Calling Agent

```text
START → agent → tools_condition
                  ├─ END
                  └─ tools → agent → END
```

同时保留：

- Deterministic Agent：CI / 回归；
- Ollama Tool Calling：真实 `tool_calls` 验证。

### State / Memory

- `MessagesState`
- Reducer
- SQLite Checkpointer
- `thread_id`
- Trace ID

ERP Diagnosis 使用独立 Checkpoint DB，避免和通用 Agent 状态空间混用。

### Agentic RAG

```text
query_analyzer
→ query_rewriter
→ retrieve
→ relevance_grade
→ answer_with_citations
```

可选后端：

```text
hybrid
chroma
chroma_rerank
graph_fusion
```

### GraphRAG

保留：

```text
Document
Chunk
Entity
HAS_CHUNK / NEXT_CHUNK / MENTIONS / RELATED_TO
Neo4j ingestion / retrieval
graph + vector fusion
dry_run
```

它是平台增强能力，不是 ERP Diagnosis 主链的必要组件。

### Multi-Agent

保留固定、可测试的角色编排：

```text
Planner
→ Researcher
→ Tool
→ Critic
→ Memory
→ Reflection
→ Supervisor
```

它用于验证多角色共享状态与编排，不宣称生产级自治 Agent Cluster。

---

## 11. API

核心业务接口：

```text
POST /erp/diagnose
```

其他平台接口继续保留，例如：

```text
POST /agent/chat
POST /agent/debug
POST /agent/smart-chat
POST /agent/smart-stream

POST /rag/search
POST /rag/agentic-debug
POST /rag/answer-verify-debug

POST /graph/fusion-debug

POST /multi-agent/supervisor-debug

GET  /observability/traces
GET  /observability/traces/{trace_id}
```

---

## 12. 本地运行

安装：

```bash
python -m pip install -r requirements-dev.txt
```

启动 Agent-API：

```bash
uvicorn src.app.main:app --reload
```

业务诊断示例：

```bash
curl -X POST http://127.0.0.1:8000/erp/diagnose \
  -H 'content-type: application/json' \
  -H 'x-trace-id: erp-demo-001' \
  -d '{
    "query":"为什么这张采购订单提交不了？",
    "user_id":"SYN-U001",
    "document_id":"SYN-PO-002",
    "operation":"SUBMIT",
    "thread_id":"erp-demo-thread-001"
  }'
```

---

## 13. 验收命令

```bash
python -m pip check
python -W error -m compileall -q src examples scripts tests
python -m pytest -q

python scripts/run_erp_diagnosis_eval.py
python scripts/run_erp_http_e2e.py

git diff --check
```

CI 同时执行完整 pytest、ERP Business Golden Acceptance 和 Synthetic ERP HTTP E2E。

---

## 14. 项目边界

可以对外声称：

- 实现了可复用 Agent-API 底座；
- 在底座上实现了 ERP 权限与流程诊断 Reference Application；
- MCP 封装只读业务能力；
- Synthetic HTTP Service 验证了微服务边界；
- Root Cause、Tool、Citation、Trace、Audit 和 Failure 均进入业务 Golden Acceptance。

不能声称：

- 接入过前公司生产 ERP；
- 使用过真实客户数据；
- 已生产上线；
- 20/20 等于真实业务 100% 准确率；
- GraphRAG / Multi-Agent 是 ERP 主链的必需组件；
- Verification 能证明自然语言事实的绝对真值。
