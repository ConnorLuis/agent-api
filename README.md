# agent-api

`agent-api` 是一个基于 **FastAPI + LangGraph** 构建的 Agent 后端项目，用于系统化实现并验证以下能力：

- Tool Calling Agent（工具调用智能体）
- 短期记忆与请求追踪
- SSE 流式输出
- Router Agent 与统一 Smart Chat 入口
- RAG、VectorRAG、Agentic RAG 与检索评估
- GraphRAG + Neo4j
- Multi-Agent 工作流
- MCP Server / Client、安全策略与主 Agent 集成

本项目最初按照 Day1–Day72 的方式迭代。本文档已经去除逐日流水账，只保留项目最终能力、核心架构、使用方法、重要边界和验证结果。

---

## 1. 项目定位

`agent-api` 与 `chat-api` 的定位不同：

```text
agent-api:
  Agent / RAG / GraphRAG / Multi-Agent / MCP 工作流项目

chat-api:
  面向生产环境的 LLM Chat Backend / LLM Gateway 项目
```

两者共同构成完整的 LLM 应用工程能力组合：

- `chat-api` 侧重多模型接入、会话管理、鉴权、限流、成本统计、容错和部署。
- `agent-api` 侧重复杂 Agent 工作流、检索增强、知识图谱、多智能体协作和 MCP 集成。

一句话定位：

> 一个基于 FastAPI + LangGraph 的 Agentic RAG / GraphRAG / Multi-Agent / MCP 后端系统。

---

## 2. 当前状态

`agent-api` 已完成当前阶段的工程收口与 release acceptance，功能开发默认冻结。

最终验收基线：

```text
Golden cases                    40 / 40 passed
Router Accuracy                 16 / 16 = 100%
Tool Call Success Rate          12 / 12 = 100%
Tool Parameter Accuracy         12 / 12 = 100%
RAG source Recall@3             10 / 10 = 100%
Task Completion Rate            24 / 24 = 100%
Failure/Recovery Validation      4 / 4  = 100%
Failure Trace Coverage           4 / 4  = 100%
Full pytest                     328 passed
Dependency check                clean
Skipped tests                   0
Warnings                        0
```

Closure 中验证的稳定性场景包括：

- tool timeout；
- tool exception；
- duplicate tool call；
- SQLite checkpoint recovery；
- trace-required case 的 trace 持久化与回放。

最终 `failure_attribution = []`。

仓库与 CI 收口也已完成：

- `.env.example` 与实际配置口径一致；
- `requirements.txt` 仅保留运行依赖，测试依赖放入 `requirements-dev.txt`；
- `constraints.txt` 固定已验证的 Python 3.10 依赖边界；
- CI 执行 `pip check`、warnings-as-errors 编译和完整 pytest。

当前维护策略为 **freeze + interview review**。除明确的 correctness / security bug、依赖升级或 CI 维护外，不继续扩展 Agent 类型、Router 路由、Multi-Agent 工作流、RAG backend 或 MCP 功能。

## 3. 核心能力

### 3.1 Agent 与 Tool Calling

项目同时提供两条 Agent 路径：

1. **Deterministic Agent**：使用确定性规则决定是否调用工具，便于测试、调试和 CI。
2. **Real LLM Tool Calling Agent**：通过 Ollama 模型生成真实 `tool_calls`，再由 LangGraph 的 `ToolNode` 执行工具。

当前内置工具包括：

- `add`：加法计算。
- `multiply`：乘法计算。
- `search_knowledge_base`：检索本地知识库；可通过 MCP-aware Gateway 路由。

典型执行图：

```text
START
  ↓
agent
  ├── 无工具调用 ───────────────→ END
  └── 生成 tool_calls
          ↓
        tools
          ↓
        agent
          ↓
         END
```

其中：

- `agent` 节点负责分析输入并决定是否调用工具。
- `tools` 节点负责执行工具并生成 `ToolMessage`。
- 第二次进入 `agent` 后，Agent 根据工具结果生成最终回答。

### 3.2 短期记忆与可观测性

项目通过 SQLite Checkpointer 保存按 `thread_id` 隔离的短期记忆。

```text
相同 thread_id：共享同一会话状态
不同 thread_id：状态相互隔离
```

每个请求支持 `x-trace-id`：

- 客户端可主动传入。
- 未传入时由服务端生成。
- Trace ID 会写入响应头、响应体和内部 Trace Event。

Observability（可观测性）接口支持：

- 查询最近的 Trace。
- 按 `trace_id` 查询完整执行事件。
- 保留检索元数据、GraphRAG 贡献信息和答案验证结果。

### 3.3 Router Agent 与 Smart Chat

Router Agent 将请求划分为三类：

```text
calculator：计算任务
rag：知识检索任务
chat：普通对话任务
```

项目提供：

- 确定性 Router。
- LLM Router（支持 Mock 与 Ollama）。
- Router Debug。
- Router SSE Streaming。
- Smart Chat 统一入口预览。
- 路由结果验证与非法路由回退。

Router 的核心价值不是重复实现业务逻辑，而是将请求委派给已经存在的 Agent Graph、RAG 和 Chat 路径。

### 3.4 RAG 与 Agentic RAG

项目的检索能力按照工程复杂度逐步扩展，目前包括：

- 本地 Markdown 知识库。
- Keyword Retrieval（关键词检索）。
- Deterministic Vector Search（确定性向量检索调试层）。
- Hybrid Retrieval（关键词信号与向量信号融合）。
- SQLite Vector Store 调试层。
- Chroma 持久化向量库。
- `EmbeddingProvider` 抽象层。
- 可选本地 `sentence-transformers` 语义 Embedding。
- `chroma_rerank` 重排扩展。
- 多后端对比与评估报告。
- Agentic RAG 工作流。
- 引用感知回答与答案验证。

Agentic RAG 不是单次“检索后回答”，而是一个可控图流程：

```text
query_analyzer
  ├── 不需要检索 → direct_answer
  └── 需要检索
          ↓
     query_rewriter
          ↓
       retrieve
          ↓
   relevance_grade
          ↓
 answer_with_citations
```

主要检索后端：

```text
hybrid          默认后端，CI 安全
chroma          Chroma 向量检索
chroma_rerank   Chroma + 重排
graph_fusion    GraphRAG + VectorRAG 融合，需显式指定
```

> `graph_fusion` 保持非默认状态，避免在 CI 或普通开发环境中隐式依赖实时 Neo4j。

### 3.5 GraphRAG + Neo4j

GraphRAG 模块提供从知识块到图检索、再到图向量融合的完整边界。

当前图模型：

```text
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:NEXT_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS]->(Entity)
(Entity)-[:RELATED_TO]->(Entity)
```

节点类型：

- `Document`：知识源文档。
- `Chunk`：由 RAG Chunk Pipeline 切分出的文本块。
- `Entity`：通过确定性别名规则抽取的实体。

关系类型：

- `HAS_CHUNK`：文档包含文本块。
- `NEXT_CHUNK`：同一文档中相邻文本块的顺序关系。
- `MENTIONS`：文本块提到某个实体。
- `RELATED_TO`：同一上下文中的实体关联。

GraphRAG 处理流程：

```text
知识库 Markdown
  ↓
Chunk Pipeline
  ↓
Entity / Relation Extraction
  ↓
Neo4j Ingestion
  ↓
Graph Retrieval
  ↓
GraphRAG + VectorRAG Fusion
  ↓
Agentic RAG Answer
```

系统支持 `dry_run=true`：

- 只生成 Schema、Cypher 和执行计划。
- 不要求真实 Neo4j 服务。
- 适合 CI 和本地无 Neo4j 环境。

### 3.6 Multi-Agent 工作流

Multi-Agent 模块采用确定性、CI-safe 的顺序式工作流：

```text
Planner
  ↓
Researcher
  ↓
Tool Agent
  ↓
Critic
  ↓
Memory Agent
  ↓
Reflection Agent
  ↓
Supervisor
```

各角色职责：

| 角色 | 中文说明 |
|---|---|
| Planner | 将目标拆分为可执行任务，并生成计划 |
| Researcher | 针对计划收集和整理研究信息 |
| Tool Agent | 模拟或封装工具执行记录 |
| Critic | 检查任务状态、结果、边界和一致性 |
| Memory Agent | 将已批准的信息写入共享状态快照 |
| Reflection Agent | 对整个过程进行复盘并给出改进建议 |
| Supervisor | 编排节点、边和执行顺序，汇总最终状态 |

Multi-Agent 当前特征：

- 使用共享 `MultiAgentState`。
- 每个角色都有独立 Debug Endpoint。
- 提供确定性 SSE 事件回放。
- 提供 Eval / Trace 一致性检查。
- 默认不调用 LLM，不执行真实 Shell 命令，不修改仓库文件。

### 3.7 MCP Integration Layer

项目使用官方 MCP Python SDK 建立标准 MCP Server / Client 集成。

MCP（Model Context Protocol）用于让模型或 Agent 以统一协议发现并调用工具、读取资源。

已实现能力：

- 标准 `FastMCP` Server。
- 真实 stdio MCP Client。
- `tools/list`、`tools/call`、`resources/list`、`resources/read`。
- Tool Registry、Resource Registry 和 Marketplace Catalog。
- Scope 权限校验。
- Tool / Server 安全策略评估。
- External Server Allowlist。
- Graph 写操作 `dry_run` 强制。
- Write / Destructive 请求阻断。
- `security_decision` 与 `security_audit_trace`。
- REST Endpoint Coverage Report。
- CI-safe Endpoint-equivalent Probe。
- Main Agent MCP Gateway 与失败回退。

当前 MCP Tools：

```text
agentic_rag_query
graph_fusion_retrieve
multi_agent_eval_trace
answer_verify
rag_backend_eval
mcp_registry_summary
mcp_marketplace_discovery
mcp_security_report
mcp_endpoint_coverage_report
mcp_endpoint_probe
```

当前 MCP Resources：

```text
agent-api://mcp/tool-registry
agent-api://mcp/marketplace
agent-api://mcp/marketplace-discovery
agent-api://mcp/security-report
agent-api://mcp/endpoint-coverage
agent-api://graph/schema
agent-api://docs/graphrag
agent-api://docs/multi-agent
agent-api://docs/mcp-plan
```

Main Agent MCP Gateway 行为：

```text
search_knowledge_base()
  ↓
MCP-aware Gateway
  ├── MCP disabled → 原内部 search_knowledge() 路径
  ├── MCP enabled  → 调用 MCP agentic_rag_query
  └── MCP failed   → fallback 到内部检索（默认允许）
```

---

## 4. 技术栈

| 技术 | 作用 |
|---|---|
| Python 3.10 | 项目运行语言 |
| FastAPI | HTTP API 与 SSE Endpoint |
| Uvicorn | ASGI 服务启动器 |
| Pydantic / Pydantic Settings | 请求响应模型与配置管理 |
| LangGraph | Agent Graph、状态流转和 Checkpoint |
| LangChain Core | Message、Tool 与模型接口抽象 |
| LangChain Ollama | 接入本地 Ollama 模型 |
| SQLite | Agent Checkpoint、短期记忆与调试型向量存储 |
| ChromaDB | 持久化向量数据库 |
| sentence-transformers | 可选本地语义 Embedding |
| Neo4j Python Driver | GraphRAG 图存储与查询 |
| MCP Python SDK | 标准 MCP Server / Client |
| Server-Sent Events | 服务端单向流式输出 |
| pytest | 单元测试与接口测试 |
| GitHub Actions | 持续集成 |

---

## 5. 简化项目结构

```text
agent-api/
├── README.md
├── HANDOFF.md
├── constraints.txt
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── src/app/
│   ├── main.py                  # FastAPI 应用入口
│   ├── agent/                   # Agent Graph、工具、MCP Gateway
│   ├── llm/                     # Mock / Ollama Provider 抽象
│   ├── rag/                     # Chunk、检索、向量库、Agentic RAG
│   ├── graph/                   # GraphRAG、Neo4j、Fusion
│   ├── multi_agent/             # 多智能体角色与 Supervisor
│   ├── mcp_integration/         # MCP Server、Client、权限与安全
│   ├── evaluation/              # RAG 与后端评估
│   ├── observability/           # Trace Store 与事件
│   ├── routes/                  # FastAPI 路由
│   └── schemas/                 # Pydantic 数据模型
├── knowledge/                   # Git 管理的 Markdown 知识库
├── eval_cases/                  # RAG 评估数据集
├── docs/                        # GraphRAG、Multi-Agent、MCP 文档
├── scripts/                     # 语义模型和评估脚本
├── tests/                       # pytest 测试
└── data/                        # 运行时 SQLite / Chroma 数据，Git 忽略
```

---

## 6. 环境与启动

### 6.1 创建环境

```bash
conda create -n agentapi python=3.10 -y
conda activate agentapi
```

### 6.2 安装依赖

仅运行服务：

```bash
python -m pip install -r requirements.txt
```

本地开发、测试与验收：

```bash
python -m pip install -r requirements-dev.txt
```

`requirements.txt` 与 `requirements-dev.txt` 共同使用 `constraints.txt` 的已验证版本。不要直接用 `pip freeze > requirements.txt` 覆盖，否则会混入间接依赖或本地构建路径。

### 6.3 启动服务

```bash
python -m uvicorn src.app.main:app --reload --port 8000
```

### 6.4 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{"status":"ok"}
```

---

## 7. 关键配置

复制环境变量模板：

```bash
cp .env.example .env
```

`.env` 不进入 Git；`.env.example` 只保留无密钥的默认值和可选配置说明。

### 7.1 Ollama

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TEMPERATURE=0
```

当项目运行在 WSL，而 Ollama 运行在 Windows 主机时，需要将 `OLLAMA_BASE_URL` 改为 WSL 可访问的 Windows Host IP。

### 7.2 Neo4j

```env
NEO4J_ENABLED=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```

默认关闭 Neo4j，使 CI 和没有 Neo4j 的开发环境仍能运行 `dry_run` 路径。

### 7.3 Main Agent MCP Gateway

```env
AGENT_API_MAIN_AGENT_MCP_ENABLED=false
AGENT_API_MAIN_AGENT_MCP_FALLBACK_ENABLED=true
AGENT_API_MAIN_AGENT_MCP_MODE=local_wrapper
AGENT_API_MAIN_AGENT_MCP_SERVER_ID=agent-api-local
```

默认行为：

- MCP 不接管主 Agent。
- `search_knowledge_base` 继续使用原内部检索。
- 显式启用 MCP 后才调用 `agentic_rag_query`。
- MCP 失败时默认回退到内部检索。

### 7.4 默认检索策略

```text
DEFAULT_RETRIEVAL_BACKEND = hybrid
```

`graph_fusion` 必须显式指定，不应在无 Neo4j 环境中自动启用。

---

## 8. API 概览

### 8.1 基础与 Agent

| Method | Endpoint | 说明 |
|---|---|---|
| GET | `/health` | 健康检查 |
| POST | `/agent/chat` | 确定性 Agent 对话 |
| POST | `/agent/debug` | 查看节点路径、消息和工具调用 |
| POST | `/llm/chat` | Mock / Ollama Provider 测试 |
| POST | `/agent/llm-chat` | 真实 LLM Tool Calling Agent |
| POST | `/agent/llm-debug` | 检查真实 `tool_calls` |
| POST | `/agent/stream` | 确定性 Agent SSE |
| POST | `/agent/llm-stream` | 真实 LLM Agent SSE |

### 8.2 Router 与 Smart Chat

| Method | Endpoint | 说明 |
|---|---|---|
| POST | `/agent/router-chat` | 确定性路由 |
| POST | `/agent/router-debug` | 路由与节点路径调试 |
| POST | `/agent/router-stream` | Router SSE |
| POST | `/agent/llm-router-chat` | LLM Router |
| POST | `/agent/smart-chat` | 统一入口预览 |
| POST | `/agent/smart-stream` | Smart Chat SSE |

### 8.3 RAG

| Method | Endpoint | 说明 |
|---|---|---|
| POST | `/rag/search` | 轻量关键词检索 |
| POST | `/rag/search-debug` | 检索解释信息 |
| POST | `/rag/chunks-debug` | Chunk Pipeline 调试 |
| POST | `/rag/vector-search-debug` | 确定性向量检索 |
| POST | `/rag/hybrid-search-debug` | Hybrid Retrieval |
| POST | `/rag/agentic-debug` | Agentic RAG 图调试 |
| POST | `/rag/agentic-stream` | Agentic RAG SSE |
| POST | `/rag/answer-verify-debug` | 答案验证 |
| POST | `/rag/vector-store-debug` | SQLite Vector Store |
| POST | `/rag/embedding-debug` | Embedding Provider |
| POST | `/rag/chroma-search-debug` | Chroma 检索 |
| POST | `/rag/eval-debug` | 单后端评估 |
| POST | `/rag/backend-eval-debug` | 多后端对比 |

### 8.4 GraphRAG

| Method | Endpoint | 说明 |
|---|---|---|
| GET | `/graph/schema-debug` | 图 Schema 信息 |
| GET | `/graph/health-debug` | Neo4j 配置或连接检查 |
| POST | `/graph/extract-debug` | Entity / Relation 抽取 |
| POST | `/graph/ingest-debug` | Neo4j 写入计划或执行 |
| POST | `/graph/retrieval-debug` | 图检索 |
| POST | `/graph/fusion-debug` | 图检索与向量检索融合 |

### 8.5 Multi-Agent

| Method | Endpoint | 说明 |
|---|---|---|
| POST | `/multi-agent/state-debug` | 创建共享状态 |
| POST | `/multi-agent/plan-debug` | Planner |
| POST | `/multi-agent/research-debug` | Researcher |
| POST | `/multi-agent/tool-debug` | Tool Agent |
| POST | `/multi-agent/critic-debug` | Critic |
| POST | `/multi-agent/memory-debug` | Memory Agent |
| POST | `/multi-agent/reflection-debug` | Reflection Agent |
| POST | `/multi-agent/supervisor-debug` | Supervisor Graph |
| POST | `/multi-agent/stream` | Multi-Agent SSE |
| POST | `/multi-agent/eval-debug` | Eval / Trace 一致性检查 |

### 8.6 Observability

| Method | Endpoint | 说明 |
|---|---|---|
| GET | `/observability/traces` | 最近 Trace 列表 |
| GET | `/observability/traces/{trace_id}` | 单个 Trace 详情 |

---

## 9. 常用请求示例

### 9.1 确定性 Agent 计算

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: demo-trace-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"demo-thread-001"}'
```

示例响应：

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001",
  "trace_id": "demo-trace-001"
}
```

### 9.2 短期记忆

连续两次使用相同的 `thread_id`：

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 4 乘 9","thread_id":"memory-demo-001"}'

curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我刚才计算了什么？","thread_id":"memory-demo-001"}'
```

### 9.3 RAG 检索

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query":"RAG 是什么？","k":2}'
```

### 9.4 Agentic RAG

```bash
curl -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -d '{"query":"RAG 和 LangGraph 有什么关系？","retrieval_backend":"hybrid"}'
```

使用 GraphRAG 融合时显式指定：

```json
{
  "query": "RAG 和 LangGraph 有什么关系？",
  "retrieval_backend": "graph_fusion",
  "graph_dry_run": true
}
```

### 9.5 SSE Streaming

```bash
curl -N -X POST http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 3 加 5","thread_id":"stream-demo-001"}'
```

典型事件序列：

```text
event: metadata
event: answer_chunk
event: final
event: done
```

---

## 10. 测试与 CI

项目测试以确定性、可回归和 CI-safe 为基本原则。

### 10.1 完整回归

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -W error -m compileall -q src scripts tests
python -m pytest -q
```

最终 release acceptance：

```text
No broken requirements found.
warnings-as-errors compile passed
328 passed, 0 skipped, 0 warnings
```

Starlette TestClient 使用 `httpx2` 测试依赖；MCP 与 `pydantic-settings` 的无 warning 兼容边界已固定。真实 `sentence-transformers` 本地模型验证保留在 `scripts/validate_semantic_embedding_provider.py`，CI 使用可复现的 Provider 适配器契约测试，不下载模型或 PyTorch。

### 10.2 Golden Evaluation

固定评测集：

```text
eval_cases/agent_closure_golden.jsonl
```

共 40 条 case：

```text
Router              12
Tool                10
RAG                 10
End-to-end            4
Failure / recovery    4
```

运行：

```bash
python scripts/run_agent_closure_eval.py
```

正式指标：

```text
Router Accuracy                 16 / 16 = 100%
Tool Call Success Rate          12 / 12 = 100%
Tool Parameter Accuracy         12 / 12 = 100%
RAG source Recall@3             10 / 10 = 100%
Task Completion Rate            24 / 24 = 100%
Failure/Recovery Validation      4 / 4  = 100%
Failure Trace Coverage           4 / 4  = 100%
```

本地报告：

```text
reports/agent_closure/latest.json
reports/agent_closure/latest.md
```

`reports/` 为运行产物，不作为 release source 提交。

### 10.3 Trace Replay

trace-required case 会写入现有 observability trace store。

HTTP 回放接口：

```text
GET /observability/traces/{trace_id}
```

也可直接调用：

```python
get_trace_events(trace_id)
```

### 10.4 RAG Evaluation 边界

当前 closure benchmark 使用 **source-level Recall@3**。

仓库当前提交的本地知识库只有一个知识文档，因此该指标用于验证：

- 检索链路正确；
- gold source 能进入 top-k；
- Agent / RAG 工程连接稳定。

它不代表大型多文档语料库上的通用检索性能。

### 10.5 CI

GitHub Actions 使用 Python 3.10，并在 `master` push 和目标为 `master` 的 pull request 上执行：

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -W error -m compileall -q src scripts tests
python -m pytest -q
```

## 11. 运行时数据

运行时 SQLite 和向量数据位于：

```text
data/
```

以下模式被 Git 忽略：

```text
data/
*.sqlite
*.sqlite-shm
*.sqlite-wal
*.sqlite-journal
```

知识库位于：

```text
knowledge/
```

知识库属于项目源码，应使用 UTF-8 编码并纳入版本管理。

---

## 12. 重要工程边界

1. `DEFAULT_RETRIEVAL_BACKEND` 保持为 `hybrid`。
2. `graph_fusion` 只作为显式选择，不自动变成默认后端。
3. Main Agent 的 MCP 默认关闭。
4. MCP 失败时默认回退到内部知识库检索。
5. CI 不启动外部 MCP Server，不访问网络，不要求实时 Neo4j。
6. MCP Write / Destructive Tool 默认阻断。
7. 图写入和高风险图操作必须支持或强制 `dry_run`。
8. Multi-Agent 当前主要用于确定性工作流、状态建模、调试和评估，不等同于已经实现生产级并发自治智能体。
9. 不在 `chat-api` 中重复实现 GraphRAG、Multi-Agent 或 MCP 平台层。

---

## 13. 后续方向

本仓库已经完成当前阶段工程目标，默认进入冻结维护状态。

后续原则：

1. 不为了增加项目体量继续新增 Agent、Supervisor、Router 类型或 RAG backend；
2. 不通过修改 golden case 或降低 evaluator 要求来提升展示指标；
3. correctness / security bug 应使用独立维护分支修复，并补 regression test；
4. 外部依赖升级、CI 兼容性和安全维护属于正常维护范围；
5. 新的实验性 Agent、具身智能或机器人能力应进入独立项目，而不是继续堆叠到本仓库。

当前仓库主要用于：

- Agent / LangGraph / RAG / Multi-Agent / MCP 工程复习；
- 面试项目讲解；
- 架构、可观测性、评测和稳定性案例展示；
- 必要的缺陷与依赖维护。

## 14. 术语说明

| 术语 | 中文说明 |
|---|---|
| Agent | 能根据输入、状态和工具自主决定下一步操作的智能体 |
| Tool Calling | 模型生成结构化工具调用参数，再由程序执行工具 |
| LangGraph | 用图结构描述 Agent 节点、边、状态和执行流程的框架 |
| RAG | Retrieval-Augmented Generation，检索增强生成 |
| Agentic RAG | 由 Agent 控制是否检索、重写、评分和回答的 RAG 工作流 |
| GraphRAG | 使用知识图谱补充实体关系和结构化上下文的 RAG |
| VectorRAG | 通过 Embedding 和向量相似度进行检索的 RAG |
| Hybrid Retrieval | 融合关键词、向量或其他检索信号 |
| Reranker | 对初次召回结果进行二次排序的模型或规则 |
| Checkpointer | 保存 LangGraph 状态，使会话可以继续执行 |
| SSE | Server-Sent Events，服务端持续向客户端推送事件 |
| Trace | 一次请求在各节点和组件中的完整执行记录 |
| Multi-Agent | 多个具有不同职责的 Agent 共同完成任务 |
| Supervisor | 负责多 Agent 编排、顺序控制和结果汇总的角色 |
| MCP | Model Context Protocol，统一工具和资源发现、调用协议 |
| CI-safe | 不依赖外部服务、网络或高风险写操作，可稳定在 CI 中运行 |
| dry_run | 只生成执行计划，不真正写入或执行高风险操作 |
