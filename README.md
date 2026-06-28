# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

This project is the second project in the AI internship preparation roadmap, following the completed `chat-api-v2` project. The current version implements a deterministic Tool Calling Agent with SQLite-based short-term memory, graph debug output, request tracing, LLM provider abstraction, pytest coverage, and GitHub Actions CI.

## Current Status

```text
Day1-Day9 completed.
Current stage: LLM provider abstraction completed before real LLM tool calling.
Local pytest: 14 passed, 1 warning.
GitHub Actions CI: green.
Next milestone: Day10 real LLM tool calling.
```

## Features

Current features:

* FastAPI backend service
* `/health` health check endpoint
* `/agent/chat` chat endpoint
* `/agent/debug` graph execution debug endpoint
* `/llm/chat` LLM chat test endpoint
* LangGraph `StateGraph`
* Deterministic Tool Calling Agent loop
* Built-in deterministic tools:
  * `add`
  * `multiply`
* SQLite checkpoint-based short-term memory
* `thread_id` based conversation state
* Request logging middleware
* `x-trace-id` request tracing
* Automatic trace id generation when client does not provide one
* Trace id reuse when client provides `x-trace-id`
* `trace_id` included in Agent and LLM response bodies
* Latency logging with `latency_ms`
* LLM provider abstraction
* Mock LLM provider for deterministic tests and CI
* Ollama LLM provider based on `langchain-ollama`
* Environment-based LLM provider configuration
* Request-level provider override for `/llm/chat`
* Split pytest API tests
* GitHub Actions CI

Not implemented yet:

* OpenAI provider
* Real LLM tool calling inside `/agent/chat`
* Streaming response
* RAG tool
* Router Agent
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
* pytest
* GitHub Actions

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
│   └── DAY09.md
├── data/
│   └── checkpoints.sqlite          # runtime only, ignored by Git
├── src/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── logging.py
│       │   ├── middleware.py
│       │   └── request_context.py
│       ├── schemas/
│       │   ├── agent.py
│       │   └── llm.py
│       ├── routes/
│       │   ├── routes_agent.py
│       │   └── routes_llm.py
│       ├── llm/
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── mock.py
│       │   └── ollama.py
│       └── agent/
│           ├── graph.py
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
    └── test_llm.py
```

## Current Agent Graph

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
AIMessage(tool_calls)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
```

## Current LLM Provider Architecture

Day9 adds an independent LLM provider abstraction. The current `/agent/chat` endpoint still uses deterministic tool-call logic. Real LLM tool calling will be introduced later.

```text
FastAPI
  ↓
/llm/chat
  ↓
get_chat_provider()
  ↓
MockChatProvider / OllamaChatProvider
  ↓
AIMessage
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

For Agent and LLM endpoints, the trace id is also returned in the response body:

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
request_completed method=POST path=/agent/chat status_code=200 latency_ms=12.34 trace_id=chat-trace-001
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

### Agent Chat

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

### Agent Debug Endpoint

The debug endpoint shows graph execution steps.

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

The full debug response includes:

* `thread_id`
* `steps`
* `final_answer`
* `messages_count`
* `trace_id`

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

## Tests

Run tests:

```bash
pytest -q
```

Current result:

```text
14 passed, 1 warning
```

Current test coverage includes:

* `/health`
* `/health` generated `x-trace-id`
* `/health` client-provided `x-trace-id`
* `/agent/chat` normal response
* `/agent/chat` trace id in header and body
* `add` tool
* `multiply` tool
* same-thread short-term memory
* different-thread memory isolation
* `/agent/debug` normal path
* `/agent/debug` tool-call path
* `/agent/debug` trace id in header and body
* `/llm/chat` mock provider
* `/llm/chat` mock provider with trace id

Current test organization:

```text
tests/
├── conftest.py
├── test_health.py
├── test_agent_chat.py
├── test_agent_memory.py
├── test_agent_debug.py
├── test_trace.py
└── test_llm.py
```

Ollama provider is manually tested locally and is not covered by CI, because CI should not depend on a local Ollama service.

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

## Development Notes

`requirements.txt` is manually maintained as a minimal dependency file. Do not blindly overwrite it with `pip freeze > requirements.txt` from a conda environment, because conda build artifact paths may break GitHub Actions CI.

Current local pytest warning:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

This warning does not block local tests or CI and can be handled later.

## Roadmap

Next milestones:

* Day10: Replace deterministic tool-call mock with real LLM tool calling
* Day11: Add `/agent/stream`
* Day12: Add RAG search tool
* Day13+: Add Router Agent
* Later: Add GraphRAG and Neo4j integration
* Later: Add Multi-Agent Supervisor workflow
