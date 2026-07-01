# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

This project is the second project in the AI internship preparation roadmap, following the completed `chat-api-v2` project. The current version implements a deterministic Tool Calling Agent, SQLite-based short-term memory, graph debug output, request tracing, LLM provider abstraction, a real Ollama-backed LLM Tool Calling Agent path, SSE streaming endpoints, a lightweight local RAG search tool, a deterministic Router Agent that delegates calculator and RAG routes to the existing Agent graph, a Router Agent SSE streaming endpoint, and an initial LLM Router Agent endpoint with mock and Ollama router providers.

## Current Status

```text
Day1-Day16 completed.
Current stage: initial LLM Router Agent completed.
Local pytest: 31 passed, 1 warning.
GitHub Actions CI: green.
Next milestone: Day17 Router default entry point or richer RAG integration.
```

## Features

Current features:

* FastAPI backend service
* `/health` health check endpoint
* `/agent/chat` deterministic Agent chat endpoint
* `/agent/debug` deterministic graph execution debug endpoint
* `/llm/chat` LLM chat test endpoint
* `/agent/llm-chat` real LLM Tool Calling Agent endpoint
* `/agent/llm-debug` real LLM Tool Calling Agent debug endpoint
* `/agent/stream` deterministic Agent SSE streaming endpoint
* `/agent/llm-stream` real LLM Tool Calling Agent SSE streaming endpoint
* `/rag/search` lightweight local RAG search endpoint
* `/agent/router-chat` deterministic Router Agent chat endpoint
* `/agent/router-debug` deterministic Router Agent debug endpoint
* `/agent/router-stream` deterministic Router Agent SSE streaming endpoint
* `/agent/llm-router-chat` initial LLM Router Agent chat endpoint
* LangGraph `StateGraph`
* Deterministic Tool Calling Agent loop
* Real LLM Tool Calling Agent loop
* Built-in tools:
  * `add`
  * `multiply`
  * `search_knowledge_base`
* Lightweight keyword-based retriever
* Local Markdown knowledge base under `knowledge/`
* UTF-8 encoded knowledge base files for CI compatibility
* Deterministic Router Agent route classification
* Router branches: `calculator`, `rag`, and `chat`
* Router `calculator` and `rag` routes delegated to existing deterministic Agent graph
* Router delegation shares `thread_id` with Agent memory
* Router SSE stream events: `metadata`, `route`, `answer_chunk`, `final`, `done`
* LLM Router provider switch: `mock` for CI and `ollama` for local manual verification
* LLM Router response metadata: `route_reason`, `router_provider`, and `router_model`
* SQLite checkpoint-based short-term memory
* `thread_id` based conversation state
* Request logging middleware
* `x-trace-id` request tracing
* Automatic trace id generation when client does not provide one
* Trace id reuse when client provides `x-trace-id`
* `trace_id` included in Agent, LLM, RAG, and streaming responses
* Latency logging with `latency_ms`
* LLM provider abstraction
* Mock LLM provider for deterministic tests and CI
* Ollama LLM provider based on `langchain-ollama`
* Ollama tool binding via `bind_tools()`
* Server-Sent Events streaming response
* SSE event helper with `ensure_ascii=False` for readable Chinese output
* Environment-based LLM provider configuration
* Request-level provider override for `/llm/chat`
* Split pytest API tests
* GitHub Actions CI

Not implemented yet:

* OpenAI provider
* Replacing `/agent/chat` with the real LLM Agent as the default main route
* LLM Router as the default unified entry point
* Vector database based RAG
* Embedding-based retrieval
* Document upload and parsing pipeline
* GraphRAG
* Multi-Agent workflow

## Tech Stack

* Python 3.10
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings
* LangGraph
* LangChain Core
* LangChain Ollama
* LangGraph prebuilt `ToolNode`
* LangGraph prebuilt `tools_condition`
* SQLite checkpoint saver
* Local Markdown knowledge base
* Lightweight keyword retriever
* Deterministic Router Agent
* Initial LLM Router Agent
* pytest
* GitHub Actions
* Server-Sent Events

## Project Structure

```text
agent-api/
├── README.md
├── HANDOFF.md
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── DAY01.md
│   ├── DAY02.md
│   ├── DAY03.md
│   ├── DAY04.md
│   ├── DAY05.md
│   ├── DAY06.md
│   ├── DAY07.md
│   ├── DAY08.md
│   ├── DAY09.md
│   ├── DAY10.md
│   ├── DAY11.md
│   ├── DAY12.md
│   ├── DAY13.md
│   ├── DAY14.md
│   ├── DAY15.md
│   └── DAY16.md
├── knowledge/
│   └── agent_basics.md
├── data/
│   └── checkpoints.sqlite          # runtime only, ignored by Git
├── src/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── logging.py
│       │   ├── middleware.py
│       │   ├── request_context.py
│       │   └── sse.py
│       ├── schemas/
│       │   ├── agent.py
│       │   ├── llm.py
│       │   └── rag.py
│       ├── routes/
│       │   ├── routes_agent.py
│       │   ├── routes_llm.py
│       │   └── routes_rag.py
│       ├── rag/
│       │   ├── __init__.py
│       │   └── retriever.py
│       ├── llm/
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── mock.py
│       │   └── ollama.py
│       └── agent/
│           ├── graph.py
│           ├── router_graph.py
│           ├── router_streaming.py
│           ├── streaming.py
│           ├── llm_router.py
│           ├── llm_graph.py
│           ├── llm_nodes.py
│           ├── state.py
│           ├── nodes.py
│           ├── tools.py
│           └── memory.py
└── tests/
    ├── conftest.py
    ├── test_health.py
    ├── test_agent_chat.py
    ├── test_agent_memory.py
    ├── test_agent_debug.py
    ├── test_trace.py
    ├── test_llm.py
    ├── test_stream.py
    ├── test_rag.py
    ├── test_router_agent.py
    ├── test_router_delegation.py
    ├── test_router_stream.py
    └── test_llm_router.py
```

## Current Agent Graphs

### Deterministic Agent Graph

`/agent/chat`, `/agent/debug`, and `/agent/stream` use the deterministic graph.

```text
START
  ↓
agent
  ↓
tools_condition
  ├── END
  └── tools
        ↓
      agent
```

For a deterministic tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by rule-based node)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
```

The deterministic graph currently supports:

```text
add
multiply
search_knowledge_base
```

RAG-related questions such as `请搜索知识库：RAG 是什么？` are routed to the `search_knowledge_base` tool by deterministic keyword rules.

### Real LLM Tool Calling Agent Graph

`/agent/llm-chat`, `/agent/llm-debug`, and `/agent/llm-stream` use the real LLM Tool Calling Agent graph.

```text
START
  ↓
llm_agent_node
  ↓
tools_condition
  ├── END
  └── tools
        ↓
      llm_agent_node
```

For a real LLM tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by Ollama model)
  ↓
ToolMessage
  ↓
AIMessage(final answer generated by Ollama model)
```

## Current LLM Provider Architecture

Day9 added an independent LLM provider abstraction. Day10 uses the Ollama provider in the LLM Agent graph and binds the existing tools to the model.

```text
FastAPI
  ↓
/agent/llm-chat or /agent/llm-debug
  ↓
llm_agent_graph
  ↓
llm_agent_node
  ↓
get_chat_provider(provider="ollama")
  ↓
OllamaChatProvider.bind_tools(tools)
  ↓
ToolNode(tools)
```

Current providers:

```text
mock
ollama
```

Provider configuration:

```env
LLM_PROVIDER=mock
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TEMPERATURE=0
```

When WSL accesses Ollama running on the Windows host, `OLLAMA_BASE_URL` can be set to the Windows host IP exposed through WSL networking.

## Current Streaming Architecture

Day11 added SSE streaming endpoints while keeping deterministic and real LLM paths separate.

```text
/agent/stream
  ↓
stream_agent_events()
  ↓
invoke_agent()
  ↓
metadata -> answer_chunk -> final -> done
```

```text
/agent/llm-stream
  ↓
stream_llm_agent_events()
  ↓
llm_agent_graph.stream(..., stream_mode="updates")
  ↓
metadata -> step(agent) -> step(tools) -> step(agent) -> final -> done
```

SSE payloads are serialized with:

```text
ensure_ascii=False
```

This keeps Chinese output readable in terminal responses instead of showing Unicode escape sequences.

## Current RAG Architecture

Day12 added a lightweight deterministic RAG search path.

```text
knowledge/agent_basics.md
  ↓
search_knowledge()
  ↓
/rag/search
```

The same retriever is also exposed to the deterministic Agent as a tool:

```text
/agent/chat or /agent/debug
  ↓
agent_node
  ↓
AIMessage(tool_calls=[search_knowledge_base])
  ↓
ToolNode(tools)
  ↓
search_knowledge_base()
  ↓
search_knowledge()
  ↓
AIMessage(final answer)
```

Day12 intentionally uses a simple keyword retriever instead of embeddings or a vector database. This keeps pytest and GitHub Actions deterministic and avoids external services.

Important Day12 notes:

```text
Knowledge files are stored under knowledge/.
Knowledge files must be UTF-8 encoded.
Runtime files remain under data/ and are ignored by Git.
The initial vector DB / embedding pipeline is intentionally deferred.
```

## Current Router Agent Architecture

Day13 added a deterministic Router Agent while keeping the existing deterministic Agent and real LLM Agent paths separate.

```text
/agent/router-chat or /agent/router-debug
  ↓
router_agent_graph
  ↓
router
  ├── calculator
  ├── rag
  └── chat
```

The Router Agent classifies each user message into one route:

```text
calculator  # arithmetic requests such as 请计算 3 加 5
rag         # knowledge-base / RAG / LangGraph search requests
chat        # ordinary chat requests
```

Current Router Agent endpoints:

```text
POST /agent/router-chat
POST /agent/router-debug
```

`/agent/router-chat` returns the selected `route` and final answer.

`/agent/router-debug` exposes node-level routing steps such as:

```text
router -> rag
```

Day13 introduced deterministic rule-based routing. Day14 keeps that routing layer but delegates `calculator` and `rag` execution to the existing deterministic Agent graph through `invoke_agent()`. This reuses the existing tools, graph behavior, and SQLite short-term memory instead of duplicating logic inside the router.

## Current Router Delegation Architecture

Day14 connects the Router Agent to existing Agent capabilities.

```text
/agent/router-chat
  ↓
router_agent_graph
  ↓
router
  ├── calculator -> invoke_agent() -> add / multiply tool
  ├── rag        -> invoke_agent() -> search_knowledge_base tool
  └── chat       -> Router chat response
```

The important Day14 behavior is that delegated routes reuse the same `thread_id` when calling `invoke_agent()`.

This means a Router call can write to the existing Agent short-term memory, and a later `/agent/chat` request with the same `thread_id` can recall that interaction.

Example:

```text
/agent/router-chat: 请计算 4 乘 9
  ↓
calculator route
  ↓
invoke_agent(thread_id=same_thread_id)
  ↓
ToolMessage(name=multiply, content=36)
  ↓
/agent/chat: 我刚才计算了什么？
  ↓
我记得上一轮工具 `multiply` 的执行结果是：36
```

## Current Router Streaming Architecture

Day15 added a Router Agent SSE streaming endpoint.

```text
/agent/router-stream
  ↓
stream_router_agent_events()
  ↓
invoke_router_agent()
  ↓
metadata -> route -> answer_chunk -> final -> done
```

The Router stream supports all three deterministic Router routes:

```text
calculator
rag
chat
```

Current event sequence:

```text
event: metadata      # thread_id and trace_id
event: route         # selected route
event: answer_chunk  # current implementation emits the full answer as one chunk
event: final         # final answer payload
event: done          # stream completion marker
```

Day15 intentionally keeps `answer_chunk` as one complete chunk because the deterministic Router does not generate token-level output. This design keeps the SSE contract stable and prepares the endpoint for future token-level LLM streaming.

## Current LLM Router Architecture

Day16 added an initial LLM Router Agent endpoint while keeping the deterministic Router Agent unchanged.

```text
/agent/llm-router-chat
  ↓
invoke_llm_router_agent()
  ↓
classify_route_with_llm()
  ├── mock   -> CI-safe deterministic router decision
  └── ollama -> local manual LLM router decision
  ↓
calculator -> invoke_agent() -> add / multiply tool
rag        -> invoke_agent() -> search_knowledge_base tool
chat       -> Router chat response
```

The LLM Router returns route decision metadata:

```text
route
route_reason
router_provider
router_model
```

Current router providers:

```text
mock
ollama
```

Important Day16 behavior:

```text
router_provider="mock"   -> always uses mock-router and is covered by CI
router_provider="ollama" -> uses local Ollama and is manually verified
```

This keeps CI independent from a local Ollama service while still allowing local experiments with real LLM-based routing.

## Request Tracing

Every request has a trace id.

Rules:

```text
If the client provides x-trace-id:
  reuse the client-provided trace id.

If the client does not provide x-trace-id:
  generate trace-xxxxxxxxxxxx.
```

The trace id is returned in the response header:

```text
x-trace-id: trace-xxxxxxxxxxxx
```

For Agent, LLM, and RAG endpoints, the trace id is also returned in the response body:

```json
{
  "trace_id": "chat-trace-001"
}
```

Current request log includes:

```text
method
path
status_code
latency_ms
trace_id
```

Example log:

```text
request_completed method=POST path=/rag/search status_code=200 latency_ms=12.34 trace_id=day12-rag-search-001
```

## Quick Start

Create and activate the conda environment:

```bash
conda create -n agentapi python=3.10 -y
conda activate agentapi
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn src.app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Health check with manual trace id:

```bash
curl -i http://localhost:8000/health \
  -H "x-trace-id: manual-trace-001"
```

Expected response header:

```text
x-trace-id: manual-trace-001
```

## API Usage

### Agent Chat - Deterministic Route

```bash
curl -i -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: chat-trace-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"demo-thread-001"}'
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001",
  "trace_id": "chat-trace-001"
}
```

### Short-Term Memory

Use the same `thread_id` to continue the same conversation thread.

First request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 4 乘 9","thread_id":"memory-demo-001"}'
```

Second request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我刚才计算了什么？","thread_id":"memory-demo-001"}'
```

Expected response:

```json
{
  "answer": "我记得上一轮工具 `multiply` 的执行结果是：36",
  "thread_id": "memory-demo-001"
}
```

### Agent Debug Endpoint - Deterministic Route

```bash
curl -i -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: debug-trace-001" \
  -d '{"message":"请计算 8 乘 9","thread_id":"debug-demo-001"}'
```

Expected node path:

```text
agent -> tools -> agent
```

Expected response body includes:

```json
{
  "thread_id": "debug-demo-001",
  "final_answer": "工具 `multiply` 执行结果：72",
  "messages_count": 4,
  "trace_id": "debug-trace-001"
}
```

### LLM Chat - Mock Provider

```bash
curl -i -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: llm-mock-trace-001" \
  -d '{"message":"你好，这是 Day9 mock LLM 测试","provider":"mock"}'
```

Expected response:

```json
{
  "answer": "Mock LLM response: 你好，这是 Day9 mock LLM 测试",
  "provider": "mock",
  "model": "mock-echo",
  "trace_id": "llm-mock-trace-001"
}
```

### LLM Chat - Ollama Provider

```bash
curl -s -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: llm-ollama-trace-001" \
  -d '{"message":"请用一句话解释什么是 Agent。","provider":"ollama"}'
```

Example response:

```json
{
  "answer": "Agent是一种软件程序，它可以自动执行任务或在特定条件下采取行动，通常用于自动化管理和监控系统等场景。",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "llm-ollama-trace-001"
}
```

### Real LLM Tool Calling Agent

Addition:

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用工具。","thread_id":"day10-llm-add-001"}'
```

Example response:

```json
{
  "answer": "计算结果是 42。",
  "thread_id": "day10-llm-add-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-add-001"
}
```

Multiplication:

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-mul-001" \
  -d '{"message":"请计算 8 乘 9，必须使用工具。","thread_id":"day10-llm-mul-001"}'
```

Example response:

```json
{
  "answer": "计算结果是 72。",
  "thread_id": "day10-llm-mul-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-mul-001"
}
```

### Real LLM Tool Calling Debug

Use `/agent/llm-debug` to verify whether the LLM really generated tool calls.

```bash
curl -s -X POST http://localhost:8000/agent/llm-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-debug-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用 add 工具。","thread_id":"day10-debug-add-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
agent -> tools -> agent
```

Expected tool call:

```json
{
  "name": "add",
  "args": {
    "a": 13,
    "b": 29
  }
}
```

Multiplication debug:

```bash
curl -s -X POST http://localhost:8000/agent/llm-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-debug-mul-001" \
  -d '{"message":"请计算 8 乘 9，必须使用 multiply 工具。","thread_id":"day10-debug-mul-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected tool call:

```json
{
  "name": "multiply",
  "args": {
    "a": 8,
    "b": 9
  }
}
```

### Agent Stream - Deterministic Route

`/agent/stream` streams deterministic Agent output as Server-Sent Events.

```bash
curl -N -X POST http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-stream-add-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day11-stream-add-001"}'
```

Expected event sequence:

```text
event: metadata
event: answer_chunk
event: final
event: done
```

Example final event:

```text
event: final
data: {"answer": "工具 `add` 执行结果：8", "thread_id": "day11-stream-add-001", "trace_id": "day11-stream-add-001"}
```

### Agent Stream - Real LLM Tool Calling Route

`/agent/llm-stream` streams real LLM Tool Calling Agent graph updates as SSE events.

```bash
curl -N -X POST http://localhost:8000/agent/llm-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-llm-stream-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用 add 工具。","thread_id":"day11-llm-stream-add-001"}'
```

Expected event sequence:

```text
event: metadata
event: step      # node=agent, LLM-generated tool_calls
event: step      # node=tools, ToolMessage result
event: step      # node=agent, final AIMessage
event: final
event: done
```

Expected tool-call path:

```text
agent -> tools -> agent
```

Example final answer:

```text
计算结果是 42。
```

### RAG Search

`/rag/search` uses the lightweight local keyword retriever.

```bash
curl -s -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-rag-search-001" \
  -d '{"query":"RAG 是什么？","k":2}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```json
{
  "query": "RAG 是什么？",
  "results": [
    {
      "source": "knowledge/agent_basics.md",
      "content": "...RAG 是 Retrieval-Augmented Generation...",
      "score": 1
    }
  ],
  "trace_id": "day12-rag-search-001"
}
```

### Agent Chat with RAG Tool

`/agent/chat` can trigger the deterministic `search_knowledge_base` tool.

```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-agent-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day12-agent-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected answer starts with:

```text
根据知识库检索结果：
```

### Agent Debug with RAG Tool

`/agent/debug` can show the deterministic RAG tool-call path.

```bash
curl -s -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-debug-rag-001" \
  -d '{"message":"请搜索知识库：LangGraph 是什么？","thread_id":"day12-debug-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
agent -> tools -> agent
```

Expected tool call:

```json
{
  "name": "search_knowledge_base",
  "args": {
    "query": "请搜索知识库：LangGraph 是什么？",
    "k": 3
  }
}
```

### Router Agent Chat

`/agent/router-chat` selects one of three routes: `calculator`, `rag`, or `chat`.

Calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day13-router-calc-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "route": "calculator",
  "thread_id": "day13-router-calc-001",
  "trace_id": "day13-router-calc-001"
}
```

RAG route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day13-router-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```json
{
  "route": "rag",
  "answer": "根据知识库检索结果：..."
}
```

Chat route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day13-router-chat-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "Router chat response: 你好，介绍一下你自己",
  "route": "chat",
  "thread_id": "day13-router-chat-001",
  "trace_id": "day13-router-chat-001"
}
```

### Router Agent Debug

`/agent/router-debug` shows the selected route and node-level router execution path.

```bash
curl -s -X POST http://localhost:8000/agent/router-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-debug-rag-001" \
  -d '{"message":"请搜索知识库：LangGraph 是什么？","thread_id":"day13-router-debug-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
router -> rag
```

Expected response includes:

```json
{
  "route": "rag",
  "final_answer": "根据知识库检索结果：..."
}
```

### Router Delegation Memory Check

Day14 verifies that Router delegated routes use the existing Agent graph and memory.

First call the Router Agent calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day14-router-memory-001" \
  -d '{"message":"请计算 4 乘 9","thread_id":"day14-router-memory-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `multiply` 执行结果：36",
  "route": "calculator",
  "thread_id": "day14-router-memory-001",
  "trace_id": "day14-router-memory-001"
}
```

Then ask the existing deterministic Agent route with the same `thread_id`:

```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day14-router-memory-002" \
  -d '{"message":"我刚才计算了什么？","thread_id":"day14-router-memory-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "我记得上一轮工具 `multiply` 的执行结果是：36",
  "thread_id": "day14-router-memory-001",
  "trace_id": "day14-router-memory-002"
}
```

### Router Agent Stream

`/agent/router-stream` streams Router Agent output as Server-Sent Events.

Calculator route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day15-router-stream-calc-001"}'
```

Expected event sequence:

```text
event: metadata
event: route
event: answer_chunk
event: final
event: done
```

Expected route and answer:

```text
"route": "calculator"
"answer": "工具 `add` 执行结果：8"
```

RAG route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day15-router-stream-rag-001"}'
```

Expected route and answer content:

```text
"route": "rag"
"根据知识库检索结果"
"knowledge/agent_basics.md"
```

Chat route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day15-router-stream-chat-001"}'
```

Expected route and answer:

```text
"route": "chat"
"Router chat response: 你好，介绍一下你自己"
```

### LLM Router Agent Chat

`/agent/llm-router-chat` selects a route through a router provider and then executes the selected route.

The CI-safe provider is `mock`; the local manual provider is `ollama`.

Mock calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day16-llm-router-calc-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "route": "calculator",
  "route_reason": "Mock LLM router selected calculator because the message contains arithmetic intent.",
  "router_provider": "mock",
  "router_model": "mock-router",
  "thread_id": "day16-llm-router-calc-001",
  "trace_id": "day16-llm-router-calc-001"
}
```

Mock RAG route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day16-llm-router-rag-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "rag"
"router_provider": "mock"
"router_model": "mock-router"
"根据知识库检索结果"
```

Mock chat route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day16-llm-router-chat-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "chat"
"answer": "Router chat response: 你好，介绍一下你自己"
```

Ollama router can be manually verified locally:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-ollama-001" \
  -d '{"message":"请计算 9 乘 9","thread_id":"day16-llm-router-ollama-001","router_provider":"ollama"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected local response includes:

```text
"router_provider": "ollama"
"router_model": "qwen2.5:7b"
"route": "calculator"
"answer": "工具 `multiply` 执行结果：81"
```

## Tests

Run tests:

```bash
pytest -q
```

Current result:

```text
31 passed, 1 warning
```

Current test coverage includes:

* `/health`
* `/health` generated `x-trace-id`
* `/health` client-provided `x-trace-id`
* `/agent/chat` normal response
* `/agent/chat` trace id in header and body
* `add` tool
* `multiply` tool
* `search_knowledge_base` tool through `/agent/chat`
* same-thread short-term memory
* different-thread memory isolation
* `/agent/debug` normal path
* `/agent/debug` tool-call path
* `/agent/debug` RAG tool-call path
* `/agent/debug` trace id in header and body
* `/llm/chat` mock provider
* `/llm/chat` mock provider with trace id
* `/agent/stream` deterministic add tool SSE response
* `/agent/stream` deterministic multiply tool SSE response
* `/rag/search` lightweight local RAG endpoint
* `/agent/router-chat` calculator route
* `/agent/router-chat` RAG route
* `/agent/router-chat` chat route
* `/agent/router-debug` RAG route path
* Router calculator route delegates to existing Agent memory
* Router RAG route delegates to existing Agent memory
* `/agent/router-stream` calculator route SSE response
* `/agent/router-stream` RAG route SSE response
* `/agent/router-stream` chat route SSE response
* `/agent/llm-router-chat` mock calculator route
* `/agent/llm-router-chat` mock RAG route
* `/agent/llm-router-chat` mock chat route

Current test organization:

```text
tests/
├── conftest.py
├── test_health.py
├── test_agent_chat.py
├── test_agent_memory.py
├── test_agent_debug.py
├── test_trace.py
├── test_llm.py
├── test_stream.py
├── test_rag.py
├── test_router_agent.py
├── test_router_delegation.py
├── test_router_stream.py
└── test_llm_router.py
```

Ollama provider, real LLM tool calling, `/agent/llm-stream`, and `/agent/llm-router-chat` with `router_provider="ollama"` are manually tested locally and are not covered by CI, because CI should not depend on a local Ollama service. The deterministic `/agent/stream`, `/rag/search`, deterministic RAG tool path, Router Agent path, Router delegation memory path, Router stream path, and `/agent/llm-router-chat` mock path are covered by CI.

## CI

GitHub Actions CI is enabled.

Workflow:

```text
checkout
  ↓
setup-python 3.10
  ↓
pip install -r requirements.txt
  ↓
pytest -q
```

Current CI status:

```text
green
```

## Runtime Data

SQLite checkpoint files are generated under:

```text
data/
```

These files are runtime data and are ignored by Git.

Ignored runtime patterns include:

```text
data/
*.sqlite
*.sqlite-shm
*.sqlite-wal
*.sqlite-journal
```

Knowledge base files are stored separately under:

```text
knowledge/
```

These files are source-controlled project files, not runtime data.

## Development Notes

`requirements.txt` is manually maintained as a minimal dependency file. Do not blindly overwrite it with `pip freeze > requirements.txt` from a conda environment, because conda build artifact paths may break GitHub Actions CI.

Current local pytest warning:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

This warning does not block local tests or CI and can be handled later.

When formatting JSON output that contains Chinese text, prefer:

```bash
python -m json.tool --no-ensure-ascii
```

or:

```bash
python -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

Without this, `python -m json.tool` may display Chinese as Unicode escape sequences such as `\u8ba1\u7b97\u7ed3\u679c\u662f 42\u3002`.

For knowledge base files, use UTF-8 encoding. If a Markdown file was created or edited through Windows tools and pytest raises a `UnicodeDecodeError`, convert it:

```bash
iconv -f gbk -t utf-8 knowledge/agent_basics.md -o /tmp/agent_basics.md
mv /tmp/agent_basics.md knowledge/agent_basics.md
```

## Roadmap

Next milestones:

* Day17: Prepare Router Agent as default entry point or add richer RAG integration
* Day18+: Add vector database based RAG preparation
* Later: Add vector database based RAG
* Later: Add GraphRAG and Neo4j integration
* Later: Add Multi-Agent Supervisor workflow
