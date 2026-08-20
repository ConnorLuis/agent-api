# agent-api 项目交接文档

本文档面向后续维护者、复习者和项目接手人员。

原始 `HANDOFF.md` 记录了大量按 DayXX 划分的开发过程。本精简版已将重复内容合并为阶段成果，只保留：

- 项目最终定位。
- 已完成能力。
- 核心架构和关键决策。
- 默认配置与安全边界。
- 测试和运行要求。
- 已知限制、暂缓事项和冻结后的维护原则。

---

## 1. 项目基本信息

项目名称：`agent-api`

技术主线：

```text
FastAPI
+ LangGraph Agent
+ Tool Calling
+ short-term memory
+ Router / Smart Chat
+ RAG / Agentic RAG
+ GraphRAG / Neo4j
+ Multi-Agent
+ MCP
+ observability
+ evaluation
```

最终验收状态：

```text
40 / 40 golden cases passed
328 pytest passed
dependency check clean
0 skipped
0 warnings
failure attribution empty
```

项目当前阶段已完成，默认状态：

```text
FROZEN
```

后续除 correctness / security bug、依赖升级或 CI 维护外，不再新增功能。

最终仓库收口已补齐 `.env.example`、依赖分层、版本约束和严格 CI，不包含新 Agent 或新部署功能。

## 2. 与 chat-api 的项目边界

两个项目必须保持不同定位。

### agent-api

```text
Agent / RAG / GraphRAG / Multi-Agent / MCP 工作流系统
```

用于证明：

- Agent Graph 设计能力。
- Tool Calling 与状态管理能力。
- 复杂 RAG Pipeline 设计能力。
- 图谱检索和图向量融合能力。
- 多智能体状态编排能力。
- MCP Server / Client、安全与集成能力。

### chat-api

```text
Production-grade LLM Chat Backend / LLM Gateway
```

应重点证明：

- 多 Provider 接入。
- 对话和消息持久化。
- 标准化 Streaming。
- Token Usage 和成本统计。
- API Key、限流、配额。
- Cache、Retry、Timeout、Fallback。
- 部署、Metrics、压测和生产可用性。

### 强制边界

不要在 `chat-api` 中重复以下模块：

```text
复杂 Agent Graph
Agentic RAG
GraphRAG
Multi-Agent Supervisor
MCP 平台层
```

---

## 3. 已完成阶段总览

### 3.1 Agent 基础设施

已完成：

- FastAPI 项目结构。
- 确定性 LangGraph Agent。
- `add`、`multiply`、知识库检索工具。
- 真实 Ollama Tool Calling Agent。
- `ToolNode` 与 `tools_condition`。
- SQLite Checkpointer 短期记忆。
- 按 `thread_id` 隔离会话。
- Request Logging 与 `x-trace-id`。
- Debug Endpoint。
- Deterministic / LLM SSE Streaming。
- Mock / Ollama Provider 抽象。

关键设计：

```text
确定性路径：用于 CI、回归测试和图流程讲解
真实 LLM 路径：用于验证模型是否真实生成 tool_calls
```

### 3.2 Router 与统一入口

已完成：

- Deterministic Router Agent。
- Calculator / RAG / Chat 三路路由。
- Router Delegation，复用已有 Agent Graph 和 Memory。
- Router Debug 与 SSE。
- LLM Router，支持 Mock 和 Ollama。
- Smart Chat / Smart Stream 统一入口预览。
- Route Validation Metadata 与非法路由回退。

关键设计：

> Router 只负责任务分流，不重复实现已有工具、RAG 和记忆逻辑。

### 3.3 RAG 与 VectorRAG

已完成：

- 本地 Markdown Knowledge Base。
- Keyword Retriever。
- Chunk Pipeline。
- Deterministic Embedding 和 Vector Search Debug。
- Hybrid Retrieval。
- SQLite Vector Store Debug。
- `EmbeddingProvider` 抽象。
- Chroma Persistent Vector Store。
- 可选本地 BCE `sentence-transformers` 模型。
- Agentic RAG Graph。
- Query Analysis、Query Rewrite、Relevance Grade。
- Citation-aware Answer。
- SSE Streaming。
- Answer Verification。
- 多后端切换：`hybrid`、`chroma`、`chroma_rerank`、`graph_fusion`。
- 多后端 Evaluation、Pairwise Delta 和 Summary。
- Extended Evaluation Dataset。
- Failure Analysis 和保守型 Backend Selection Guidance。

重要结论：

```text
VectorRAG 工程层已经足够完整。
不要继续无限扩展检索后端选择策略，而忽略项目主线。
```

### 3.4 GraphRAG + Neo4j

已完成：

- Graph Schema。
- Neo4j Client Boundary。
- CI-safe Health Debug。
- 确定性 Entity / Relation Extraction。
- Neo4j Ingestion Dry-run 与 Live Execution。
- Graph Retrieval。
- GraphRAG + VectorRAG Fusion。
- Agentic RAG `graph_fusion` Backend。
- GraphRAG Evaluation。
- GraphRAG-aware Trace 和 Answer Verification。
- `docs/GRAPHRAG.md` 架构文档。

图结构：

```text
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:NEXT_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS]->(Entity)
(Entity)-[:RELATED_TO]->(Entity)
```

种子知识库当前可识别的核心实体包括：

```text
Agent
RAG
LangGraph
Tool
Memory
```

GraphRAG 的工程边界：

- 支持 `dry_run`，CI 不要求实时 Neo4j。
- `graph_fusion` 必须显式指定。
- 默认检索后端仍是 `hybrid`。
- 图检索和向量检索通过 `chunk_id` 合并。
- 结果保留 `graph_score`、`vector_score`、`fusion_score` 和来源元数据。

### 3.5 Multi-Agent

已完成：

- 共享 `MultiAgentState`。
- Planner。
- Researcher。
- Tool Agent。
- Critic。
- Memory Agent。
- Reflection Agent。
- Supervisor Graph。
- Multi-Agent SSE。
- Multi-Agent Eval / Trace。
- `docs/MULTI_AGENT.md` 架构文档。

当前执行顺序：

```text
planner
  → researcher
  → tool
  → critic
  → memory
  → reflection
  → supervisor
```

Multi-Agent 当前定位：

```text
确定性、可测试、CI-safe 的状态编排与角色职责演示
```

它目前不是：

- 生产级自治智能体集群。
- 并发 Agent Runtime。
- LLM 驱动的动态角色选择系统。
- 可执行真实 Shell 或自动修改仓库的工具系统。

### 3.6 MCP Integration

已完成：

- 官方 MCP Python SDK。
- 标准 FastMCP Server。
- 真实 stdio MCP Client。
- MCP Tool Registry。
- MCP Resource Registry。
- Local Marketplace Catalog。
- External Server Catalog Metadata。
- MCP Client Wrapper。
- Tool / Resource List、Call 和 Read。
- Scope Permission。
- Tool / Server Security Evaluation。
- External Server Allowlist。
- Graph `dry_run` Enforcement。
- Write / Destructive Request Blocking。
- Security Audit Trace。
- Endpoint Coverage Report。
- Endpoint-equivalent Probe。
- Main Agent MCP Gateway。
- MCP Disabled / Enabled / Failure Fallback Tests。

当前 MCP Tool 数量：

```text
10
```

当前 MCP Resource 数量：

```text
9
```

Main Agent 集成行为：

```text
MCP disabled:
  source = internal_search_knowledge
  fallback_used = false

MCP enabled and successful:
  source = mcp_agentic_rag_query
  保留 security_decision / security_audit_trace / mcp_boundary

MCP enabled but failed:
  source = internal_search_knowledge
  fallback_used = true
  不向最终用户暴露 MCP 内部异常
```

---

## 4. 核心架构决策

### 4.1 确定性路径与真实模型路径并存

原因：

- CI 不能依赖本地 Ollama。
- 确定性路径更适合验证图结构、状态和工具调用契约。
- 真实模型路径用于证明 Tool Calling 并非硬编码模拟。

因此：

```text
CI / 回归测试：Deterministic 或 Mock
本地人工验证：Ollama
```

### 4.2 所有外部依赖都有安全边界

- Ollama 不进入强制 CI。
- Neo4j 默认关闭。
- Graph 操作支持 `dry_run`。
- External MCP Server 默认关闭。
- CI 不访问网络。
- Write / Destructive MCP Tool 默认阻断。

### 4.3 默认检索后端锁定为 hybrid

```text
DEFAULT_RETRIEVAL_BACKEND = hybrid
```

不能随意修改为 `graph_fusion`，原因：

- `hybrid` 不要求实时 Neo4j。
- 更适合本地默认运行和 CI。
- `graph_fusion` 属于增强路径，应由调用方显式选择。

### 4.4 复用现有能力而非复制代码

- Router 委派给已有 Agent Graph。
- Agentic RAG 的 `graph_fusion` 复用 Graph Fusion Boundary。
- MCP Tool Wrapper 复用现有 RAG、GraphRAG、Multi-Agent 和 Observability 能力。
- Main Agent MCP Gateway 保留内部知识库检索作为 fallback。

### 4.5 Debug Endpoint 是工程能力的一部分

本项目大量使用 `*-debug` Endpoint，目的不是暴露临时接口，而是：

- 显示节点执行顺序。
- 显示 Tool Call 参数和结果。
- 展示检索分数和融合元数据。
- 检查 Graph Dry-run Plan。
- 输出角色状态、Artifact 和 Memory。
- 支持面试时逐层解释系统行为。

---

## 5. 必须保持的默认配置

### 5.1 Main Agent MCP

```env
AGENT_API_MAIN_AGENT_MCP_ENABLED=false
AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED=true
AGENT_API_MAIN_AGENT_MCP_MODE=local_wrapper
AGENT_API_MAIN_AGENT_MCP_SERVER_ID=agent-api-local
```

不要在没有明确需求时将 MCP 默认开启。

### 5.2 Neo4j

```env
NEO4J_ENABLED=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```

### 5.3 Ollama

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TEMPERATURE=0
```

### 5.4 Retrieval

```text
DEFAULT_RETRIEVAL_BACKEND = hybrid
```

---

## 6. 主要模块位置

```text
src/app/main.py
  FastAPI 应用入口与路由注册

src/app/agent/
  Agent Graph、工具、Memory 和 Main Agent MCP Gateway

src/app/llm/
  Mock / Ollama Provider 抽象

src/app/rag/
  Chunk、Retriever、Embedding、Vector Store、Agentic RAG

src/app/graph/
  Schema、Extraction、Ingestion、Retrieval、Fusion、Neo4j Client

src/app/multi_agent/
  State、各角色 Agent、Supervisor、Streaming、Evaluation

src/app/mcp_integration/
  Server、Client、Registry、Marketplace、Permission、Security、Probe

src/app/evaluation/
  RAG Backend Evaluation、Report、Failure Analysis

src/app/observability/
  Trace Event、Trace Store、查询接口

src/app/routes/
  FastAPI Endpoint

src/app/schemas/
  Pydantic Request / Response Model
```

项目数据：

```text
knowledge/    Git 管理的知识库
eval_cases/    RAG 评估数据
 docs/         架构和阶段文档
 data/         运行时 SQLite / Chroma 数据，Git 忽略
```

---

## 7. 主要 API 交接

### 7.1 Agent

```text
GET  /health
POST /agent/chat
POST /agent/debug
POST /llm/chat
POST /agent/llm-chat
POST /agent/llm-debug
POST /agent/stream
POST /agent/llm-stream
```

### 7.2 Router / Smart Chat

```text
POST /agent/router-chat
POST /agent/router-debug
POST /agent/router-stream
POST /agent/llm-router-chat
POST /agent/smart-chat
POST /agent/smart-stream
```

### 7.3 RAG

```text
POST /rag/search
POST /rag/search-debug
POST /rag/chunks-debug
POST /rag/vector-search-debug
POST /rag/hybrid-search-debug
POST /rag/agentic-debug
POST /rag/agentic-stream
POST /rag/answer-verify-debug
POST /rag/vector-store-debug
POST /rag/embedding-debug
POST /rag/chroma-search-debug
POST /rag/eval-debug
POST /rag/backend-eval-debug
```

### 7.4 GraphRAG

```text
GET  /graph/schema-debug
GET  /graph/health-debug
POST /graph/extract-debug
POST /graph/ingest-debug
POST /graph/retrieval-debug
POST /graph/fusion-debug
```

### 7.5 Multi-Agent

```text
POST /multi-agent/state-debug
POST /multi-agent/plan-debug
POST /multi-agent/research-debug
POST /multi-agent/tool-debug
POST /multi-agent/critic-debug
POST /multi-agent/memory-debug
POST /multi-agent/reflection-debug
POST /multi-agent/supervisor-debug
POST /multi-agent/stream
POST /multi-agent/eval-debug
```

### 7.6 Observability

```text
GET /observability/traces
GET /observability/traces/{trace_id}
```

---

## 8. 测试与验证状态

最终 release acceptance 已完成完整测试、golden evaluation、failure injection、checkpoint recovery 和 trace replay 验证。

### 完整测试

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -W error -m compileall -q src scripts tests
python -m pytest -q
```

最终结果：

```text
No broken requirements found.
warnings-as-errors compile passed
328 passed, 0 skipped, 0 warnings
```

Starlette TestClient 通过 `httpx2` 运行，MCP 所需 `pydantic-settings` 固定在已验证的无 warning 版本。真实本地语义模型由 `scripts/validate_semantic_embedding_provider.py` 手动验证；CI 中的 Provider 契约测试不依赖本机模型路径。

### Golden Set

固定文件：

```text
eval_cases/agent_closure_golden.jsonl
```

总计 40 条：

```text
Router              12
Tool                10
RAG                 10
End-to-end            4
Failure / recovery    4
```

### 正式指标

```text
Router Accuracy                 16 / 16 = 100%
Dedicated Router                12 / 12 = 100%
Tool Call Success Rate          12 / 12 = 100%
Tool Parameter Accuracy         12 / 12 = 100%
RAG source Recall@3             10 / 10 = 100%
Task Completion Rate            24 / 24 = 100%
Failure/Recovery Validation      4 / 4  = 100%
Failure Trace Coverage           4 / 4  = 100%
```

最终评测状态：

```text
passed_cases            = 40
failed_or_error_cases   = 0
failure_count           = 0
failure_attribution     = []
```

### Failure / Recovery

已验证：

1. tool timeout；
2. tool exception；
3. duplicate tool call；
4. SQLite checkpoint recovery。

Checkpoint recovery 使用相同 `thread_id` 验证现有 SqliteSaver 状态恢复能力。

### Trace Replay

HTTP：

```text
GET /observability/traces/{trace_id}
```

SQLite：

```python
get_trace_events(trace_id)
```

最终 Failure Trace Coverage：

```text
4 / 4 = 100%
```

### RAG Evaluation 限制

当前 committed local KB 只有一个知识文档，因此：

```text
RAG source Recall@3 = 10 / 10
```

仅用于证明当前检索链路与 gold-source retrieval correctness；不要将该数字解释为大型多文档知识库上的通用检索性能。

## 9. 运行与数据注意事项

### 9.1 环境

```bash
conda create -n agentapi python=3.10 -y
conda activate agentapi
python -m pip install -r requirements-dev.txt
python -m uvicorn src.app.main:app --reload --port 8000
```

### 9.2 依赖分层

```text
requirements.txt       运行依赖
requirements-dev.txt   测试与本地验收依赖
constraints.txt        已验证的精确版本边界
```

不要直接使用：

```bash
pip freeze > requirements.txt
```

原因：Conda 环境可能输出本地 Build Artifact Path，导致 GitHub Actions 安装失败。

### 9.3 数据目录

运行时文件：

```text
data/
*.sqlite
*.sqlite-shm
*.sqlite-wal
*.sqlite-journal
```

应保持 Git Ignore。

知识库：

```text
knowledge/
```

知识库属于源码，必须使用 UTF-8。

如果 Windows 编辑导致 `UnicodeDecodeError`，可转换编码：

```bash
iconv -f gbk -t utf-8 knowledge/agent_basics.md -o /tmp/agent_basics.md
mv /tmp/agent_basics.md knowledge/agent_basics.md
```

中文 JSON 查看建议：

```bash
python -m json.tool --no-ensure-ascii
```

---

## 10. 安全与稳定性约束

后续修改必须继续满足：

1. Main Agent MCP 默认关闭。
2. MCP Fallback 默认开启。
3. External MCP Server 默认关闭。
4. CI 不启动 External MCP Server。
5. CI 不依赖网络和 Live Neo4j。
6. Graph Mutation 必须支持或强制 `dry_run`。
7. Write / Destructive Tool 默认阻断。
8. 所有 MCP Tool Wrapper 保留 `security_decision`。
9. 所有 MCP Tool Wrapper 保留 `security_audit_trace`。
10. `graph_fusion` 保持非默认。
11. `DEFAULT_RETRIEVAL_BACKEND` 保持 `hybrid`。
12. 不改变现有 REST Endpoint 的默认行为。
13. MCP 失败不能直接破坏 `/agent/chat` 和 `/agent/debug` 的可用性。

---

## 11. 已知限制

### 11.1 Agent

- 真实模型主要验证 Ollama，尚未扩展到完整生产级多 Provider。
- Tool 集合仍然较小。
- SQLite Memory 适合项目演示，不等同于分布式生产会话系统。

### 11.2 RAG

- 知识库规模较小。
- 文档上传与解析 Pipeline 尚未实现。
- Backend Selection Report 主要用于工程分析，尚未固化为生产运行策略。
- 本地语义 Embedding 可能依赖特定机器模型路径。

### 11.3 GraphRAG

- 当前 Entity Extraction 使用确定性别名匹配，不是通用 NER / Relation Extraction 模型。
- 种子图规模小。
- `RELATED_TO` 使用 `MERGE` 时，相同实体对的多次共现会折叠为唯一关系。
- 暂未实现复杂实体消歧、时间关系和证据级关系列表。

### 11.4 Multi-Agent

- 当前为顺序确定性执行。
- 无真实并发调度。
- 默认不调用 LLM。
- Tool Agent 不执行真实 Shell 或代码修改。
- Supervisor 主要验证编排契约，不是分布式 Agent Runtime。

### 11.5 MCP

- Main Agent 当前使用 `local_wrapper` 模式。
- External Server 仅存在 Catalog 和 Manual Validation Metadata。
- External Server 不在 CI 中实际启动。
- 高风险写工具尚未开放。

---

## 12. 暂缓事项

以下内容不是当前 release blocker，也不应在封板前继续扩展：

- 更多 Agent 类型；
- 更多 Router 路由类型；
- 更复杂的 Supervisor 编排；
- 新的 RAG backend；
- 大规模 retrieval benchmark；
- 新的 MCP marketplace 能力；
- 分布式 checkpoint / trace storage；
- 为展示项目体量而新增模块。

未来如确有业务需求，应重新立项评估，而不是默认继续当前开发周期。

## 13. 下一步项目方向

项目已经完成当前阶段工程目标。

默认状态：

```text
FROZEN
```

后续只接受三类工作：

1. correctness / security bug fix；
2. 依赖与 CI 维护；
3. 面试复习与项目讲解材料维护。

任何代码修改必须：

- 使用独立分支；
- 有明确问题定义；
- 补 regression test；
- 保持现有 golden evaluation 不被削弱；
- 完整 `pytest -q` 通过后才能合并。

新的 Agent、机器人、具身智能或其他实验方向应放入独立仓库。

## 14. 面试讲解建议

推荐按以下顺序介绍项目：

```text
1. 项目为什么不是普通 Chat API
2. LangGraph Agent 与 Tool Calling
3. SQLite Memory 与 Trace
4. Router 和 Smart Chat
5. 从 Keyword RAG 到 Agentic RAG
6. Chroma、Rerank 和 Backend Evaluation
7. GraphRAG + Neo4j + Vector Fusion
8. Multi-Agent 角色与 Supervisor
9. MCP Server / Client / Security
10. 默认关闭、dry_run、fallback 和 CI-safe 设计
```

需要明确区分：

- “已真实运行”的能力。
- “确定性模拟用于验证架构”的能力。
- “仅作为未来扩展边界”的能力。

推荐项目表述：

> 我实现了一个基于 FastAPI 和 LangGraph 的 Agent 后端。系统从确定性 Tool Calling 和 SQLite 短期记忆开始，逐步扩展到 Hybrid RAG、Chroma、Agentic RAG、GraphRAG + Neo4j、多智能体 Supervisor 工作流，以及标准 MCP Server / Client 和安全网关。项目保留了 Mock、dry-run、fallback 和 Trace 机制，使核心流程在没有 Ollama、Neo4j 和外部 MCP Server 的 CI 环境中仍可稳定验证。

---

## 15. 接手检查清单

接手后先确认：

```text
[ ] Python 3.10 环境可用
[ ] python -m pip install -r requirements-dev.txt 成功
[ ] python -m pip check 通过
[ ] warnings-as-errors compile 通过
[ ] GET /health 返回 status=ok
[ ] pytest -q 为 328 passed、0 skipped、0 warnings
[ ] DEFAULT_RETRIEVAL_BACKEND 仍为 hybrid
[ ] AGENT_API_MAIN_AGENT_MCP_ENABLED 仍为 false
[ ] AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED 仍为 true
[ ] NEO4J_ENABLED 默认仍为 false
[ ] /agent/chat 与 /agent/debug 默认行为未改变
[ ] MCP Tool Wrapper 仍返回 security_decision 和 security_audit_trace
[ ] graph_fusion 未被设为默认
[ ] External MCP Server 未在 CI 中启动
[ ] data/ 与 SQLite 运行时文件未提交 Git
```

---

## 16. 术语说明

| 术语 | 中文说明 |
|---|---|
| Deterministic | 结果由固定规则决定，便于稳定测试 |
| Tool Calling | 模型生成结构化工具调用，由系统执行 |
| Checkpointer | 保存 LangGraph 状态和会话上下文 |
| Provider | 对不同 LLM 服务的统一封装 |
| RAG | 检索增强生成 |
| Agentic RAG | 由 Agent 控制检索决策和回答步骤 |
| GraphRAG | 将知识图谱关系加入检索上下文 |
| Rerank | 对初次检索结果进行二次排序 |
| Observability | 对请求、节点、检索和结果进行可观测记录 |
| Trace | 一次请求的完整执行轨迹 |
| Multi-Agent | 多个分工不同的 Agent 协作 |
| Supervisor | 多智能体编排与汇总角色 |
| MCP | Model Context Protocol，模型上下文协议 |
| Scope | MCP 权限范围 |
| Allowlist | 允许访问的 Server 或操作白名单 |
| Fallback | 主路径失败时切换到安全备用路径 |
| CI-safe | 在 CI 中无需外部服务即可稳定运行 |
| dry_run | 只生成计划，不真正写入或执行高风险操作 |
