# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

The current version implements a deterministic Tool Calling Agent with SQLite-based short-term memory and debug output. It is designed as the second project in the AI internship preparation roadmap, following the previous `chat-api-v2` project.

## Features

Current features:

* FastAPI backend service
* `/health` health check endpoint
* `/agent/chat` chat endpoint
* LangGraph `StateGraph`
* Tool Calling Agent loop
* Built-in mock tools:

  * `add`
  * `multiply`
* SQLite checkpoint-based short-term memory
* `thread_id` based conversation state
* `/agent/debug` endpoint for inspecting graph execution steps
* pytest API tests
* GitHub Actions CI

Not implemented yet:

* Real LLM integration
* Ollama provider
* OpenAI provider
* Real LLM tool calling
* Streaming response
* RAG tool
* Router Agent
* GraphRAG
* Multi-Agent workflow

## Tech Stack

* Python 3.10
* FastAPI
* Uvicorn
* LangGraph
* LangChain Core
* SQLite checkpoint saver
* pytest
* GitHub Actions

## Project Structure

```text
agent-api/
├── README.md
├── HANDOFF.md
├── requirements.txt
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── app/
│       ├── main.py
│       ├── schemas/
│       │   └── agent.py
│       ├── routes/
│       │   └── routes_agent.py
│       └── agent/
│           ├── graph.py
│           ├── state.py
│           ├── nodes.py
│           ├── tools.py
│           └── memory.py
└── tests/
    └── test_agent_api.py
```

## Current Graph

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

For a tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
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

## API Usage

### Chat

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 3 加 5","thread_id":"demo-thread-001"}'
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001"
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

## Debug Endpoint

The debug endpoint shows the graph execution steps.

```bash
curl -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 8 乘 9","thread_id":"debug-demo-001"}'
```

Expected node path:

```text
agent -> tools -> agent
```

The response includes:

* `thread_id`
* `steps`
* `final_answer`
* `messages_count`

## Tests

Run tests:

```bash
pytest -q
```

Current test coverage includes:

* `/health`
* normal chat
* add tool
* multiply tool
* same-thread short-term memory
* different-thread memory isolation
* normal debug steps
* tool-call debug steps

## Runtime Data

SQLite checkpoint files are generated under:

```text
data/
```

These files are runtime data and are ignored by Git.

## Roadmap

Next milestones:

* Add request logging middleware with `x-trace-id`
* Add latency logging
* Connect trace id with Agent debug output
* Add Ollama LLM provider
* Replace deterministic tool-call mock with real LLM tool calling
* Add `/agent/stream`
* Add RAG search tool
* Add Router Agent
* Add GraphRAG and Neo4j integration
* Add Multi-Agent Supervisor workflow
